"""
Moteur IA avec gouvernance éthique
ENSA Béni Mellal - Système IA Responsable
"""

import hashlib
import json
import os
import time
import requests as http_requests
from datetime import datetime, timedelta
from app.utils.security import detect_sensitive_data, anonymize_text


class AIEngine:
    """Moteur IA avec contrôles éthiques et RGPD"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.max_tokens = self.config.get('AI_MAX_TOKENS', 1000)
        self.temperature = self.config.get('AI_TEMPERATURE', 0.7)
        self.enable_validation = self.config.get('ENABLE_HUMAN_VALIDATION', True)
    
    def process_request(self, content, request_type, user_id=None):
        """
        Traite une demande IA avec tous les contrôles
        Retourne un dictionnaire avec le résultat
        """
        start_time = time.time()
        
        # Étape 1: Validation du contenu
        validation_result = self._validate_content(content)
        if not validation_result['is_valid']:
            return {
                'success': False,
                'error': validation_result['error'],
                'issues': validation_result.get('issues', [])
            }
        
        # Étape 2: Détection de données sensibles
        has_sensitive, sensitive_types, sensitive_details = detect_sensitive_data(content)
        if has_sensitive:
            return {
                'success': False,
                'error': 'Votre demande contient des données sensibles qui ne peuvent pas être traitées.',
                'sensitive_types': sensitive_types,
                'details': sensitive_details
            }
        
        # Étape 3: Vérifier le cache
        cache_key = self._generate_cache_key(content, request_type)
        cached_response = self._check_cache(cache_key)
        if cached_response:
            processing_time = int((time.time() - start_time) * 1000)
            return {
                'success': True,
                'response': cached_response['response'],
                'from_cache': True,
                'processing_time_ms': processing_time,
                'requires_validation': False
            }
        
        # Étape 4: Générer la réponse
        try:
            response = self._generate_response(content, request_type)
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la génération: {str(e)}'
            }
        
        # Étape 5: Validation post-génération
        post_validation = self._post_validation_checks(response)
        if not post_validation['is_valid']:
            return {
                'success': False,
                'error': 'La réponse générée ne respecte pas les critères de qualité',
                'issues': post_validation.get('issues', [])
            }
        
        # Étape 6: Calculer les métriques
        processing_time = int((time.time() - start_time) * 1000)
        
        # Étape 7: Mettre en cache
        self._save_to_cache(cache_key, response, request_type)
        
        # Retourner le résultat
        return {
            'success': True,
            'response': response,
            'from_cache': False,
            'processing_time_ms': processing_time,
            'requires_validation': self.enable_validation,
            'metadata': {
                'request_type': request_type,
                'timestamp': datetime.utcnow().isoformat(),
                'model': 'AI-Engine-v1.0'
            }
        }
    
    def _validate_content(self, content):
        """Valide le contenu avant traitement"""
        issues = []
        
        # Vérifier la longueur
        if not content or len(content.strip()) < 10:
            return {
                'is_valid': False,
                'error': 'Le contenu doit contenir au moins 10 caractères'
            }
        
        if len(content) > 10000:
            return {
                'is_valid': False,
                'error': 'Le contenu ne doit pas dépasser 10000 caractères'
            }
        
        # Vérifier qu'il n'y a pas d'injection de code
        dangerous_patterns = [
            '<script', 'javascript:', 'onerror=', 'onclick=',
            'eval(', 'exec(', '__import__'
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                issues.append(f'Pattern dangereux détecté: {pattern}')
        
        if issues:
            return {
                'is_valid': False,
                'error': 'Contenu potentiellement dangereux détecté',
                'issues': issues
            }
        
        return {'is_valid': True}
    
    def _generate_response(self, content, request_type):
        """
        Génère une réponse IA
        Cette version utilise des règles simples
        En production: intégrer un vrai modèle LLM (OpenAI, Claude, etc.)
        """
        
        if request_type == 'question':
            return self._handle_question(content)
        elif request_type == 'resume':
            return self._handle_resume(content)
        elif request_type == 'generation':
            return self._handle_generation(content)
        elif request_type == 'analysis':
            return self._handle_analysis(content)
        else:
            return "Type de demande non supporté."
    
    def _handle_question(self, question):
        """Gère les questions"""
        
        # Analyse basique de la question
        question_lower = question.lower()
        
        # Réponses contextuelles basiques
        if any(word in question_lower for word in ['comment', 'pourquoi', 'qu\'est-ce']):
            response_type = "explication"
        elif any(word in question_lower for word in ['quand', 'où', 'qui']):
            response_type = "information factuelle"
        else:
            response_type = "réponse générale"
        
        response = f"""Réponse générée par le système IA :

