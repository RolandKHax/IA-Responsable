"""
Routes principales de l'application
ENSA Béni Mellal - Système IA Responsable
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response, stream_with_context, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from app.models import Request, AuditLog, User, Conversation
from app.utils.ai_engine import AIEngine, StressAnalyzer
from app.utils.security import get_client_ip
from app.utils.validators import validate_ai_request, validate_rating, validate_feedback_text
from datetime import datetime

main_bp = Blueprint('main', __name__)

# Initialiser le moteur IA
ai_engine = AIEngine()
stress_analyzer = StressAnalyzer()


@main_bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord utilisateur"""
    
    # Récupérer les dernières demandes
    recent_requests = Request.query.filter_by(user_id=current_user.id)\
        .order_by(Request.created_at.desc())\
        .limit(10)\
        .all()
    
    # Statistiques utilisateur
    total_requests = Request.query.filter_by(user_id=current_user.id).count()
    validated_requests = Request.query.filter_by(
        user_id=current_user.id,
        validated_by_human=True
    ).count()
    
    # Mettre à jour la dernière activité
    current_user.last_activity = datetime.utcnow()
    db.session.commit()
    
    return render_template('user/dashboard.html',
                         recent_requests=recent_requests,
                         total_requests=total_requests,
                         validated_requests=validated_requests)


@main_bp.route('/new-request', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour")
def new_request():
    """Créer une nouvelle demande IA"""
    
    if request.method == 'POST':
        request_type = request.form.get('request_type')
        content = request.form.get('content', '').strip()
        title = request.form.get('title', '').strip()
        
        # Validation
        is_valid, error_msg = validate_ai_request(content, request_type)
        if not is_valid:
            flash(error_msg, 'danger')
            return redirect(url_for('main.new_request'))
        
        # Analyse du stress (si c'est une question)
        stress_data = None
        if request_type == 'question':
            stress_data = stress_analyzer.analyze(content)
            
            # Alerter si niveau de stress critique
            if stress_data['level'] == 'critique':
                flash(f"⚠️ Niveau de stress détecté : {stress_data['level']}. "
                     f"{stress_data['recommendation']}", 'warning')
        
        # Traiter la demande avec le moteur IA
        ai_result = ai_engine.process_request(
            content=content,
            request_type=request_type,
            user_id=current_user.id
        )
        
        if not ai_result['success']:
            flash(f"Erreur : {ai_result.get('error', 'Erreur inconnue')}", 'danger')
            
            # Afficher les détails si disponibles
            for issue in ai_result.get('issues', []):
                flash(f"⚠️ {issue}", 'warning')
            
            return redirect(url_for('main.new_request'))
        
        # Créer la demande en base de données
        new_req = Request(
            user_id=current_user.id,
            request_type=request_type,
            title=title or f"{request_type.capitalize()} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            content=content,
            response=ai_result['response'],
            model_used=ai_result.get('metadata', {}).get('model', 'AI-Engine-v1.0'),
            processing_time_ms=ai_result.get('processing_time_ms'),
            validated_by_human=False,
            status='completed',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent')
        )
        
        # Ajouter les données de stress si présentes
        if stress_data:
            new_req.confidence_score = 1 - stress_data['score']  # Score inversé
        
        db.session.add(new_req)
        db.session.commit()
        
        # Log de l'action
        AuditLog.log_action(
            user_id=current_user.id,
            action='DEMANDE_IA_CREEE',
            details=f"Type: {request_type}, ID: {new_req.id}, Cache: {ai_result.get('from_cache', False)}",
            severity='info',
            resource_type='request',
            resource_id=new_req.id
        )
        
        # Message de succès
        if ai_result.get('from_cache'):
            flash('✓ Réponse récupérée du cache (réponse validée précédemment).', 'info')
        elif ai_result.get('requires_validation'):
            flash('✓ Réponse générée. Elle sera validée par un humain prochainement.', 'info')
        else:
            flash('✓ Réponse générée avec succès.', 'success')
        
        return redirect(url_for('main.view_request', request_id=new_req.id))
    
    return render_template('user/new_request.html')


@main_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    """Voir une demande spécifique"""
    
    req = Request.query.get_or_404(request_id)
    
    # Vérifier les permissions
    if req.user_id != current_user.id and not current_user.is_admin():
        flash('Accès non autorisé à cette demande.', 'danger')
        abort(403)
    
    return render_template('user/view_request.html', req=req)


@main_bp.route('/request/<int:request_id>/feedback', methods=['POST'])
@login_required
@limiter.limit("30 per hour")
def submit_feedback(request_id):
    """Soumettre un feedback sur une réponse"""
    
    req = Request.query.get_or_404(request_id)
    
    # Vérifier les permissions
    if req.user_id != current_user.id:
        abort(403)
    
    rating = request.form.get('rating')
    feedback = request.form.get('feedback', '').strip()
    is_helpful = request.form.get('is_helpful') == 'yes'
    
    # Validation
    if rating and not validate_rating(rating):
        flash('Note invalide. Utilisez une valeur entre 1 et 5.', 'danger')
        return redirect(url_for('main.view_request', request_id=request_id))
    
    if feedback and not validate_feedback_text(feedback):
        flash('Commentaire invalide.', 'danger')
        return redirect(url_for('main.view_request', request_id=request_id))
    
    # Mettre à jour la demande
    if rating:
        req.user_rating = int(rating)
    if feedback:
        req.user_feedback = feedback
    req.is_helpful = is_helpful
    
    db.session.commit()
    
    # Log de l'action
    AuditLog.log_action(
        user_id=current_user.id,
        action='FEEDBACK_SOUMIS',
        details=f"Demande {request_id}, Note: {rating}, Utile: {is_helpful}",
        severity='info',
        resource_type='request',
        resource_id=request_id
    )
    
    flash('Merci pour votre feedback !', 'success')
    return redirect(url_for('main.view_request', request_id=request_id))


@main_bp.route('/my-data')
@login_required
def my_data():
    """Exercice du droit d'accès RGPD"""
    
    # Récupérer toutes les données de l'utilisateur
    all_requests = Request.query.filter_by(user_id=current_user.id)\
        .order_by(Request.created_at.desc())\
        .all()
    
    audit_logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.timestamp.desc())\
        .limit(50)\
        .all()
    
    # Log de l'accès aux données
    AuditLog.log_action(
        user_id=current_user.id,
        action='DROIT_ACCES',
        details='Consultation des données personnelles',
        severity='info'
    )
    
    return render_template('user/my_data.html',
                         user=current_user,
                         requests=all_requests,
                         logs=audit_logs)


