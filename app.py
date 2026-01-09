from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from gtts import gTTS
from deep_translator import GoogleTranslator
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///english_learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'smart-english-learning-2024'

db = SQLAlchemy(app)

# ==================== MODELS ====================

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
    context = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(10), nullable=True)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'translation': self.translation,
            'context': self.context,
            'level': self.level,
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None
        }


# ==================== ROUTES - PAGES ====================

@app.route('/')
def index():
    """Main reading interface"""
    return render_template('index.html')


@app.route('/flashcards')
def flashcards():
    """Flashcard review page"""
    return render_template('flashcards.html')


# ==================== API - LESSONS ====================

@app.route('/api/lessons')
def get_lessons():
    """Get all lessons, optionally filtered by level"""
    level = request.args.get('level')
    if level:
        lessons = Lesson.query.filter_by(level=level.upper()).all()
    else:
        lessons = Lesson.query.all()
    return jsonify([lesson.to_dict() for lesson in lessons])


@app.route('/api/lessons/<int:lesson_id>')
def get_lesson(lesson_id):
    """Get a specific lesson by ID"""
    lesson = Lesson.query.get_or_404(lesson_id)
    return jsonify(lesson.to_dict())


# ==================== API - TRANSLATION ====================

@app.route('/api/translate', methods=['POST'])
def translate_word():
    """Translate English word to Vietnamese"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        translator = GoogleTranslator(source='en', target='vi')
        translation = translator.translate(text)
        return jsonify({
            'original': text,
            'translation': translation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API - TEXT-TO-SPEECH ====================

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech and return audio file"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API - VOCABULARY ====================

@app.route('/api/vocabulary')
def get_vocabulary():
    """Get all saved vocabulary"""
    vocabulary = Vocabulary.query.order_by(Vocabulary.created_at.desc()).all()
    return jsonify([v.to_dict() for v in vocabulary])


@app.route('/api/vocabulary', methods=['POST'])
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


@app.route('/api/vocabulary/<int:vocab_id>/review', methods=['PUT'])
def review_vocabulary(vocab_id):
    """Increment review count for a vocabulary item"""
    vocab = Vocabulary.query.get_or_404(vocab_id)
    vocab.review_count += 1
    vocab.last_reviewed = datetime.utcnow()
    db.session.commit()
    return jsonify(vocab.to_dict())


@app.route('/api/vocabulary/<int:vocab_id>', methods=['DELETE'])
def delete_vocabulary(vocab_id):
    """Delete a vocabulary item"""
    vocab = Vocabulary.query.get_or_404(vocab_id)
    db.session.delete(vocab)
    db.session.commit()
    return jsonify({'message': 'Vocabulary deleted successfully'})


# ==================== INITIALIZE DATABASE ====================

def init_db():
    """Initialize database with sample lessons"""
    with app.app_context():
        db.create_all()
        
        # Check if lessons already exist
        if Lesson.query.first():
            return
        
        # Sample A1 Lessons
        a1_lessons = [
            {
                'title': 'Greetings - Chào hỏi',
                'level': 'A1',
                'category': 'Daily Communication',
                'content': '''Hello! My name is Anna. I am from Vietnam. I am 25 years old. 
                
Nice to meet you! How are you today? I am fine, thank you.

Good morning! Good afternoon! Good evening! Good night!

What is your name? My name is John. Where are you from? I am from America.

This is my friend. Her name is Lisa. She is a teacher. He is a doctor.

Goodbye! See you later! See you tomorrow! Have a nice day!'''
            },
            {
                'title': 'Family - Gia đình',
                'level': 'A1',
                'category': 'Family & Relationships',
                'content': '''This is my family. I have a big family.

My father is 50 years old. He is a businessman. My mother is 48 years old. She is a nurse.

I have one brother and two sisters. My brother is older than me. He is 28 years old.

My sisters are younger. They are students. They go to school every day.

My grandmother lives with us. She is 75 years old. She cooks delicious food.

I love my family very much. We eat dinner together every evening.'''
            },
            {
                'title': 'Daily Routine - Thói quen hàng ngày',
                'level': 'A1',
                'category': 'Daily Life',
                'content': '''I wake up at 6 o'clock every morning. I brush my teeth and wash my face.

I eat breakfast at 7 o'clock. I usually have bread and milk for breakfast.

I go to work at 8 o'clock. I take the bus to my office. I work from 9 to 5.

I have lunch at 12 o'clock. I eat lunch at a restaurant near my office.

I come home at 6 o'clock. I take a shower and change my clothes.

I have dinner with my family at 7 o'clock. After dinner, I watch TV or read a book.

I go to bed at 10 o'clock. I sleep for 8 hours every night.'''
            },
            {
                'title': 'Shopping - Mua sắm',
                'level': 'A1',
                'category': 'Shopping',
                'content': '''I go shopping on Saturday. I go to the supermarket with my mother.

Excuse me, how much is this? This shirt is 200,000 dong. That is too expensive!

Can I have a discount please? OK, I can give you 10 percent off.

I want to buy some apples. How much are the apples? They are 50,000 dong per kilogram.

I need a bag please. Here you are. Thank you very much!

Do you accept credit card? Yes, we do. No, only cash please.

Where is the fitting room? It is over there, on the left.'''
            }
        ]
        
        # Sample A2 Lessons
        a2_lessons = [
            {
                'title': 'Travel Plans - Kế hoạch du lịch',
                'level': 'A2',
                'category': 'Travel',
                'content': '''I am planning a trip to Da Nang next month. I have never been there before.

I want to visit the beach and see the Golden Bridge. I heard it is very beautiful.

I need to book a hotel room. I prefer a room with a sea view. How much is it per night?

I will travel by plane because it is faster. The flight takes about one hour.

I am going to stay for five days. I will try the local food and visit some temples.

What should I pack? I need to bring sunscreen, a hat, and my camera.

I am really excited about this trip! I hope the weather will be nice.'''
            },
            {
                'title': 'At the Restaurant - Tại nhà hàng',
                'level': 'A2',
                'category': 'Food & Dining',
                'content': '''Good evening, do you have a reservation? Yes, I booked a table for four people.

Here is the menu. What would you like to order? I need a few minutes to decide.

I would like to have the grilled fish with vegetables. How is the steak here?

The steak is very popular. It comes with mashed potatoes and salad.

Could I have some water please? Still or sparkling? Still water is fine.

Is there anything you cannot eat? I am allergic to seafood and nuts.

For dessert, I recommend the chocolate cake. It is homemade and delicious.

Can I have the bill please? Would you like to pay together or separately?'''
            },
            {
                'title': 'Health and Doctor - Sức khỏe và bác sĩ',
                'level': 'A2',
                'category': 'Health',
                'content': '''I am not feeling well today. I have a headache and a sore throat.

I think I caught a cold. I have been sneezing all day. My nose is runny.

I need to see a doctor. I made an appointment for this afternoon.

Doctor, I have had a fever since yesterday. My temperature is 38 degrees.

Let me examine you. Open your mouth please. Take a deep breath.

You have the flu. You should rest at home and drink plenty of water.

I will prescribe some medicine for you. Take this three times a day after meals.

You should feel better in a few days. Come back if the symptoms get worse.'''
            },
            {
                'title': 'Job Interview - Phỏng vấn xin việc',
                'level': 'A2',
                'category': 'Work',
                'content': '''Thank you for coming to the interview today. Please have a seat.

Tell me about yourself. I graduated from university three years ago with a degree in business.

I have worked as a sales assistant for two years. I enjoy working with customers.

Why do you want to work for our company? I admire your company's reputation and products.

What are your strengths? I am hardworking, organized, and good at solving problems.

What are your weaknesses? Sometimes I work too hard and forget to take breaks.

Where do you see yourself in five years? I hope to become a team leader.

Do you have any questions for us? Yes, what are the working hours?'''
            }
        ]
        
        # Sample B1 Lessons
        b1_lessons = [
            {
                'title': 'Environmental Issues - Vấn đề môi trường',
                'level': 'B1',
                'category': 'Environment',
                'content': '''Climate change is one of the biggest challenges facing our world today. Global temperatures are rising, causing extreme weather events.

Many scientists believe that human activities, especially burning fossil fuels, are the main cause of global warming.

Deforestation is another serious problem. When forests are cut down, animals lose their homes and less carbon dioxide is absorbed from the atmosphere.

Plastic pollution is harming our oceans. Millions of tons of plastic waste end up in the sea every year, killing marine life.

What can we do to help? We can reduce, reuse, and recycle. We can use public transportation instead of driving.

Governments need to invest in renewable energy sources like solar and wind power. We all have a responsibility to protect our planet.

Small changes in our daily habits can make a big difference. Every action counts in the fight against climate change.'''
            },
            {
                'title': 'Technology and Society - Công nghệ và xã hội',
                'level': 'B1',
                'category': 'Technology',
                'content': '''Technology has transformed the way we live, work, and communicate. Smartphones have become an essential part of our daily lives.

Social media allows us to connect with friends and family around the world. However, it also has negative effects on mental health.

Many people spend too much time online instead of having face-to-face conversations. This can lead to feelings of loneliness and isolation.

Artificial intelligence is changing many industries. Some jobs may disappear, but new opportunities will be created.

Online learning has become more popular, especially since the pandemic. Students can access courses from anywhere in the world.

Privacy is a growing concern in the digital age. Companies collect our personal data, and we need to be careful about what we share online.

Despite the challenges, technology has many benefits. It has improved healthcare, education, and helped connect people across borders.'''
            },
            {
                'title': 'Cultural Differences - Khác biệt văn hóa',
                'level': 'B1',
                'category': 'Culture',
                'content': '''When traveling to a new country, it is important to understand and respect local customs and traditions.

In some cultures, it is polite to remove your shoes before entering a home. In others, this is not necessary.

Body language can have different meanings in different countries. For example, nodding your head does not always mean yes.

Gift-giving customs vary widely. In some Asian countries, gifts should be wrapped beautifully and given with both hands.

Table manners are also different around the world. In some places, it is rude to leave food on your plate. In others, it shows you are satisfied.

Learning a few words in the local language is always appreciated. It shows respect for the culture and helps you connect with local people.

Being open-minded and willing to learn about different cultures can enrich your travel experiences and help you make lasting friendships.'''
            },
            {
                'title': 'Future Career Planning - Kế hoạch nghề nghiệp',
                'level': 'B1',
                'category': 'Career',
                'content': '''Choosing the right career path is one of the most important decisions you will make in life.

First, you should identify your interests and skills. What subjects do you enjoy? What are you naturally good at?

Research different career options and industry trends. Some fields are growing rapidly while others are declining.

Consider getting additional qualifications or certifications. Continuous learning is essential in today\'s competitive job market.

Networking is crucial for career success. Attend industry events, join professional associations, and connect with people on LinkedIn.

Internships and volunteer work can provide valuable experience. They also help you discover what you really want to do.

Setting short-term and long-term goals will help you stay focused. Review and adjust your plans regularly.

Remember that career paths are rarely straight. Many successful people have changed careers multiple times before finding their passion.'''
            }
        ]
        
        # Add all lessons to database
        for lesson_data in a1_lessons + a2_lessons + b1_lessons:
            lesson = Lesson(**lesson_data)
            db.session.add(lesson)
        
        db.session.commit()
        print("Database initialized with sample lessons!")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
