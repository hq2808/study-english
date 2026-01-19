from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main reading interface"""
    return render_template('index.html')


@main_bp.route('/flashcards')
def flashcards():
    """Flashcard review page"""
    return render_template('flashcards.html')


@main_bp.route('/tts')
def tts():
    """Text to Speech page"""
    return render_template('tts.html')
