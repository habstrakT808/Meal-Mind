import json
import random
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from app.ml.food_database import USDAFoodDatabase
from app.ml.model_serializer import ModelSerializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('recommendation_engine.log'), logging.StreamHandler()]
)
logger = logging.getLogger('recommendation_engine')

class AdvancedRecommendationEngine:
    """
    Advanced recommendation engine that leverages machine learning 
    to provide personalized meal recommendations based on user preferences,
    nutritional needs, and health goals.
    """
    
    def __init__(self, food_db_path='food_database.db', api_key=None):
        """
        Initialize the advanced recommendation engine
        
        Args:
            food_db_path: Path to SQLite food database
            api_key: USDA FoodData Central API key
        """
        self.food_db = USDAFoodDatabase(db_path=food_db_path, api_key=api_key)
        
        # Ensure the database has some initial data
        self.food_db.seed_default_foods()
        
        # Activity data
        self.activities_data = [
            {'name': 'Jogging', 'calories_per_hour': 400, 'intensity': 'medium', 'met': 7.0},
            {'name': 'Bersepeda', 'calories_per_hour': 300, 'intensity': 'medium', 'met': 6.0},
            {'name': 'Berenang', 'calories_per_hour': 500, 'intensity': 'high', 'met': 8.0},
            {'name': 'Jalan Kaki', 'calories_per_hour': 200, 'intensity': 'low', 'met': 3.5},
            {'name': 'Senam Aerobik', 'calories_per_hour': 350, 'intensity': 'medium', 'met': 6.5},
            {'name': 'Push Up & Sit Up', 'calories_per_hour': 250, 'intensity': 'medium', 'met': 3.8},
            {'name': 'Yoga', 'calories_per_hour': 180, 'intensity': 'low', 'met': 3.0},
            {'name': 'Badminton', 'calories_per_hour': 320, 'intensity': 'medium', 'met': 5.5},
            {'name': 'Lari Interval', 'calories_per_hour': 450, 'intensity': 'high', 'met': 8.5},
            {'name': 'Pilates', 'calories_per_hour': 210, 'intensity': 'low', 'met': 3.5},
            {'name': 'Sepak Bola', 'calories_per_hour': 430, 'intensity': 'high', 'met': 7.0},
            {'name': 'Basket', 'calories_per_hour': 440, 'intensity': 'high', 'met': 6.5},
            {'name': 'Angkat Beban', 'calories_per_hour': 280, 'intensity': 'medium', 'met': 5.0},
            {'name': 'Berjalan Cepat', 'calories_per_hour': 260, 'intensity': 'medium', 'met': 4.3},
            {'name': 'Renang Gaya Bebas', 'calories_per_hour': 530, 'intensity': 'high', 'met': 8.3}
        ]
        
        # User recommendation history cache (user_id -> history data)
        self.user_history = {}
        
        # Buat direktori untuk model jika belum ada
        os.makedirs("models", exist_ok=True)
        
        # Similarity model for food recommendations - load or initialize
        self.vectorizer = ModelSerializer.initialize_vectorizer(
            food_data=self.food_db.get_all_foods(limit=1000),
            model_path="models/tfidf_vectorizer.joblib"
        )
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
        
        Args:
            weight: Weight in kg
            height: Height in cm
            age: Age in years
            gender: Gender ('male' or 'female')
        
        Returns:
            BMR in calories per day
        """
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Physical activity level
            
        Returns:
            TDEE in calories per day
        """
        activity_multipliers = {
            'sedentary': 1.2,      # Little or no exercise
            'light': 1.375,        # Light exercise 1-3 days/week
            'moderate': 1.55,      # Moderate exercise 3-5 days/week
            'active': 1.725,       # Heavy exercise 6-7 days/week
            'very_active': 1.9     # Very heavy exercise, physical job or 2x training
        }
        return bmr * activity_multipliers.get(activity_level, 1.55)
    
    def calculate_target_calories(self, 
                                  current_weight: float, 
                                  goal_weight: float, 
                                  tdee: float, 
                                  timeframe: int = 30,
                                  gender: str = 'male') -> float:
        """
        Calculate target daily calories for weight goal
        
        Args:
            current_weight: Current weight in kg
            goal_weight: Target weight in kg
            tdee: Total Daily Energy Expenditure
            timeframe: Number of days to achieve goal
            gender: User gender
            
        Returns:
            Target calories per day
        """
        # Weight difference in kg
        weight_diff = goal_weight - current_weight
        
        # Weight loss/gain rate
        # Safe weight loss rate is up to 0.5-1% of body weight per week (0.5-1 kg)
        # Safe weight gain rate is about 0.25-0.5% of body weight per week
        
        # Calculate the maximum safe weight change per day
        if weight_diff < 0:  # Weight loss
            max_daily_change = min(0.14, current_weight * 0.001)  # Max 1% per week = 0.14% per day
        else:  # Weight gain
            max_daily_change = min(0.07, current_weight * 0.0005)  # Max 0.5% per week = 0.07% per day
        
        # Adjust if the goal is too aggressive
        daily_change_needed = weight_diff / timeframe
        daily_change = max(min(daily_change_needed, max_daily_change), -max_daily_change)
        
        # Each kg is about 7700 calories
        calorie_adjustment = daily_change * 7700
        
        target_calories = tdee + calorie_adjustment
        
        # Ensure minimum healthy calorie intake (1200 for women, 1500 for men)
        min_calories = 1500 if gender.lower() == 'male' else 1200
        
        return max(target_calories, min_calories)
    
    def adjust_target_calories_for_missed_days(self,
                                              original_target: float,
                                              current_weight: float,
                                              goal_weight: float,
                                              days_passed: int,
                                              successful_days: int,
                                              remaining_days: int,
                                              tdee: float,
                                              gender: str = 'male') -> float:
        """
        Adjust target calories if user has missed some days of their plan
        
        Args:
            original_target: Original target calories per day
            current_weight: Current weight in kg
            goal_weight: Target weight in kg
            days_passed: Days since plan started
            successful_days: Days successfully completed
            remaining_days: Days remaining in the plan
            tdee: Total Daily Energy Expenditure
            gender: User gender
            
        Returns:
            Adjusted target calories per day
        """
        if days_passed == 0 or remaining_days == 0:
            return original_target
        
        # Weight difference remaining
        weight_diff = goal_weight - current_weight
        
        # Original daily deficit/surplus
        original_daily_adjustment = (original_target - tdee)
        
        # Expected progress by now (in calories)
        expected_progress = days_passed * original_daily_adjustment
        
        # Actual progress (in calories)
        actual_progress = successful_days * original_daily_adjustment
        
        # Calorie deficit needed to recover
        recovery_deficit = expected_progress - actual_progress
        
        # Distribute the recovery over the remaining days
        daily_recovery = recovery_deficit / remaining_days
        
        # Add to the daily target
        new_target = original_target - daily_recovery
        
        # Safety check - don't go too extreme
        if weight_diff < 0:  # Weight loss
            # When losing weight, ensure we don't drop below a certain threshold
            min_calories = 1500 if gender.lower() == 'male' else 1200
            max_deficit = tdee * 0.3  # Maximum 30% deficit for safety
            new_target = max(new_target, tdee - max_deficit)
            new_target = max(new_target, min_calories)
        else:  # Weight gain
            # When gaining weight, ensure we don't exceed a reasonable surplus
            max_surplus = tdee * 0.2  # Maximum 20% surplus
            new_target = min(new_target, tdee + max_surplus)
        
        return new_target
    
    def get_foods_for_meal(self, 
                          meal_type: str, 
                          target_calories: float,
                          foods_count: int = 10,
                          dietary_restrictions: List[str] = None,
                          preferred_foods: List[str] = None,
                          exclude_foods: List[str] = None,
                          min_calories: float = None,
                          max_calories: float = None) -> List[Dict]:
        """
        Get a list of foods suitable for a meal type
        
        Args:
            meal_type: Meal type (breakfast, lunch, dinner, snack)
            target_calories: Target calories for the meal
            foods_count: Number of foods to return
            dietary_restrictions: List of foods to restrict (e.g., vegetarian)
            preferred_foods: List of preferred foods
            exclude_foods: List of foods to exclude
            min_calories: Minimum calories (optional)
            max_calories: Maximum calories (optional)
            
        Returns:
            List of food dictionaries
        """
        # Default values
        dietary_restrictions = dietary_restrictions or []
        preferred_foods = preferred_foods or []
        exclude_foods = exclude_foods or []
        
        # Get suitable foods from database
        db = USDAFoodDatabase()
        
        # Set default calorie range if not provided
        if min_calories is None:
            min_calories = target_calories * 0.75
        if max_calories is None:
            max_calories = target_calories * 1.25
        
        try:
            # Try with strict meal type first
            foods = db.get_foods_by_meal_type(
                meal_type, 
                min_calories=min_calories,
                max_calories=max_calories,
                dietary_restrictions=dietary_restrictions,
                exclude_foods=exclude_foods
            )
            
            # If not enough options, try with expanded calorie range
            if len(foods) < foods_count:
                expanded_min = target_calories * 0.6
                expanded_max = target_calories * 1.4
                
                foods = db.get_foods_by_meal_type(
                    meal_type, 
                    min_calories=expanded_min,
                    max_calories=expanded_max,
                    dietary_restrictions=dietary_restrictions,
                    exclude_foods=exclude_foods
                )
            
            # If still not enough options, try with all meal types
            if len(foods) < foods_count / 2:
                foods = db.get_foods_by_calorie_range(
                    min_calories=expanded_min,
                    max_calories=expanded_max,
                    dietary_restrictions=dietary_restrictions,
                    exclude_foods=exclude_foods
                )
                
                # If still empty, ignore calorie constraints
                if len(foods) < 2:
                    foods = db.get_foods_by_meal_type(
                        meal_type,
                        dietary_restrictions=dietary_restrictions,
                        exclude_foods=exclude_foods
                    )
            
            # Prioritize preferred foods if any match
            if preferred_foods:
                for food in foods:
                    if food['name'] in preferred_foods:
                        food['priority'] = 10
                    else:
                        food['priority'] = 0
                
                # Sort by priority (higher first) then by how close to target calories
                foods.sort(key=lambda x: (-x.get('priority', 0), abs(x['calories'] - target_calories)))
            else:
                # Sort by how close to target calories
                foods.sort(key=lambda x: abs(x['calories'] - target_calories))
                
            # Shuffle the top matches slightly for more variety
            import random
            top_count = min(10, len(foods))
            if top_count > 3:
                top_foods = foods[:top_count]
                random.shuffle(top_foods)
                foods[:top_count] = top_foods
                
            # Remove the priority key before returning
            for food in foods:
                if 'priority' in food:
                    del food['priority']
                    
            # Return the requested number of foods or all if fewer
            return foods[:foods_count]
            
        finally:
            db.close()
            
        # Fallback - should not be reached if database has foods
        return [self._get_fallback_meal(meal_type) for _ in range(min(foods_count, 3))]
    
    def recommend_meals(self, 
                       target_calories: float,
                       dietary_restrictions: List[str] = None,
                       preferred_foods: List[str] = None,
                       exclude_foods: List[str] = None) -> Dict[str, Any]:
        """
        Generate meal recommendations
        
        Args:
            target_calories: Target calories for the day
            dietary_restrictions: List of foods to restrict
            preferred_foods: List of preferred foods
            exclude_foods: List of foods to exclude
            
        Returns:
            Meal plan dictionary
        """
        # Distribute calories: 25% breakfast, 35% lunch, 40% dinner
        breakfast_target = target_calories * 0.25
        lunch_target = target_calories * 0.35
        dinner_target = target_calories * 0.40
        
        # Inisialisasi dengan fallback untuk berjaga-jaga
        breakfast = self._get_fallback_meal('breakfast')
        lunch = self._get_fallback_meal('lunch')
        dinner = self._get_fallback_meal('dinner')
        
        # Get breakfast options
        breakfast_options = self.get_foods_for_meal(
            meal_type='breakfast', 
            target_calories=breakfast_target,
            foods_count=5, 
            dietary_restrictions=dietary_restrictions,
            preferred_foods=preferred_foods,
            exclude_foods=exclude_foods
        )
        
        # Get lunch options
        lunch_options = self.get_foods_for_meal(
            meal_type='lunch', 
            target_calories=lunch_target,
            foods_count=5, 
            dietary_restrictions=dietary_restrictions,
            preferred_foods=preferred_foods,
            exclude_foods=exclude_foods
        )
        
        # Get dinner options
        dinner_options = self.get_foods_for_meal(
            meal_type='dinner', 
            target_calories=dinner_target,
            foods_count=5, 
            dietary_restrictions=dietary_restrictions,
            preferred_foods=preferred_foods,
            exclude_foods=exclude_foods
        )
        
        # Coba dapatkan makanan dengan kriteria yang dilonggarkan jika opsi tidak cukup
        if not breakfast_options:
            min_calories = breakfast_target * 0.6
            max_calories = breakfast_target * 1.4
            breakfast_options = self.get_foods_for_meal(
                meal_type='breakfast', 
                target_calories=breakfast_target,
                foods_count=5,
                min_calories=min_calories,
                max_calories=max_calories,
                dietary_restrictions=None,  # Hilangkan pembatasan
                exclude_foods=exclude_foods
            )
            if not breakfast_options:
                breakfast_options = [self._get_fallback_meal('breakfast')]
        
        if not lunch_options:
            min_calories = lunch_target * 0.6
            max_calories = lunch_target * 1.4
            lunch_options = self.get_foods_for_meal(
                meal_type='lunch', 
                target_calories=lunch_target,
                foods_count=5,
                min_calories=min_calories,
                max_calories=max_calories,
                dietary_restrictions=None,  # Hilangkan pembatasan
                exclude_foods=exclude_foods
            )
            if not lunch_options:
                lunch_options = [self._get_fallback_meal('lunch')]
                
        if not dinner_options:
            min_calories = dinner_target * 0.6
            max_calories = dinner_target * 1.4
            dinner_options = self.get_foods_for_meal(
                meal_type='dinner', 
                target_calories=dinner_target,
                foods_count=5,
                min_calories=min_calories,
                max_calories=max_calories,
                dietary_restrictions=None,  # Hilangkan pembatasan
                exclude_foods=exclude_foods
            )
            if not dinner_options:
                dinner_options = [self._get_fallback_meal('dinner')]
        
        # Sort by proximity to target calories
        sorted_breakfast = sorted(breakfast_options, key=lambda x: abs(x.get('calories', 0) - breakfast_target))
        sorted_lunch = sorted(lunch_options, key=lambda x: abs(x.get('calories', 0) - lunch_target))
        sorted_dinner = sorted(dinner_options, key=lambda x: abs(x.get('calories', 0) - dinner_target))
        
        # Take the top 3 options (or fewer if not enough) and randomly select one with some randomness
        import random
        breakfast_pool = sorted_breakfast[:min(3, len(sorted_breakfast))]
        lunch_pool = sorted_lunch[:min(3, len(sorted_lunch))]
        dinner_pool = sorted_dinner[:min(3, len(sorted_dinner))]
        
        # Random selection with preference for variety
        breakfast = random.choice(breakfast_pool)
        lunch = random.choice(lunch_pool) 
        dinner = random.choice(dinner_pool)
        
        # Calculate total calories
        total_calories = breakfast.get('calories', 0) + lunch.get('calories', 0) + dinner.get('calories', 0)
        
        return {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'total_calories': total_calories,
            'target_calories': int(target_calories)
        }
    
    def recommend_activities(self, calories_to_burn: float, 
                            user_preferences: List[str] = None,
                            exclude_activities: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate activity recommendations
        
        Args:
            calories_to_burn: Target calories to burn
            user_preferences: List of preferred activities
            exclude_activities: List of activities to exclude
            
        Returns:
            List of activity recommendations
        """
        recommendations = []
        
        # Filter out excluded activities
        available_activities = self.activities_data
        if exclude_activities:
            exclude_set = set(a.lower() for a in exclude_activities)
            available_activities = [
                a for a in available_activities 
                if a['name'].lower() not in exclude_set
            ]
        
        # Prioritize user preferences if available
        if user_preferences:
            pref_set = set(p.lower() for p in user_preferences)
            preferred = [a for a in available_activities if a['name'].lower() in pref_set]
            
            # Add preferred activities first
            for activity in preferred:
                duration_hours = calories_to_burn / activity['calories_per_hour']
                duration_minutes = duration_hours * 60
                
                # Only recommend activities with reasonable duration (15-120 minutes)
                if 15 <= duration_minutes <= 120:
                    recommendations.append({
                        'name': activity['name'],
                        'duration_minutes': round(duration_minutes),
                        'calories_burned': round(calories_to_burn),
                        'intensity': activity['intensity']
                    })
        
        # Fill with other activities if needed
        if len(recommendations) < 3:
            remaining = [a for a in available_activities if not any(r['name'] == a['name'] for r in recommendations)]
            random.shuffle(remaining)
            
            for activity in remaining:
                duration_hours = calories_to_burn / activity['calories_per_hour']
                duration_minutes = duration_hours * 60
                
                if 15 <= duration_minutes <= 120:
                    recommendations.append({
                        'name': activity['name'],
                        'duration_minutes': round(duration_minutes),
                        'calories_burned': round(calories_to_burn),
                        'intensity': activity['intensity']
                    })
                
                if len(recommendations) >= 5:  # Limit to 5 recommendations
                    break
        
        return recommendations
    
    def get_user_history(self, user_id: int) -> Dict[str, Any]:
        """
        Get user recommendation history
        
        Args:
            user_id: User ID
            
        Returns:
            User history dictionary
        """
        if user_id in self.user_history:
            return self.user_history[user_id]
        
        # Default empty history
        return {
            'foods_eaten': defaultdict(int),
            'activities_done': defaultdict(int),
            'days_completed': 0,
            'days_failed': 0
        }
    
    def update_user_history(self, user_id: int, 
                            day_data: Dict[str, Any],
                            completed: bool) -> None:
        """
        Update user recommendation history
        
        Args:
            user_id: User ID
            day_data: Day recommendation data
            completed: Whether the day was completed
        """
        if user_id not in self.user_history:
            self.user_history[user_id] = {
                'foods_eaten': defaultdict(int),
                'activities_done': defaultdict(int),
                'days_completed': 0,
                'days_failed': 0
            }
        
        history = self.user_history[user_id]
        
        # Update food history
        if completed:
            history['foods_eaten'][day_data.get('breakfast', {}).get('name', '')] += 1
            history['foods_eaten'][day_data.get('lunch', {}).get('name', '')] += 1
            history['foods_eaten'][day_data.get('dinner', {}).get('name', '')] += 1
            
            # Update activity history
            for activity in day_data.get('activities', []):
                history['activities_done'][activity.get('name', '')] += 1
            
            history['days_completed'] += 1
        else:
            history['days_failed'] += 1
    
    def get_user_food_preferences(self, user_id: int) -> List[str]:
        """
        Get user food preferences based on history
        
        Args:
            user_id: User ID
            
        Returns:
            List of preferred foods
        """
        if user_id not in self.user_history:
            return []
        
        foods_eaten = self.user_history[user_id]['foods_eaten']
        
        # Sort by frequency and return top 5
        return [food for food, _ in sorted(
            foods_eaten.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]]
    
    def get_user_activity_preferences(self, user_id: int) -> List[str]:
        """
        Get user activity preferences based on history
        
        Args:
            user_id: User ID
            
        Returns:
            List of preferred activities
        """
        if user_id not in self.user_history:
            return []
        
        activities_done = self.user_history[user_id]['activities_done']
        
        # Sort by frequency and return top 3
        return [activity for activity, _ in sorted(
            activities_done.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]]
    
    def generate_daily_recommendation(self, user_profile: Dict[str, Any],
                                     user_id: Optional[int] = None,
                                     day_in_plan: Optional[int] = None,
                                     plan_length: Optional[int] = 30,
                                     previous_days: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate a complete daily recommendation
        
        Args:
            user_profile: User profile data
            user_id: Optional user ID for history
            day_in_plan: Day number in the plan (for dynamic adjustment)
            plan_length: Length of the plan in days
            previous_days: List of previous day recommendations and adherence
            
        Returns:
            Daily recommendation dictionary
        """
        # Calculate BMR and TDEE
        bmr = self.calculate_bmr(
            user_profile['weight'],
            user_profile['height'],
            user_profile['age'],
            user_profile['gender']
        )
        
        tdee = self.calculate_tdee(bmr, user_profile['activity_level'])
        
        # Parse dietary restrictions
        dietary_restrictions = []
        if user_profile.get('dietary_restrictions'):
            try:
                dietary_restrictions = json.loads(user_profile['dietary_restrictions'])
            except:
                dietary_restrictions = []
        
        # Calculate target calories
        if day_in_plan and previous_days and day_in_plan > 1:
            # Dynamic adjustment based on adherence to previous days
            base_target = self.calculate_target_calories(
                user_profile['weight'],
                user_profile.get('goal_weight', user_profile['weight']),
                tdee,
                timeframe=plan_length,
                gender=user_profile['gender']
            )
            
            # Count successful days
            successful_days = sum(1 for day in previous_days if day.get('completed', False))
            
            # Adjust target based on adherence
            target_calories = self.adjust_target_calories_for_missed_days(
                base_target,
                user_profile['weight'],
                user_profile.get('goal_weight', user_profile['weight']),
                day_in_plan - 1,  # Days passed
                successful_days,
                plan_length - day_in_plan + 1,  # Days remaining
                tdee,
                gender=user_profile['gender']
            )
        else:
            # Regular calculation for first day or no history
            target_calories = self.calculate_target_calories(
                user_profile['weight'],
                user_profile.get('goal_weight', user_profile['weight']),
                tdee,
                timeframe=plan_length,
                gender=user_profile['gender']
            )
        
        # Get food preferences if user_id is provided
        exclude_foods = []
        food_preferences = []
        if user_id:
            # Track recently eaten foods to avoid repetition
            if previous_days:
                recent_days = previous_days[-3:]  # Last 3 days
                for day in recent_days:
                    exclude_foods.extend([
                        day.get('breakfast', {}).get('name', ''),
                        day.get('lunch', {}).get('name', ''),
                        day.get('dinner', {}).get('name', '')
                    ])
                exclude_foods = [f for f in exclude_foods if f]
            
            # Get user preferences
            food_preferences = self.get_user_food_preferences(user_id)
        
        # Generate meal recommendations
        meals = self.recommend_meals(
            target_calories,
            dietary_restrictions,
            food_preferences,
            exclude_foods
        )
        
        # Calculate calories to burn
        calories_to_burn = max(0, tdee - target_calories)
        if calories_to_burn < 100:
            calories_to_burn = 200  # Minimum activity for health
        
        # Get activity preferences if user_id is provided
        activity_preferences = []
        if user_id:
            activity_preferences = self.get_user_activity_preferences(user_id)
        
        # Exclude recent activities to prevent boredom
        exclude_activities = []
        if previous_days:
            recent_activities = []
            for day in previous_days[-2:]:  # Last 2 days
                day_activities = day.get('activities', [])
                recent_activities.extend([a.get('name', '') for a in day_activities])
            
            exclude_activities = [a for a in recent_activities if a]
        
        # Generate activity recommendations
        activities = self.recommend_activities(
            calories_to_burn,
            activity_preferences,
            exclude_activities
        )
        
        return {
            'meals': meals,
            'activities': activities,
            'user_stats': {
                'bmr': round(bmr),
                'tdee': round(tdee),
                'target_calories': round(target_calories),
                'calories_to_burn': round(calories_to_burn)
            }
        }
    
    def regenerate_meal(self, meal_type: str, target_calories: float, dietary_restrictions: List[str] = None, exclude_previous: str = None) -> Dict[str, Any]:
        """Regenerate specific meal (breakfast, lunch, dinner)"""
        if meal_type not in ['breakfast', 'lunch', 'dinner']:
            raise ValueError("meal_type must be 'breakfast', 'lunch', or 'dinner'")
        
        # Get a list of exclude foods
        exclude_foods = [exclude_previous] if exclude_previous and exclude_previous != "Rekomendasikan makanan lain" else []
        
        # Coba dapatkan makanan dengan kriteria awal (rentang kalori yang lebih ketat)
        meal_options = self.get_foods_for_meal(
            meal_type,
            target_calories,
            foods_count=5,  # Get 5 options to increase variety
            dietary_restrictions=dietary_restrictions,
            exclude_foods=exclude_foods
        )
        
        # Jika tidak menemukan makanan, coba longgarkan batasan kalori
        if not meal_options:
            # Perluas rentang kalori (+/- 40%)
            min_calories = target_calories * 0.6
            max_calories = target_calories * 1.4
            
            meal_options = self.get_foods_for_meal(
                meal_type,
                target_calories,
                foods_count=5,
                min_calories=min_calories,
                max_calories=max_calories,
                dietary_restrictions=dietary_restrictions,
                exclude_foods=exclude_foods
            )
            
            # Jika masih tidak menemukan, coba hilangkan batasan pantangan makanan
            if not meal_options and dietary_restrictions:
                meal_options = self.get_foods_for_meal(
                    meal_type,
                    target_calories,
                    foods_count=5,
                    min_calories=min_calories,
                    max_calories=max_calories,
                    exclude_foods=exclude_foods
                )
        
        # Jika masih belum ada opsi, gunakan fallback
        if not meal_options:
            return self._get_fallback_meal(meal_type)
            
        # Select a random option from the top matches for more variety
        import random
        selected_meal = random.choice(meal_options[:3]) if len(meal_options) >= 3 else meal_options[0]
        
        return selected_meal
    
    def regenerate_activities(self, 
                             calories_to_burn: float, 
                             exclude_previous: List[str] = None) -> List[Dict[str, Any]]:
        """
        Regenerate activity recommendations
        
        Args:
            calories_to_burn: Target calories to burn
            exclude_previous: Previous activities to exclude
            
        Returns:
            New activity recommendations
        """
        return self.recommend_activities(calories_to_burn, exclude_activities=exclude_previous)
    
    def generate_weekly_plan(self, 
                            user_profile: Dict[str, Any],
                            user_id: Optional[int] = None,
                            days: int = 7) -> List[Dict[str, Any]]:
        """
        Generate a weekly meal plan
        
        Args:
            user_profile: User profile data
            user_id: Optional user ID for preferences
            days: Number of days to generate
            
        Returns:
            List of daily recommendations
        """
        plan = []
        
        for day in range(1, days + 1):
            # Generate recommendation for each day
            day_plan = self.generate_daily_recommendation(
                user_profile, 
                user_id=user_id,
                day_in_plan=day,
                plan_length=days,
                previous_days=plan
            )
            
            plan.append(day_plan)
        
        return plan
    
    def generate_monthly_plan(self,
                             user_profile: Dict[str, Any],
                             user_id: Optional[int] = None,
                             days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate a monthly meal plan
        
        Args:
            user_profile: User profile data
            user_id: Optional user ID for preferences
            days: Number of days to generate
            
        Returns:
            List of daily recommendations
        """
        # This leverages the same logic as weekly plan but for more days
        return self.generate_weekly_plan(user_profile, user_id, days)
    
    def _get_fallback_meal(self, meal_type: str = None):
        """Get a fallback meal when no suitable option is found"""
        # Gunakan makanan default yang sesuai dengan tipe makanan
        if meal_type == 'breakfast':
            default_meals = [
                {'name': 'Nasi Uduk dengan Ayam Goreng', 'calories': 420, 'protein': 18, 'carbs': 55, 'fat': 14},
                {'name': 'Bubur Ayam Spesial', 'calories': 380, 'protein': 15, 'carbs': 50, 'fat': 10},
                {'name': 'Roti Bakar dengan Selai dan Susu', 'calories': 350, 'protein': 12, 'carbs': 45, 'fat': 12}
            ]
        elif meal_type == 'lunch':
            default_meals = [
                {'name': 'Nasi dengan Ayam Bakar dan Lalapan', 'calories': 580, 'protein': 30, 'carbs': 65, 'fat': 18},
                {'name': 'Mie Goreng Spesial', 'calories': 550, 'protein': 20, 'carbs': 70, 'fat': 20},
                {'name': 'Nasi dengan Ikan Bakar dan Sayur Asem', 'calories': 520, 'protein': 25, 'carbs': 60, 'fat': 15}
            ]
        elif meal_type == 'dinner':
            default_meals = [
                {'name': 'Nasi dengan Ayam Penyet dan Lalapan', 'calories': 520, 'protein': 28, 'carbs': 55, 'fat': 16},
                {'name': 'Nasi dengan Pecel Lele dan Sambal', 'calories': 480, 'protein': 25, 'carbs': 55, 'fat': 15},
                {'name': 'Sup Ayam dengan Sayuran', 'calories': 380, 'protein': 22, 'carbs': 40, 'fat': 10}
            ]
        elif meal_type == 'snack':
            default_meals = [
                {'name': 'Pisang dan Yogurt', 'calories': 180, 'protein': 5, 'carbs': 35, 'fat': 2},
                {'name': 'Roti Panggang dengan Selai', 'calories': 200, 'protein': 6, 'carbs': 30, 'fat': 5},
                {'name': 'Kacang Panggang', 'calories': 160, 'protein': 8, 'carbs': 8, 'fat': 12}
            ]
        else:
            default_meals = [
                {'name': 'Nasi dengan Telur dan Sayur', 'calories': 400, 'protein': 15, 'carbs': 50, 'fat': 12},
                {'name': 'Sandwich Isi Telur dan Sayur', 'calories': 350, 'protein': 15, 'carbs': 40, 'fat': 12},
                {'name': 'Mie Rebus dengan Sayuran', 'calories': 420, 'protein': 12, 'carbs': 65, 'fat': 10}
            ]
        
        # Pilih makanan acak dari daftar
        import random
        meal = random.choice(default_meals)
        
        # Tambahkan informasi meal_type
        meal['meal_type'] = meal_type or 'unknown'
        
        return meal 