from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Load configuration from environment variables for better security and flexibility
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')

    # Initialize database with the app
    db.init_app(app)

    # Import blueprints
    from .views import views
    from .auth import auth

    # Register blueprints with specific URL prefixes if necessary
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