Question posée : "{question[:150]}{'...' if len(question) > 150 else ''}"

Type de réponse : {response_type}

Cette réponse est générée automatiquement. Pour des informations critiques, 
veuillez consulter un expert humain ou vérifier avec des sources officielles.

⚠️ AVERTISSEMENTS IMPORTANTS :
• Les réponses IA peuvent contenir des erreurs factuelles
• Aucune garantie d'exactitude à 100%
• Toujours vérifier les informations importantes
• Ne pas utiliser pour des décisions médicales, juridiques ou financières

📋 TRAÇABILITÉ RGPD :
Cette interaction est enregistrée conformément à notre politique de confidentialité.
Vous pouvez exercer vos droits d'accès et de suppression à tout moment.

💡 RECOMMANDATIONS :
• Vérifiez cette réponse auprès d'un enseignant
• Consultez les ressources pédagogiques officielles
• Utilisez cette réponse comme point de départ, pas comme vérité absolue"""
        
        return response
    
    def _handle_resume(self, text):
        """Gère les résumés de texte"""
        
        # Analyse statistique du texte
        word_count = len(text.split())
        char_count = len(text)
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        # Calculer une estimation de temps de lecture (250 mots/min)
        reading_time = max(1, round(word_count / 250))
        
        response = f"""Résumé automatique généré :

📊 STATISTIQUES DU DOCUMENT :
• Nombre de mots : {word_count}
• Nombre de caractères : {char_count}
• Phrases estimées : {sentences}
• Temps de lecture : ~{reading_time} minute(s)

📝 ANALYSE PRÉLIMINAIRE :
Le document soumis nécessite une analyse approfondie pour extraire 
les points clés et thèmes principaux.

⚠️ LIMITATIONS :
• Ce résumé est automatique et peut manquer des nuances importantes
• Certains concepts complexes peuvent être simplifiés à l'excès
• La validation par un humain est fortement recommandée

📚 RECOMMANDATIONS :
• Lisez le document complet pour une compréhension approfondie
• Vérifiez que le résumé capture bien vos besoins
• Utilisez ce résumé comme support, pas comme remplacement

