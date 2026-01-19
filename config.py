import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///english_learning.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'smart-english-learning-2024'
