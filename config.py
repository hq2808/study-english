import os

class Config:
    # PostgreSQL connection - use DATABASE_URL env variable or default to localhost
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/study_english'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-english-learning-2024')