⚖️ CONFORMITÉ :
Ce résumé respecte les principes d'IA responsable et de protection des données."""
        
        return response
    
    def _handle_generation(self, prompt):
        """Gère la génération de contenu"""
        
        response = f"""Génération de contenu basée sur votre demande :

Demande initiale : "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"

🎯 CONTENU GÉNÉRÉ :
[Le contenu généré apparaîtrait ici dans une version de production avec un vrai modèle LLM]

⚠️ RAPPELS IMPORTANTS :
• Le contenu généré par IA peut contenir des inexactitudes
• Toujours vérifier et adapter le contenu à votre contexte
• Ne jamais plagier du contenu généré par IA sans attribution
• Respecter les droits d'auteur et la propriété intellectuelle

🔍 VÉRIFICATIONS NÉCESSAIRES :
• Exactitude factuelle : à vérifier
• Pertinence contextuelle : à adapter
• Originalité : à valider
• Conformité académique : à confirmer

📖 UTILISATION ÉTHIQUE :
• Utilisez ce contenu comme inspiration, pas comme produit final
• Citez l'utilisation d'IA si vous publiez ce contenu
• Adaptez toujours à votre voix et style personnels"""
        
        return response
    
    def _handle_analysis(self, text):
        """Gère l'analyse de contenu"""
        
        # Analyse simple
        words = text.split()
        unique_words = set(words)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        response = f"""Analyse automatique du contenu :

📊 MÉTRIQUES LINGUISTIQUES :
• Vocabulaire total : {len(words)} mots
• Vocabulaire unique : {len(unique_words)} mots
• Richesse lexicale : {round(len(unique_words) / max(len(words), 1) * 100, 1)}%
• Longueur moyenne des mots : {round(avg_word_length, 1)} caractères

🔍 ANALYSE QUALITATIVE :
L'analyse approfondie du contenu révèlerait des insights sur :
• Thèmes principaux
• Ton et style d'écriture
• Complexité du langage
• Structure argumentative

⚠️ AVERTISSEMENT :
Cette analyse est automatique et simplifiée. Une analyse humaine 
professionnelle fournirait des insights beaucoup plus riches.

💡 SUGGESTIONS :
• Comparez avec des analyses humaines expertes
• Utilisez comme point de départ pour votre propre analyse
• Ne vous fiez pas uniquement aux métriques quantitatives"""
        
        return response
    
    def _post_validation_checks(self, response):
        """Valide la réponse générée"""
        if not response or len(response.strip()) < 20:
            return {'is_valid': False, 'issues': ['Réponse trop courte']}
        return {'is_valid': True}
    
    def _generate_cache_key(self, content, request_type):
        """Génère une clé de cache unique"""
        content_to_hash = f"{request_type}:{content}"
        return hashlib.sha256(content_to_hash.encode()).hexdigest()
    
    def _check_cache(self, cache_key):
        """Vérifie si une réponse est en cache"""
        from app.models import CacheEntry
        
        cache = CacheEntry.query.filter_by(cache_key=cache_key).first()
        
        if cache and not cache.is_expired():
            # Incrémenter le compteur de hits
            cache.hit_count += 1
            cache.last_accessed = datetime.utcnow()
            
            from app import db
            db.session.commit()
            
            return {
                'response': cache.cached_response,
                'from_cache': True
            }
        
        return None
    
    def _save_to_cache(self, cache_key, response, request_type):
        """Sauvegarde une réponse dans le cache"""
        from app.models import CacheEntry
        from app import db
        
        # Vérifier si déjà en cache
        existing = CacheEntry.query.filter_by(cache_key=cache_key).first()
        if existing:
            return
        
        # Créer nouvelle entrée
        cache = CacheEntry(
            cache_key=cache_key,
            request_type=request_type,
            content_hash=cache_key[:32],
            cached_response=response,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(cache)
        db.session.commit()
    
    def stream_chat_api(self, messages, username=None, request_type=None):
        """Stream a chat response via Groq cloud API (OpenAI-compatible)."""
        groq_api_key = self.config.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEY')
        if not groq_api_key:
            yield f"data: {json.dumps({'error': 'Clé API Groq non configurée. Ajoutez GROQ_API_KEY dans votre .env'})}\n\n"
            return

        system_prompts = {
            'question': (
                "Tu es CampusMind, un assistant pédagogique pour les étudiants de l'ENSA Béni Mellal. "
                "Réponds de façon claire et précise aux questions. Maintiens le contexte de la conversation. "
                "Réponds en français."
            ),
            'resume': (
                "Tu es CampusMind, spécialisé dans les résumés de cours académiques. "
                "Produis des résumés structurés avec les points clés, définitions importantes et formules essentielles. "
                "Maintiens le contexte de la conversation. Réponds en français."
            ),
            'generation': (
                "Tu es CampusMind, expert en organisation académique. "
                "Aide l'étudiant à créer un planning de révision personnalisé et réaliste. "
                "Pose des questions pour cerner ses contraintes (examens, disponibilités, matières). "
                "Maintiens le contexte de la conversation. Réponds en français."
            ),
            'analysis': (
                "Tu es CampusMind, un assistant bienveillant pour le soutien émotionnel. "
                "Détecte les signes de stress, de frustration ou de découragement. "
                "Montre toujours de l'empathie en premier, puis propose des conseils pratiques et encourageants. "
                "Maintiens le contexte de la conversation. Réponds en français."
            ),
        }

        if request_type and request_type in system_prompts:
            system_prompt = system_prompts[request_type]
        else:
            system_prompt = (
                "Tu es CampusMind, un assistant pédagogique bienveillant pour les étudiants de l'ENSA Béni Mellal. "
                "Tu maintiens le contexte de la conversation et réponds de façon claire et précise. "
                "Si l'étudiant semble stressé, frustré ou découragé, montre d'abord de l'empathie avant de répondre. "
                "Tu peux générer des résumés de cours, répondre aux questions, proposer un planning d'études personnalisé. "
                "Réponds toujours en français, sauf si l'étudiant écrit dans une autre langue."
            )
        if username:
            system_prompt += f" L'étudiant s'appelle {username}, utilise son prénom naturellement et chaleureusement."

        full_messages = [{'role': 'system', 'content': system_prompt}] + messages
        payload = {
            'model': 'openai/gpt-oss-120b',
            'messages': full_messages,
            'stream': True,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }

        full_response = []
        try:
            with http_requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {groq_api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                stream=True,
                timeout=60
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                    if not line_str.startswith('data: '):
                        continue
                    data_str = line_str[6:]
                    if data_str.strip() == '[DONE]':
                        yield f"data: {json.dumps({'done': True, 'full_response': ''.join(full_response), 'source': 'groq', 'model': 'openai/gpt-oss-120b'})}\n\n"
                        return
                    try:
                        data = json.loads(data_str)
                        token = data['choices'][0]['delta'].get('content', '')
                        if token:
                            full_response.append(token)
                            yield f"data: {json.dumps({'token': token})}\n\n"
                    except Exception:
                        pass
        except http_requests.exceptions.HTTPError as e:
            detail = ''
            try:
                detail = e.response.json().get('error', {}).get('message', '')
            except Exception:
                pass
            yield f"data: {json.dumps({'error': f'Erreur API Groq : {detail or str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Erreur API : {str(e)}'})}\n\n"

    def get_model_info(self):
        """Retourne les informations sur le modèle"""
        return {
            'name': 'AI-Engine-v1.0',
            'version': '1.0.0',
            'type': 'Rule-based with ML augmentation',
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'features': [
                'Question answering',
                'Text summarization',
                'Content generation',
                'Text analysis'
            ],
            'safety_features': [
                'Sensitive data detection',
                'Content validation',
                'Human validation workflow',
                'RGPD compliance',
                'Caching system'
            ]
        }


# ==================== ANALYSEUR DE STRESS ====================

class StressAnalyzer:
    """Analyse le niveau de stress dans un texte"""
    
    STRESS_KEYWORDS = {
        # Niveau élevé (0.7-1.0)
        "je ne comprends rien": 0.95,
        "j'abandonne": 0.95,
        "je stresse": 0.9,
        "je panique": 0.9,
        "c'est trop difficile": 0.85,
        "je suis perdu": 0.8,
        "je ne comprends pas": 0.75,
        "je n'y arrive pas": 0.75,
        
        # Niveau moyen (0.4-0.7)
        "compliqué": 0.6,
        "difficile": 0.55,
        "bloqué": 0.5,
        "problème": 0.45,
        
        # Niveau bas (0.1-0.4)
        "question": 0.2,
        "doute": 0.3,
        "hésitation": 0.25,
    }
    
    def analyze(self, text):
        """
        Analyse le stress dans un texte
        Retourne un dictionnaire avec score et niveau
        """
        if not text:
            return {
                'score': 0.0,
                'level': 'normal',
                'detected_keywords': []
            }
        
        text_lower = text.lower()
        detected_keywords = []
        max_score = 0.0
        
        # Chercher tous les mots-clés de stress
        for keyword, score in self.STRESS_KEYWORDS.items():
            if keyword in text_lower:
                detected_keywords.append(keyword)
                max_score = max(max_score, score)
        
        # Déterminer le niveau
        if max_score >= 0.8:
            level = 'critique'
            recommendation = "Assistance humaine recommandée immédiatement"
        elif max_score >= 0.5:
            level = 'élevé'
            recommendation = "Soutien pédagogique suggéré"
        elif max_score >= 0.3:
            level = 'modéré'
            recommendation = "Surveillance recommandée"
        else:
            level = 'normal'
            recommendation = "Aucune action spécifique nécessaire"
        
        return {
            'score': round(max_score, 2),
            'level': level,
            'detected_keywords': detected_keywords,
            'recommendation': recommendation
        }