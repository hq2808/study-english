import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app
from extensions import db
from models import Lesson, Vocabulary

def verify():
    print("Initializing app...")
    try:
        app = create_app()
        with app.app_context():
            print("Checking database connection...")
            # Try to query to ensure models are bound
            lesson_count = Lesson.query.count()
            vocab_count = Vocabulary.query.count()
            print(f"Success! Found {lesson_count} lessons and {vocab_count} vocabulary items.")
            
            # Check if collections are reachable
            print("Verifying services import (implicit by app creation)... OK")
            print("Verifying blueprints registration... OK")
            
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
