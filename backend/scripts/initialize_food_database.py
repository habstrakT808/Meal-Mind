#!/usr/bin/env python3
"""
Food Database Initialization Script

This script initializes the food database with a basic dataset for use
when the USDA API is not available or for more limited deployments.
"""

import os
import sys
import pandas as pd
import logging
import csv
from pathlib import Path

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.food_database import USDAFoodDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('food_db_init.log'), logging.StreamHandler()]
)
logger = logging.getLogger('food_db_init')

# Sample food data for different meal types
BREAKFAST_FOODS = [
    {'name': 'Nasi Gudeg + Telur', 'category': 'Breakfast', 'calories': 450, 'protein': 15, 'carbs': 65, 'fat': 12},
    {'name': 'Roti Bakar + Selai + Susu', 'category': 'Breakfast', 'calories': 320, 'protein': 12, 'carbs': 45, 'fat': 10},
    {'name': 'Bubur Ayam + Kerupuk', 'category': 'Breakfast', 'calories': 380, 'protein': 18, 'carbs': 55, 'fat': 8},
    {'name': 'Nasi Uduk + Ayam Goreng', 'category': 'Breakfast', 'calories': 520, 'protein': 25, 'carbs': 60, 'fat': 18},
    {'name': 'Lontong Sayur + Telur', 'category': 'Breakfast', 'calories': 350, 'protein': 14, 'carbs': 50, 'fat': 9},
    {'name': 'Oatmeal dengan Pisang', 'category': 'Breakfast', 'calories': 280, 'protein': 10, 'carbs': 50, 'fat': 5},
    {'name': 'Pancake dengan Madu', 'category': 'Breakfast', 'calories': 350, 'protein': 8, 'carbs': 55, 'fat': 12},
    {'name': 'Nasi Goreng', 'category': 'Breakfast', 'calories': 400, 'protein': 12, 'carbs': 65, 'fat': 15},
    {'name': 'Sereal dengan Susu', 'category': 'Breakfast', 'calories': 300, 'protein': 10, 'carbs': 60, 'fat': 5},
    {'name': 'Telur Dadar + Roti', 'category': 'Breakfast', 'calories': 320, 'protein': 22, 'carbs': 25, 'fat': 18},
    {'name': 'Sandwich Telur + Keju', 'category': 'Breakfast', 'calories': 380, 'protein': 20, 'carbs': 30, 'fat': 18},
    {'name': 'Yogurt dengan Granola', 'category': 'Breakfast', 'calories': 250, 'protein': 12, 'carbs': 35, 'fat': 8},
    {'name': 'Alpukat Tumbuk + Roti', 'category': 'Breakfast', 'calories': 350, 'protein': 8, 'carbs': 25, 'fat': 25},
    {'name': 'Pisang Goreng + Teh', 'category': 'Breakfast', 'calories': 280, 'protein': 4, 'carbs': 55, 'fat': 10},
    {'name': 'Ketupat Sayur', 'category': 'Breakfast', 'calories': 400, 'protein': 10, 'carbs': 70, 'fat': 12}
]

LUNCH_FOODS = [
    {'name': 'Nasi + Ayam Bakar + Lalapan', 'category': 'Lunch', 'calories': 650, 'protein': 35, 'carbs': 70, 'fat': 20},
    {'name': 'Nasi + Rendang + Sayur', 'category': 'Lunch', 'calories': 720, 'protein': 30, 'carbs': 75, 'fat': 25},
    {'name': 'Nasi + Ikan Bakar + Tumis Kangkung', 'category': 'Lunch', 'calories': 580, 'protein': 32, 'carbs': 65, 'fat': 18},
    {'name': 'Nasi + Soto Ayam + Kerupuk', 'category': 'Lunch', 'calories': 620, 'protein': 28, 'carbs': 70, 'fat': 22},
    {'name': 'Nasi + Gado-gado + Kerupuk', 'category': 'Lunch', 'calories': 550, 'protein': 20, 'carbs': 68, 'fat': 20},
    {'name': 'Nasi + Pecel + Tempe', 'category': 'Lunch', 'calories': 520, 'protein': 20, 'carbs': 65, 'fat': 18},
    {'name': 'Mie Goreng + Telur', 'category': 'Lunch', 'calories': 580, 'protein': 20, 'carbs': 80, 'fat': 22},
    {'name': 'Nasi + Sayur Asem + Tempe Goreng', 'category': 'Lunch', 'calories': 500, 'protein': 15, 'carbs': 75, 'fat': 15},
    {'name': 'Nasi + Rawon + Telur', 'category': 'Lunch', 'calories': 600, 'protein': 25, 'carbs': 70, 'fat': 18},
    {'name': 'Nasi + Sate Ayam + Sambal Kacang', 'category': 'Lunch', 'calories': 680, 'protein': 30, 'carbs': 75, 'fat': 22},
    {'name': 'Bakso Kuah + Mie', 'category': 'Lunch', 'calories': 550, 'protein': 25, 'carbs': 65, 'fat': 15},
    {'name': 'Nasi + Gulai Ikan + Sayur', 'category': 'Lunch', 'calories': 580, 'protein': 28, 'carbs': 60, 'fat': 20},
    {'name': 'Nasi + Ayam Pop + Sayur', 'category': 'Lunch', 'calories': 620, 'protein': 35, 'carbs': 65, 'fat': 18},
    {'name': 'Nasi + Tahu Telor + Sambal', 'category': 'Lunch', 'calories': 500, 'protein': 22, 'carbs': 65, 'fat': 16},
    {'name': 'Nasi + Capcay Seafood', 'category': 'Lunch', 'calories': 520, 'protein': 25, 'carbs': 60, 'fat': 15}
]

