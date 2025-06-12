#!/usr/bin/env python
"""
Test script to verify meal recommendations are diverse and working correctly
"""

import sys
import os
import json
from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine

# Sample user profile for testing
TEST_PROFILE = {
    "weight": 70,
    "height": 170,
    "age": 30,
    "gender": "male",
    "activity_level": "moderate",
    "goal_weight": 65,
    "dietary_restrictions": "[]"  # Empty restrictions
}

def test_recommendation_variety():
    """Test that the recommendation engine generates varied meals"""
    print("Testing meal recommendation variety...")
    
    # Initialize recommendation engine
    engine = AdvancedRecommendationEngine()
    
    # Generate 5 recommendations
    recommendations = []
    for i in range(5):
        rec = engine.generate_daily_recommendation(TEST_PROFILE)
        recommendations.append(rec)
    
    # Check variety
    breakfast_names = [r['meals']['breakfast']['name'] for r in recommendations]
    lunch_names = [r['meals']['lunch']['name'] for r in recommendations]
    dinner_names = [r['meals']['dinner']['name'] for r in recommendations]
    
    print("\nBreakfast variety:")
    for i, name in enumerate(breakfast_names):
        print(f"  Day {i+1}: {name}")
    
    print("\nLunch variety:")
    for i, name in enumerate(lunch_names):
        print(f"  Day {i+1}: {name}")
    
    print("\nDinner variety:")
    for i, name in enumerate(dinner_names):
        print(f"  Day {i+1}: {name}")
    
    # Check if there are any repetitions
    breakfast_unique = len(set(breakfast_names))
    lunch_unique = len(set(lunch_names))
    dinner_unique = len(set(dinner_names))
    
    print("\nUnique meals:")
    print(f"  Breakfast: {breakfast_unique} out of 5")
    print(f"  Lunch: {lunch_unique} out of 5")
    print(f"  Dinner: {dinner_unique} out of 5")
    
    # Test with dietary restrictions
    print("\nTesting with dietary restrictions...")
    
    # Add some restrictions
    restricted_profile = TEST_PROFILE.copy()
    restricted_profile["dietary_restrictions"] = '["ayam", "daging"]'  # Restrict chicken and meat
    
    rec_with_restrictions = engine.generate_daily_recommendation(restricted_profile)
    
    print("\nRecommendation with restrictions (no chicken or meat):")
    print(f"  Breakfast: {rec_with_restrictions['meals']['breakfast']['name']}")
    print(f"  Lunch: {rec_with_restrictions['meals']['lunch']['name']}")
    print(f"  Dinner: {rec_with_restrictions['meals']['dinner']['name']}")

if __name__ == "__main__":
    # Add the parent directory to the path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run the test
    test_recommendation_variety() 