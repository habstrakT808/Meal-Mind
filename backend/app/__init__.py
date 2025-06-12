# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import sys
from datetime import timedelta
from config import Config

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_env=None):
    app = Flask(__name__)
    
    # Get configuration from environment or argument
    if config_env is None:
        config_env = os.environ.get('FLASK_ENV', 'development')
    
    # Import configuration
    from config import config_dict
    app.config.from_object(config_dict[config_env])
    
    # Print which configuration is being used
    print(f"Running with {config_env} configuration")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Set up CORS - allow specific origins for API routes
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "https://mealmind-2k6u3ud5g-ranggajs-projects.vercel.app",
        "https://mealmind-ranggajs-projects.vercel.app",
        "*"  # Keep wildcard for development
    ]}}, 
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         expose_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    # Add a simple test route first
    @app.route('/')
    def hello():
        return "Meal Mind Backend is running!"
    
    # Import and register blueprints
    with app.app_context():
        # Import blueprints
        from app.routes.auth import auth_bp
        from app.routes.profile import profile_bp
        from app.routes.recommendations import recommendations_bp
        from app.routes.activities import activities_bp
        from app.routes.user import user_bp
        from app.routes.progress import progress_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(profile_bp, url_prefix='/api/profile')
        app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
        app.register_blueprint(activities_bp, url_prefix='/api/activities')
        app.register_blueprint(user_bp, url_prefix='/api/user')
        app.register_blueprint(progress_bp, url_prefix='/api/progress')
        
        # Print all registered routes
        print("========================")
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule}")
        print("========================")
        
        # Create database tables
        try:
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            
    return app