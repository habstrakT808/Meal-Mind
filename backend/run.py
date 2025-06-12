# backend/run.py
import os
import sys
import click
from app import create_app, db
from datetime import datetime
from flask.cli import FlaskGroup

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Add key objects to shell context for convenience."""
    # Import models for shell context
    from app.models.user import User, UserProfile
    from app.models.food import Food, Activity
    from app.models.recommendation import DailyRecommendation, DailyCheckin
    
    return {
        'db': db, 
        'User': User, 
        'UserProfile': UserProfile, 
        'Food': Food, 
        'Activity': Activity,
        'DailyRecommendation': DailyRecommendation,
        'DailyCheckin': DailyCheckin
    }

@app.cli.command("create-db")
def create_db():
    """Create database tables."""
    db.create_all()
    click.echo("Database tables created!")

@app.cli.command("drop-db")
def drop_db():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables?', abort=True):
        db.drop_all()
        click.echo("All database tables dropped!")

@app.cli.command("seed-db")
def seed_db():
    """Seed the database with initial data."""
    from app.models.user import User, UserProfile
    from werkzeug.security import generate_password_hash
    
    # Create admin user if not exists
    if not User.query.filter_by(email="admin@mealmind.com").first():
        admin = User(
            email="admin@mealmind.com",
            username="admin",
            password_hash=generate_password_hash("adminpass")
        )
        db.session.add(admin)
        
    # Create test user if not exists
    if not User.query.filter_by(email="test@mealmind.com").first():
        test_user = User(
            email="test@mealmind.com",
            username="testuser",
            password_hash=generate_password_hash("testpass")
        )
        db.session.add(test_user)
        
        # Add profile for test user
        profile = UserProfile(
            user=test_user,
            weight=70.0,
            height=175.0,
            age=30,
            gender="male",
            activity_level="moderate",
            goal_weight=68.0,
            dietary_restrictions="[]"
        )
        db.session.add(profile)
    
    db.session.commit()
    click.echo("Database seeded with initial data!")

# Main execution
if __name__ == '__main__':
    # Print routes
    with app.app_context():
        print("\n=== REGISTERED ROUTES ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule}")
        print("========================\n")
    
    # Run the application
    app.run(host="0.0.0.0", debug=True)