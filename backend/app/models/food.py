from app import db

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    calories_per_100g = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'calories_per_100g': self.calories_per_100g,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'category': self.category
        }

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    calories_per_hour = db.Column(db.Integer, nullable=False)
    intensity_level = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'calories_per_hour': self.calories_per_hour,
            'intensity_level': self.intensity_level
        }