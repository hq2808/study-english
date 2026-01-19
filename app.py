from flask import Flask
from config import Config
from extensions import db
from utils.seed import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    init_db(app)
    
    app.run(debug=True, port=5000)
