from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Set the login view for the LoginManager
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    # Import routes after the app and extensions are initialized
    from app.routes import app as routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

# Import the models for the app
import app.models

# Initialize the app and run it
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