@main_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Exercice du droit à l'effacement RGPD"""
    
    # Demander confirmation
    confirmation = request.form.get('confirmation', '').strip().lower()
    
    if confirmation != 'supprimer':
        flash('Veuillez taper "supprimer" pour confirmer la suppression de votre compte.', 'warning')
        return redirect(url_for('main.my_data'))
    
    user_id = current_user.id
    username = current_user.username
    
    # Log avant suppression
    AuditLog.log_action(
        user_id=user_id,
        action='DROIT_EFFACEMENT',
        details=f'Demande de suppression de compte : {username}',
        severity='warning'
    )
    
    # Supprimer toutes les demandes
    Request.query.filter_by(user_id=user_id).delete()
    
    # Anonymiser les logs d'audit (garder pour conformité)
    AuditLog.query.filter_by(user_id=user_id).update({
        'details': '[Données utilisateur supprimées - RGPD]'
    })
    
    # Supprimer l'utilisateur
    from flask_login import logout_user
    logout_user()
    
    db.session.delete(current_user)
    db.session.commit()
    
    flash('Votre compte et toutes vos données personnelles ont été supprimés conformément au RGPD.', 'success')
    return redirect(url_for('main.index'))


@main_bp.route('/chat')
@login_required
def chat():
    """Interface de chat conversationnel"""
    return render_template('user/chat.html')


@main_bp.route('/chat/stream', methods=['POST'])
@login_required
def stream_chat():
    """Stream a multi-turn chat response via SSE."""
    messages_json = request.form.get('messages', '[]')
    request_type = request.form.get('request_type', None)
    try:
        messages = json.loads(messages_json)
        if not isinstance(messages, list):
            messages = []
    except Exception:
        messages = []

    username = current_user.username

    def generate():
        yield from ai_engine.stream_chat_api(messages, username=username, request_type=request_type)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@main_bp.route('/conversations')
@login_required
def list_conversations():
    convs = Conversation.query.filter_by(user_id=current_user.id)\
        .order_by(Conversation.updated_at.desc()).limit(50).all()
    return jsonify({'conversations': [
        {'id': c.id, 'title': c.title,
         'updated_at': c.updated_at.strftime('%d/%m/%Y') if c.updated_at else ''}
        for c in convs
    ]})


@main_bp.route('/conversations/save', methods=['POST'])
@login_required
def save_conversation():
    data = request.get_json()
    conv_id = data.get('id')
    messages = data.get('messages', [])
    title = data.get('title', 'Nouvelle conversation')

    if conv_id:
        conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first()
        if not conv:
            return jsonify({'error': 'Not found'}), 404
    else:
        conv = Conversation(user_id=current_user.id)
        db.session.add(conv)

    conv.title = title[:100]
    conv.messages = messages
    conv.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'id': conv.id, 'title': conv.title})


@main_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@login_required
def get_conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    return jsonify({'id': conv.id, 'title': conv.title, 'messages': conv.messages})


@main_bp.route('/conversations/<int:conv_id>/delete', methods=['POST'])
@login_required
def delete_conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'ok': True})


@main_bp.route('/privacy-policy')
def privacy_policy():
    """Politique de confidentialité"""
    return render_template('legal/privacy_policy.html')


@main_bp.route('/terms')
def terms():
    """Conditions d'utilisation"""
    return render_template('legal/terms.html')


@main_bp.route('/about')
def about():
    """À propos du système"""
    
    # Informations sur le modèle IA
    model_info = ai_engine.get_model_info()
    
    return render_template('about.html', model_info=model_info)