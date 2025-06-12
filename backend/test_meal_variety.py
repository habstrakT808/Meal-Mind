#!/usr/bin/env python
"""
Script untuk menguji variasi makanan dan memastikan tidak ada fallback message
"Tidak ada pilihan lain sesuai pantangan"
"""

import sys
import os
import json
import random

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine
from app.ml.food_database import USDAFoodDatabase

def test_meal_variety():
    """Test meal variety and ensure no fallback messages"""
    print("===== TESTING MEAL VARIETY =====")
    
    # Sample user profiles for testing
    test_profiles = [
        {
            "weight": 70,
            "height": 170,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate",
            "goal_weight": 65,
            "dietary_restrictions": "[]"  # Empty restrictions
        },
        {
            "weight": 55,
            "height": 160,
            "age": 25,
            "gender": "female",
            "activity_level": "light",
            "goal_weight": 52,
            "dietary_restrictions": "[\"vegetarian\"]"  # Vegetarian
        }
    ]
    
    # Create recommendation engine
    engine = AdvancedRecommendationEngine()
    
    # Test each profile
    for i, profile in enumerate(test_profiles):
        print(f"\nProfile {i+1}: {profile['gender']}, {profile['age']} years old, {profile['dietary_restrictions']} restrictions")
        
        # Parse dietary restrictions
        try:
            dietary_restrictions = json.loads(profile['dietary_restrictions'])
        except:
            dietary_restrictions = []
        
        # Generate 5 recommendations for each meal type
        meal_types = ['breakfast', 'lunch', 'dinner']
        for meal_type in meal_types:
            print(f"\n{meal_type.upper()}:")
            
            # Target calories based on typical distribution
            if meal_type == 'breakfast':
                target_calories = 400
            elif meal_type == 'lunch':
                target_calories = 600
            else:
                target_calories = 700
                
            # Get 5 sets of meals
            meals = []
            for _ in range(5):
                exclude_previous = [meal['name'] for meal in meals] if meals else []
                meal_options = engine.get_foods_for_meal(
                    meal_type, 
                    target_calories, 
                    foods_count=3,
                    dietary_restrictions=dietary_restrictions,
                    exclude_foods=exclude_previous
                )
                
                if not meal_options:
                    print("  ERROR: No meal options found!")
                    continue
                    
                meal = random.choice(meal_options)
                meals.append(meal)
                
                # Check for fallback message
                if "Tidak ada pilihan lain sesuai pantangan" in meal['name']:
                    print(f"  ERROR: Found fallback message in meal: {meal['name']}")
                    
                print(f"  - {meal['name']} ({meal['calories']} kcal)")
            
            # Check unique meals
            unique_meals = set(meal['name'] for meal in meals)
            print(f"  Unique meals: {len(unique_meals)}/{len(meals)}")
    
    print("\n===== FOOD DATABASE STATS =====")
    
    # Check food database statistics
    db = USDAFoodDatabase()
    try:
        # Count total foods
        food_count = db.count_foods()
        print(f"Total foods in database: {food_count}")
        
        # Count by meal type
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            count = db.count_foods_by_meal_type(meal_type)
            print(f"Foods for {meal_type}: {count}")
    finally:
        db.close()

if __name__ == "__main__":
    test_meal_variety() 