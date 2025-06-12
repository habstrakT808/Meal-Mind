from app.ml.food_database import USDAFoodDatabase
from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine
from app.ml.diet_progress_analyzer import DietProgressAnalyzer
from app.ml.recommendation_engine import MealRecommendationEngine
from app.ml.model_serializer import ModelSerializer

# Export the upgraded components
__all__ = [
    'USDAFoodDatabase',
    'AdvancedRecommendationEngine',
    'DietProgressAnalyzer',
    'MealRecommendationEngine',
    'ModelSerializer'
]
