from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from models import Lesson, Vocabulary
from extensions import db
from services.translation import translate_text
from services.tts import generate_speech_audio
from services.text_parser import parse_vocabulary_with_examples

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
    phonetic = data.get('phonetic', '').strip() if data.get('phonetic') else None
    context = data.get('context', '').strip() if data.get('context') else None
    example_en = data.get('example_en', '').strip() if data.get('example_en') else None
    example_vi = data.get('example_vi', '').strip() if data.get('example_vi') else None
    level = data.get('level', '').strip() if data.get('level') else None
    
    if not word or not translation:
        return jsonify({'error': 'Word and translation are required'}), 400
    
    # Check if word already exists
    existing = Vocabulary.query.filter_by(word=word.lower()).first()
    if existing:
        return jsonify({'error': 'Word already saved', 'vocabulary': existing.to_dict()}), 409
    
    vocab = Vocabulary(
        word=word.lower(),
        translation=translation,
        phonetic=phonetic,
        context=context,
        example_en=example_en,
        example_vi=example_vi,
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


# ==================== API - TEXT PARSER ====================

@api_bp.route('/vocabulary/parse', methods=['POST'])
def parse_text():
    """Parse text to extract vocabulary entries"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        vocabulary_items = parse_vocabulary_with_examples(text)
        return jsonify({
            'count': len(vocabulary_items),
            'items': vocabulary_items
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/vocabulary/bulk', methods=['POST'])
def save_vocabulary_bulk():
    """Save multiple vocabulary items at once"""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items provided'}), 400
    
    saved = []
    skipped = []
    
    for item in items:
        word = item.get('word', '').strip()
        translation = item.get('translation', '').strip()
        
        if not word or not translation:
            continue
        
        # Check if word already exists
        existing = Vocabulary.query.filter_by(word=word.lower()).first()
        if existing:
            skipped.append({'word': word, 'reason': 'Already exists'})
            continue
        
        vocab = Vocabulary(
            word=word.lower(),
            translation=translation,
            phonetic=item.get('phonetic'),
            context=item.get('context'),
            example_en=item.get('example_en'),
            example_vi=item.get('example_vi'),
            level=item.get('level')
        )
        db.session.add(vocab)
        saved.append(word)
    
    db.session.commit()
    
    return jsonify({
        'saved_count': len(saved),
        'saved': saved,
        'skipped_count': len(skipped),
        'skipped': skipped
    }), 201


# ==================== API - PRACTICE ====================

@api_bp.route('/vocabulary/<int:vocab_id>/typing', methods=['PUT'])
def update_typing_result(vocab_id):
    """Update typing practice result for a vocabulary item"""
    data = request.get_json()
    correct = data.get('correct', False)
    
    vocab = Vocabulary.query.get_or_404(vocab_id)
    
    if correct:
        vocab.typing_correct += 1
    
    vocab.review_count += 1
    vocab.last_reviewed = datetime.utcnow()
    db.session.commit()
    
    return jsonify(vocab.to_dict())


@api_bp.route('/vocabulary/<int:vocab_id>/speech', methods=['PUT'])
def update_speech_result(vocab_id):
    """Update speech practice result for a vocabulary item"""
    data = request.get_json()
    correct = data.get('correct', False)
    
    vocab = Vocabulary.query.get_or_404(vocab_id)
    
    if correct:
        vocab.speech_correct += 1
    
    vocab.review_count += 1
    vocab.last_reviewed = datetime.utcnow()
    db.session.commit()
    
    return jsonify(vocab.to_dict())


@api_bp.route('/vocabulary/practice')
def get_practice_vocabulary():
    """Get vocabulary for practice, prioritizing less reviewed items"""
    mode = request.args.get('mode', 'words')  # 'words' or 'phrases'
    
    if mode == 'phrases':
        # Only items with example sentences
        vocabulary = Vocabulary.query.filter(
            Vocabulary.example_en.isnot(None),
            Vocabulary.example_en != ''
        ).order_by(Vocabulary.review_count.asc()).all()
    else:
        # All vocabulary
        vocabulary = Vocabulary.query.order_by(Vocabulary.review_count.asc()).all()
    
    return jsonify([v.to_dict() for v in vocabulary])
