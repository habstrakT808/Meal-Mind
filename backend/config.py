# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-meal-mind'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour for production (can be adjusted)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use SQLite for development with absolute path
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "mealmind_dev.db")}'
    JWT_ACCESS_TOKEN_EXPIRES = False  # No expiration during development

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = False

class ProductionConfig(Config):
    """Production configuration."""
    # Use SQLite for production deployment in Docker
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "mealmind_prod.db")}'
    
    # Production database optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,  # recycle connections after 1 hour
        'pool_pre_ping': True  # verify connections before use
    }
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# Configuration dictionary to easily select environment
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig, 
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Return the appropriate configuration object based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, config_dict['default'])