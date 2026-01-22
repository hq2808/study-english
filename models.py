from datetime import datetime
from extensions import db


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(10), nullable=False)  # A1, A2, B1
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'level': self.level,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }


class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(200), nullable=False)
    phonetic = db.Column(db.String(100), nullable=True)  # IPA phonetic transcription
    context = db.Column(db.Text, nullable=True)
    example_en = db.Column(db.Text, nullable=True)  # Example sentence in English
    example_vi = db.Column(db.Text, nullable=True)  # Example sentence translation
    level = db.Column(db.String(10), nullable=True)
    review_count = db.Column(db.Integer, default=0)
    typing_correct = db.Column(db.Integer, default=0)  # Typing practice correct count
    speech_correct = db.Column(db.Integer, default=0)  # Speech practice correct count
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'translation': self.translation,
            'phonetic': self.phonetic,
            'context': self.context,
            'example_en': self.example_en,
            'example_vi': self.example_vi,
            'level': self.level,
            'review_count': self.review_count,
            'typing_correct': self.typing_correct,
            'speech_correct': self.speech_correct,
            'created_at': self.created_at.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None
        }