DINNER_FOODS = [
    {'name': 'Nasi + Pecel Lele + Lalapan', 'category': 'Dinner', 'calories': 480, 'protein': 25, 'carbs': 55, 'fat': 15},
    {'name': 'Sandwich + Telur + Susu', 'category': 'Dinner', 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 16},
    {'name': 'Nasi + Ayam Geprek + Sayur', 'category': 'Dinner', 'calories': 520, 'protein': 30, 'carbs': 58, 'fat': 18},
    {'name': 'Mie Ayam + Pangsit + Bakso', 'category': 'Dinner', 'calories': 450, 'protein': 22, 'carbs': 60, 'fat': 12},
    {'name': 'Nasi + Tempe Goreng + Sayur Asem', 'category': 'Dinner', 'calories': 380, 'protein': 16, 'carbs': 55, 'fat': 10},
    {'name': 'Nasi + Tahu Telur + Oseng Kangkung', 'category': 'Dinner', 'calories': 420, 'protein': 20, 'carbs': 50, 'fat': 18},
    {'name': 'Nasi + Ikan Asin + Terong Balado', 'category': 'Dinner', 'calories': 400, 'protein': 15, 'carbs': 60, 'fat': 12},
    {'name': 'Nasi + Sup Ayam', 'category': 'Dinner', 'calories': 350, 'protein': 25, 'carbs': 45, 'fat': 8},
    {'name': 'Ketoprak + Teh Manis', 'category': 'Dinner', 'calories': 370, 'protein': 18, 'carbs': 50, 'fat': 10},
    {'name': 'Bihun Goreng + Kerupuk', 'category': 'Dinner', 'calories': 400, 'protein': 15, 'carbs': 65, 'fat': 12},
    {'name': 'Nasi + Ayam Rica-Rica + Sayur', 'category': 'Dinner', 'calories': 480, 'protein': 28, 'carbs': 50, 'fat': 16},
    {'name': 'Nasi + Cakalang Fufu + Tumis Kangkung', 'category': 'Dinner', 'calories': 450, 'protein': 30, 'carbs': 48, 'fat': 14},
    {'name': 'Nasi + Telur Balado + Sup', 'category': 'Dinner', 'calories': 380, 'protein': 18, 'carbs': 55, 'fat': 12},
    {'name': 'Lontong + Gulai Sayur', 'category': 'Dinner', 'calories': 400, 'protein': 12, 'carbs': 65, 'fat': 12},
    {'name': 'Nasi + Tongkol Balado + Tumis Kacang', 'category': 'Dinner', 'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 16}
]

SNACK_FOODS = [
    {'name': 'Roti Kering + Susu', 'category': 'Snack', 'calories': 200, 'protein': 8, 'carbs': 25, 'fat': 8},
    {'name': 'Pisang + Yogurt', 'category': 'Snack', 'calories': 180, 'protein': 5, 'carbs': 35, 'fat': 2},
    {'name': 'Kacang Tanah Panggang', 'category': 'Snack', 'calories': 220, 'protein': 10, 'carbs': 10, 'fat': 16},
    {'name': 'Keripik Singkong', 'category': 'Snack', 'calories': 150, 'protein': 2, 'carbs': 20, 'fat': 8},
    {'name': 'Tempe Mendoan', 'category': 'Snack', 'calories': 180, 'protein': 8, 'carbs': 15, 'fat': 10},
    {'name': 'Ubi Rebus', 'category': 'Snack', 'calories': 120, 'protein': 2, 'carbs': 28, 'fat': 0},
    {'name': 'Telur Rebus', 'category': 'Snack', 'calories': 80, 'protein': 6, 'carbs': 1, 'fat': 5},
    {'name': 'Roti Panggang + Selai', 'category': 'Snack', 'calories': 140, 'protein': 4, 'carbs': 25, 'fat': 3},
    {'name': 'Jeruk Segar', 'category': 'Snack', 'calories': 70, 'protein': 1, 'carbs': 18, 'fat': 0},
    {'name': 'Keripik Tempe', 'category': 'Snack', 'calories': 160, 'protein': 10, 'carbs': 14, 'fat': 8}
]

WESTERN_FOODS = [
    {'name': 'Burger Sapi + Kentang Goreng', 'category': 'Western', 'calories': 750, 'protein': 30, 'carbs': 65, 'fat': 40},
    {'name': 'Pizza Keju', 'category': 'Western', 'calories': 800, 'protein': 35, 'carbs': 90, 'fat': 35},
    {'name': 'Pasta Carbonara', 'category': 'Western', 'calories': 650, 'protein': 25, 'carbs': 80, 'fat': 30},
    {'name': 'Caesar Salad dengan Ayam', 'category': 'Western', 'calories': 420, 'protein': 35, 'carbs': 15, 'fat': 22},
    {'name': 'Sandwich Tuna', 'category': 'Western', 'calories': 450, 'protein': 28, 'carbs': 40, 'fat': 18},
    {'name': 'Steak Daging Sapi + Kentang', 'category': 'Western', 'calories': 650, 'protein': 40, 'carbs': 30, 'fat': 35},
    {'name': 'Fish & Chips', 'category': 'Western', 'calories': 700, 'protein': 32, 'carbs': 70, 'fat': 35},
    {'name': 'Burrito Bowl', 'category': 'Western', 'calories': 550, 'protein': 25, 'carbs': 65, 'fat': 20}
]

HEALTHY_FOODS = [
    {'name': 'Salad Sayur + Ayam Panggang', 'category': 'Healthy', 'calories': 350, 'protein': 30, 'carbs': 20, 'fat': 15},
    {'name': 'Bowl Quinoa + Salmon', 'category': 'Healthy', 'calories': 420, 'protein': 35, 'carbs': 40, 'fat': 12},
    {'name': 'Smoothie Bowl Buah', 'category': 'Healthy', 'calories': 320, 'protein': 12, 'carbs': 55, 'fat': 8},
    {'name': 'Oatmeal + Kacang + Buah', 'category': 'Healthy', 'calories': 380, 'protein': 15, 'carbs': 60, 'fat': 10},
    {'name': 'Wrap Hummus + Sayur', 'category': 'Healthy', 'calories': 340, 'protein': 12, 'carbs': 45, 'fat': 12},
    {'name': 'Buddha Bowl', 'category': 'Healthy', 'calories': 450, 'protein': 20, 'carbs': 55, 'fat': 15},
    {'name': 'Tumis Sayur + Tofu', 'category': 'Healthy', 'calories': 280, 'protein': 18, 'carbs': 25, 'fat': 12},
    {'name': 'Salad Kacang + Alpukat', 'category': 'Healthy', 'calories': 320, 'protein': 15, 'carbs': 25, 'fat': 20}
]

def map_foods_to_meal_types(food_db):
    """Map foods to appropriate meal types based on heuristics"""
    try:
        logger.info("Mapping foods to meal types")
        
        # Connect to the database
        conn = food_db._get_connection()
        cursor = conn.cursor()
        
        # Get all foods
        cursor.execute("SELECT id, name, category FROM foods")
        foods = cursor.fetchall()
        
        breakfast_keywords = [
            'breakfast', 'cereal', 'oatmeal', 'pancake', 'waffle', 'egg', 
            'toast', 'bagel', 'muffin', 'yogurt', 'milk', 'bread',
            'coffee', 'tea', 'juice', 'morning'
        ]
        
        lunch_keywords = [
            'sandwich', 'soup', 'salad', 'wrap', 'burger', 'pasta',
            'lunch', 'noon', 'midday', 'roll', 'bowl', 'taco',
            'burrito', 'noon meal'
        ]
        
        dinner_keywords = [
            'dinner', 'steak', 'fish', 'chicken', 'pork', 'beef',
            'roast', 'curry', 'evening', 'supper', 'casserole',
            'stew', 'hearty', 'nighttime'
        ]
        
        snack_keywords = [
            'snack', 'chip', 'cracker', 'nut', 'seed', 'bar',
            'popcorn', 'pretzel', 'candy', 'chocolate', 'cookie',
            'between meal', 'trail mix', 'dried fruit', 'jerky'
        ]
        
        # Indonesian food keywords
        indo_breakfast = [
            'bubur', 'nasi uduk', 'nasi kuning', 'lontong', 'ketupat',
            'roti', 'serabi', 'kue', 'gudeg', 'kolak'
        ]
        
        indo_lunch = [
            'nasi', 'bakso', 'soto', 'gado-gado', 'pecel', 'rendang',
            'ayam', 'sate', 'ikan', 'sayur', 'sambal', 'tumis'
        ]
        
        indo_dinner = [
            'lele', 'bakar', 'goreng', 'geprek', 'rica', 'teri',
            'tahu', 'tempe', 'terong', 'lalapan', 'sup'
        ]
        
        indo_snack = [
            'keripik', 'kerupuk', 'kacang', 'gorengan', 'cireng',
            'bakwan', 'pisang', 'tempe mendoan', 'tahu gejrot'
        ]
        
        # Combine keywords
        breakfast_keywords.extend(indo_breakfast)
        lunch_keywords.extend(indo_lunch)
        dinner_keywords.extend(indo_dinner)
        snack_keywords.extend(indo_snack)
        
        count = 0
        mappings = 0
        
        for food in foods:
            food_id = food['id']
            name = food['name'].lower() if food['name'] else ''
            category = food['category'].lower() if food['category'] else ''
            
            # Check if the food matches any meal type
            meal_types = []
            
            for keyword in breakfast_keywords:
                if keyword.lower() in name or keyword.lower() in category:
                    meal_types.append('breakfast')
                    break
            
            for keyword in lunch_keywords:
                if keyword.lower() in name or keyword.lower() in category:
                    meal_types.append('lunch')
                    break
            
            for keyword in dinner_keywords:
                if keyword.lower() in name or keyword.lower() in category:
                    meal_types.append('dinner')
                    break
            
            for keyword in snack_keywords:
                if keyword.lower() in name or keyword.lower() in category:
                    meal_types.append('snack')
                    break
            
            # Add mappings to database
            for meal_type in meal_types:
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO food_meal_types (food_id, meal_type_id)
                        SELECT ?, id FROM meal_types WHERE name = ?
                        """,
                        (food_id, meal_type)
                    )
                    mappings += 1
                except Exception as e:
                    logger.warning(f"Error mapping food to meal type: {e}")
            
            count += 1
            if count % 1000 == 0:
                print(f"\rProcessed {count} foods, created {mappings} mappings", end='')
        
        conn.commit()
        print(f"\nCreated {mappings} meal type mappings for {count} foods")
        return mappings
    
    except Exception as e:
        logger.error(f"Error mapping foods to meal types: {e}")
        return 0

def create_food_csv(output_path='food_data.csv'):
    """Create a CSV file with food data"""
    # Combine all food categories
    all_foods = (BREAKFAST_FOODS + LUNCH_FOODS + DINNER_FOODS + 
                SNACK_FOODS + WESTERN_FOODS + HEALTHY_FOODS)
    
    # Write to CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'category', 'calories', 'protein', 'carbs', 'fat']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for food in all_foods:
                writer.writerow(food)
        
        logger.info(f"Created food CSV with {len(all_foods)} entries at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating food CSV: {e}")
        return None

def initialize_database(db_path='food_database.db', csv_path=None):
    """Initialize the food database with sample data"""
    try:
        # Create the food database
        food_db = USDAFoodDatabase(db_path=db_path)
        
        # Create CSV if not provided
        if csv_path is None:
            csv_path = create_food_csv()
        
        if csv_path and os.path.exists(csv_path):
            # Import data from CSV
            count = food_db.import_from_csv(csv_path)
            logger.info(f"Imported {count} foods from CSV")
            
            # Map foods to meal types
            mappings = map_foods_to_meal_types(food_db)
            logger.info(f"Created {mappings} meal type mappings")
            
            return count
        else:
            # Just seed default foods
            success = food_db.seed_default_foods()
            count = 0
            if success:
                logger.info("Seeded default foods")
                count = 24  # Default number of foods
            return count
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 0
        
    finally:
        if 'food_db' in locals():
            food_db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize food database')
    parser.add_argument('--db-path', default='food_database.db', help='Database path')
    parser.add_argument('--csv-path', help='Path to CSV file with food data')
    args = parser.parse_args()
    
    count = initialize_database(args.db_path, args.csv_path)
    print(f"Initialized database with {count} food items") 