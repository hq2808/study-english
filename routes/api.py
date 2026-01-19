from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from models import Lesson, Vocabulary
from extensions import db
from services.translation import translate_text
from services.tts import generate_speech_audio

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================== API - LESSONS ====================

@api_bp.route('/lessons')
def get_lessons():
    """Get all lessons, optionally filtered by level"""
    level = request.args.get('level')
    if level:
        lessons = Lesson.query.filter_by(level=level.upper()).all()
    else:
        lessons = Lesson.query.all()
    return jsonify([lesson.to_dict() for lesson in lessons])


@api_bp.route('/lessons/<int:lesson_id>')
def get_lesson(lesson_id):
    """Get a specific lesson by ID"""
    lesson = Lesson.query.get_or_404(lesson_id)
    return jsonify(lesson.to_dict())


# ==================== API - TRANSLATION ====================

@api_bp.route('/translate', methods=['POST'])
def translate_word():
    """Translate English word to Vietnamese"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        translation = translate_text(text, source='en', target='vi')
        return jsonify({
            'original': text,
            'translation': translation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API - TEXT-TO-SPEECH ====================

@api_bp.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech and return audio file"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        audio_buffer = generate_speech_audio(text)
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API - VOCABULARY ====================

@api_bp.route('/vocabulary')
def get_vocabulary():
    """Get all saved vocabulary"""
    vocabulary = Vocabulary.query.order_by(Vocabulary.created_at.desc()).all()
    return jsonify([v.to_dict() for v in vocabulary])


@api_bp.route('/vocabulary', methods=['POST'])
def save_vocabulary():
    """Save a word to vocabulary/flashcard"""
    data = request.get_json()
    word = data.get('word', '').strip()
    translation = data.get('translation', '').strip()
    context = data.get('context', '').strip()
    level = data.get('level', '').strip()
    
    if not word or not translation:
        return jsonify({'error': 'Word and translation are required'}), 400
    
    # Check if word already exists
    existing = Vocabulary.query.filter_by(word=word.lower()).first()
    if existing:
        return jsonify({'error': 'Word already saved', 'vocabulary': existing.to_dict()}), 409
    
    vocab = Vocabulary(
        word=word.lower(),
        translation=translation,
        context=context,
        level=level
    )
    db.session.add(vocab)
    db.session.commit()
    
    return jsonify(vocab.to_dict()), 201


@api_bp.route('/vocabulary/<int:vocab_id>/review', methods=['PUT'])
def review_vocabulary(vocab_id):
    """Increment review count for a vocabulary item"""
    vocab = Vocabulary.query.get_or_404(vocab_id)
    vocab.review_count += 1
    vocab.last_reviewed = datetime.utcnow()
    db.session.commit()
    return jsonify(vocab.to_dict())


@api_bp.route('/vocabulary/<int:vocab_id>', methods=['DELETE'])
def delete_vocabulary(vocab_id):
    """Delete a vocabulary item"""
    vocab = Vocabulary.query.get_or_404(vocab_id)
    db.session.delete(vocab)
    db.session.commit()
    return jsonify({'message': 'Vocabulary deleted successfully'})
