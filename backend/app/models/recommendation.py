from app import db
from datetime import datetime, date
import json

class DailyRecommendation(db.Model):
    __tablename__ = 'daily_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    breakfast = db.Column(db.Text, nullable=False)
    lunch = db.Column(db.Text, nullable=False)
    dinner = db.Column(db.Text, nullable=False)
    activities = db.Column(db.Text, nullable=False)
    total_calories = db.Column(db.Integer, nullable=False)
    target_calories = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('recommendations', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        breakfast = json.loads(self.breakfast) if self.breakfast else None
        lunch = json.loads(self.lunch) if self.lunch else None
        dinner = json.loads(self.dinner) if self.dinner else None
        activities = json.loads(self.activities) if self.activities else []
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'activities': activities,
            'total_calories': self.total_calories,
            'target_calories': self.target_calories,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_completed': self.is_completed
        }

class DailyCheckin(db.Model):
    """Daily check-in model for tracking user adherence to recommendations"""
    __tablename__ = 'daily_checkins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('daily_recommendations.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    food_completed = db.Column(db.Boolean, default=False)
    activity_completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('checkins', lazy=True))
    recommendation = db.relationship('DailyRecommendation', 
                                    backref=db.backref('checkins', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendation_id': self.recommendation_id,
            'date': self.date.isoformat() if self.date else None,
            'food_completed': self.food_completed,
            'activity_completed': self.activity_completed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }