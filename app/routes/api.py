"""
API REST pour intégrations externes
ENSA Béni Mellal - Système IA Responsable
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db, limiter
from app.models import Request, User, AuditLog
from app.utils.ai_engine import AIEngine
from app.utils.validators import validate_ai_request
from app.utils.security import get_client_ip
from datetime import datetime

api_bp = Blueprint('api', __name__)

# Initialiser le moteur IA
ai_engine = AIEngine()


# ==================== GESTION DES ERREURS API ====================

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400


@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@api_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'message': 'Access denied'
    }), 403


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'Resource not found'
    }), 404


@api_bp.errorhandler(429)
def ratelimit_error(error):
    return jsonify({
        'error': 'Too Many Requests',
        'message': 'Rate limit exceeded'
    }), 429


# ==================== ENDPOINTS API ====================

@api_bp.route('/health', methods=['GET'])
def health():
    """Vérifier l'état du système"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@api_bp.route('/ask', methods=['POST'])
@login_required
@limiter.limit("30 per hour")
def ask():
    """
    Soumettre une question à l'IA
    
    Body JSON:
    {
        "content": "Ma question...",
        "request_type": "question|resume|generation|analysis"
    }
    """
    
    # Récupérer les données JSON
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'No JSON data provided'
        }), 400
    
    content = data.get('content', '').strip()
    request_type = data.get('request_type', 'question')
    
    # Validation
    is_valid, error_msg = validate_ai_request(content, request_type)
    if not is_valid:
        return jsonify({
            'error': 'Validation failed',
            'message': error_msg
        }), 400
    
    # Traiter avec le moteur IA
    ai_result = ai_engine.process_request(
        content=content,
        request_type=request_type,
        user_id=current_user.id
    )
    
    if not ai_result['success']:
        return jsonify({
            'error': 'Processing failed',
            'message': ai_result.get('error'),
            'issues': ai_result.get('issues', [])
        }), 400
    
    # Créer l'enregistrement en base
    new_req = Request(
        user_id=current_user.id,
        request_type=request_type,
        content=content,
        response=ai_result['response'],
        processing_time_ms=ai_result.get('processing_time_ms'),
        status='completed',
        ip_address=get_client_ip(),
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.add(new_req)
    db.session.commit()
    
    # Log
    AuditLog.log_action(
        user_id=current_user.id,
        action='API_REQUEST',
        details=f"Type: {request_type}, ID: {new_req.id}",
        severity='info',
        resource_type='request',
        resource_id=new_req.id
    )
    
    # Retourner la réponse
    return jsonify({
        'success': True,
        'request_id': new_req.id,
        'response': ai_result['response'],
        'from_cache': ai_result.get('from_cache', False),
        'processing_time_ms': ai_result.get('processing_time_ms'),
        'requires_validation': ai_result.get('requires_validation', False),
        'created_at': new_req.created_at.isoformat()
    })


@api_bp.route('/request/<int:request_id>', methods=['GET'])
@login_required
def get_request(request_id):
    """Récupérer une demande spécifique"""
    
    req = Request.query.get_or_404(request_id)
    
    # Vérifier les permissions
    if req.user_id != current_user.id and not current_user.is_admin():
        return jsonify({
            'error': 'Access denied'
        }), 403
    
    return jsonify(req.to_dict())


@api_bp.route('/requests', methods=['GET'])
@login_required
def get_requests():
    """Liste des demandes de l'utilisateur"""
    
    # Paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if per_page > 100:
        per_page = 100
    
    # Filtres
    request_type = request.args.get('type')
    status = request.args.get('status')
    
    # Query de base
    query = Request.query.filter_by(user_id=current_user.id)
    
    if request_type:
        query = query.filter_by(request_type=request_type)
    
    if status:
        query = query.filter_by(status=status)
    
    # Pagination
    pagination = query.order_by(Request.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'requests': [req.to_dict() for req in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page
    })


@api_bp.route('/request/<int:request_id>/feedback', methods=['POST'])
@login_required
@limiter.limit("50 per hour")
def submit_request_feedback(request_id):
    """
    Soumettre un feedback
    
    Body JSON:
    {
        "rating": 1-5,
        "feedback": "Commentaire...",
        "is_helpful": true/false
    }
    """
    
    req = Request.query.get_or_404(request_id)
    
    # Vérifier les permissions
    if req.user_id != current_user.id:
        return jsonify({
            'error': 'Access denied'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'No JSON data provided'
        }), 400
    
    # Mettre à jour le feedback
    if 'rating' in data:
        rating = data['rating']
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            return jsonify({
                'error': 'Rating must be between 1 and 5'
            }), 400
        req.user_rating = rating
    
    if 'feedback' in data:
        req.user_feedback = data['feedback']
    
    if 'is_helpful' in data:
        req.is_helpful = bool(data['is_helpful'])
    
    db.session.commit()
    
    # Log
    AuditLog.log_action(
        user_id=current_user.id,
        action='API_FEEDBACK',
        details=f"Feedback pour demande {request_id}",
        severity='info',
        resource_type='request',
        resource_id=request_id
    )
    
    return jsonify({
        'success': True,
        'message': 'Feedback submitted successfully'
    })


@api_bp.route('/stats', methods=['GET'])
@login_required
def user_stats():
    """Statistiques de l'utilisateur"""
    
    total_requests = Request.query.filter_by(user_id=current_user.id).count()
    
    # Par type
    from sqlalchemy import func
    by_type = db.session.query(
        Request.request_type,
        func.count(Request.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by(Request.request_type)\
     .all()
    
    # Rating moyen
    avg_rating = db.session.query(
        func.avg(Request.user_rating)
    ).filter_by(user_id=current_user.id).scalar()
    
    # Temps de traitement moyen
    avg_time = db.session.query(
        func.avg(Request.processing_time_ms)
    ).filter_by(user_id=current_user.id).scalar()
    
    return jsonify({
        'total_requests': total_requests,
        'requests_by_type': {item[0]: item[1] for item in by_type},
        'average_rating': round(avg_rating, 2) if avg_rating else None,
        'average_processing_time_ms': round(avg_time, 2) if avg_time else None,
        'member_since': current_user.created_at.isoformat()
    })


@api_bp.route('/model-info', methods=['GET'])
def model_info():
    """Informations sur le modèle IA"""
    return jsonify(ai_engine.get_model_info())