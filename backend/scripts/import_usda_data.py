#!/usr/bin/env python
"""
USDA Food Data Import Script

This script downloads and processes food data from the USDA FoodData 
Central database and imports it into our application's database.
"""

import os
import sys
import argparse
import requests
import zipfile
import json
import csv
import io
from pathlib import Path
import logging
import time
from datetime import datetime

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.food_database import USDAFoodDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('usda_import.log'), logging.StreamHandler()]
)
logger = logging.getLogger('usda_import')

# USDA FoodData Central download URLs
DOWNLOAD_URLS = {
    'foundation': 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2025-04-24.zip',
    'sr_legacy': 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip',
    'branded': 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_branded_food_json_2025-04-24.zip',
    'survey': 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_survey_food_json_2024-10-31.zip'
}

def download_file(url, output_dir):
    """Download a file from the given URL to the output directory"""
    try:
        start_time = time.time()
        logger.info(f"Downloading {url}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract filename from URL
        filename = os.path.basename(url)
        output_path = os.path.join(output_dir, filename)
        
        # Write the file
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Print progress
                    done = downloaded / total_size * 100 if total_size > 0 else 0
                    print(f"\rDownloading: {done:.2f}% ({downloaded / 1024 / 1024:.1f}MB)", end='')
        
        elapsed = time.time() - start_time
        print(f"\nDownloaded {output_path} in {elapsed:.1f} seconds")
        return output_path
    
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return None

def extract_zip(zip_path, output_dir):
    """Extract a zip file to the output directory"""
    try:
        logger.info(f"Extracting {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        return True
    
    except Exception as e:
        logger.error(f"Error extracting zip file: {e}")
        return False

def process_foundation_foods(json_path, food_db):
    """Process foundation foods from the JSON file"""
    try:
        logger.info(f"Processing foundation foods from {json_path}")
        with open(json_path, 'r') as file:
            foods = json.load(file)
        
        count = 0
        for food in foods:
            try:
                # Extract basic food information
                food_data = {
                    'fdc_id': food.get('fdcId'),
                    'name': food.get('description'),
                    'category': food.get('foodCategory', {}).get('description', ''),
                    'data_type': 'Foundation',
                }
                
                # Extract nutrients
                for nutrient in food.get('foodNutrients', []):
                    nutrient_id = nutrient.get('nutrient', {}).get('id')
                    nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                    amount = nutrient.get('amount', 0)
                    
                    if 'protein' in nutrient_name:
                        food_data['protein'] = amount
                    elif 'carbohydrate' in nutrient_name and 'total' in nutrient_name:
                        food_data['carbs'] = amount
                    elif 'total lipid' in nutrient_name or ('fat' in nutrient_name and 'total' in nutrient_name):
                        food_data['fat'] = amount
                    elif 'energy' in nutrient_name:
                        food_data['calories'] = amount
                    elif 'fiber' in nutrient_name and 'total' in nutrient_name:
                        food_data['fiber'] = amount
                    elif 'sugar' in nutrient_name and 'total' in nutrient_name:
                        food_data['sugar'] = amount
                    elif 'sodium' in nutrient_name:
                        food_data['sodium'] = amount
                
                # Save to database
                if 'calories' in food_data and 'protein' in food_data and 'carbs' in food_data and 'fat' in food_data:
                    food_db._save_food_to_db(food_data)
                    count += 1
                    
                    if count % 100 == 0:
                        print(f"\rProcessed {count} foods", end='')
            
            except Exception as e:
                logger.warning(f"Error processing foundation food: {e}")
                continue
        
        print(f"\nSuccessfully processed {count} foundation foods")
        return count
    
    except Exception as e:
        logger.error(f"Error processing foundation foods: {e}")
        return 0

def process_sr_legacy_foods(json_path, food_db):
    """Process SR Legacy foods from the JSON file"""
    try:
        logger.info(f"Processing SR Legacy foods from {json_path}")
        with open(json_path, 'r') as file:
            foods = json.load(file)
        
        count = 0
        for food in foods:
            try:
                # Extract basic food information
                food_data = {
                    'fdc_id': food.get('fdcId'),
                    'name': food.get('description'),
                    'category': food.get('foodCategory', {}).get('description', ''),
                    'data_type': 'SR Legacy',
                }
                
                # Extract nutrients
                for nutrient in food.get('foodNutrients', []):
                    nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                    amount = nutrient.get('amount', 0)
                    
                    if 'protein' in nutrient_name:
                        food_data['protein'] = amount
                    elif 'carbohydrate' in nutrient_name and 'total' in nutrient_name:
                        food_data['carbs'] = amount
                    elif 'total lipid' in nutrient_name or ('fat' in nutrient_name and 'total' in nutrient_name):
                        food_data['fat'] = amount
                    elif 'energy' in nutrient_name:
                        food_data['calories'] = amount
                    elif 'fiber' in nutrient_name and 'total' in nutrient_name:
                        food_data['fiber'] = amount
                    elif 'sugar' in nutrient_name and 'total' in nutrient_name:
                        food_data['sugar'] = amount
                    elif 'sodium' in nutrient_name:
                        food_data['sodium'] = amount
                
                # Skip if missing required nutrients
                if 'calories' in food_data and 'protein' in food_data and 'carbs' in food_data and 'fat' in food_data:
                    food_db._save_food_to_db(food_data)
                    count += 1
                    
                    if count % 100 == 0:
                        print(f"\rProcessed {count} SR Legacy foods", end='')
            
            except Exception as e:
                logger.warning(f"Error processing SR Legacy food: {e}")
                continue
        
        print(f"\nSuccessfully processed {count} SR Legacy foods")
        return count
    
    except Exception as e:
        logger.error(f"Error processing SR Legacy foods: {e}")
        return 0

def process_branded_foods(json_path, food_db, limit=10000):
    """Process branded foods from the JSON file (with limit due to large size)"""
    try:
        logger.info(f"Processing branded foods from {json_path} (limit: {limit})")
        count = 0
        
        # Branded foods file is very large, so process it incrementally
        with open(json_path, 'r') as file:
            # The file begins with a [ character
            char = file.read(1)
            if char != '[':
                logger.error("Invalid JSON format for branded foods")
                return 0
            
            # Process each food item
            while count < limit:
                # Try to read and parse a single food item
                try:
                    food_json = ""
                    braces = 0
                    in_quotes = False
                    escape_next = False
                    
                    # Simple JSON parser to find a complete food item
                    while True:
                        char = file.read(1)
                        if not char:  # End of file
                            break
                        
                        food_json += char
                        
                        if escape_next:
                            escape_next = False
                        elif char == '\\':
                            escape_next = True
                        elif char == '"' and not escape_next:
                            in_quotes = not in_quotes
                        elif not in_quotes:
                            if char == '{':
                                braces += 1
                            elif char == '}':
                                braces -= 1
                                if braces == 0:
                                    break
                    
                    if not char:  # End of file
                        break
                    
                    # Remove trailing comma if present
                    if food_json.endswith(','):
                        food_json = food_json[:-1]
                    
                    # Parse the food item
                    food = json.loads(food_json)
                    
                    # Extract basic food information
                    food_data = {
                        'fdc_id': food.get('fdcId'),
                        'name': food.get('description', ''),
                        'category': food.get('brandedFoodCategory', ''),
                        'data_type': 'Branded',
                    }
                    
                    # Extract serving size
                    serving_size = food.get('servingSize')
                    serving_unit = food.get('servingSizeUnit')
                    if serving_size:
                        food_data['serving_size'] = serving_size
                        food_data['serving_unit'] = serving_unit
                    
                    # Extract nutrients
                    for nutrient in food.get('foodNutrients', []):
                        nutrient_name = nutrient.get('nutrientName', '').lower()
                        amount = nutrient.get('value', 0)
                        
                        if 'protein' in nutrient_name:
                            food_data['protein'] = amount
                        elif 'carbohydrate' in nutrient_name or 'carbs' in nutrient_name:
                            food_data['carbs'] = amount
                        elif ('fat' in nutrient_name and 'total' in nutrient_name) or 'total fat' in nutrient_name:
                            food_data['fat'] = amount
                        elif 'energy' in nutrient_name or 'calorie' in nutrient_name:
                            food_data['calories'] = amount
                        elif 'fiber' in nutrient_name:
                            food_data['fiber'] = amount
                        elif 'sugar' in nutrient_name:
                            food_data['sugar'] = amount
                        elif 'sodium' in nutrient_name:
                            food_data['sodium'] = amount
                    
                    # Skip if missing required nutrients
                    if 'calories' in food_data and 'protein' in food_data and 'carbs' in food_data and 'fat' in food_data:
                        food_db._save_food_to_db(food_data)
                        count += 1
                        
                        if count % 100 == 0:
                            print(f"\rProcessed {count} branded foods", end='')
                
                except json.JSONDecodeError:
                    # Skip invalid JSON
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error processing branded food: {e}")
                    continue
        
        print(f"\nSuccessfully processed {count} branded foods")
        return count
    
    except Exception as e:
        logger.error(f"Error processing branded foods: {e}")
        return 0

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

def main():
    parser = argparse.ArgumentParser(description='Import USDA food data')
    parser.add_argument('--api-key', help='USDA FoodData Central API key')
    parser.add_argument('--db-path', default='food_database.db', help='Output database path')
    parser.add_argument('--data-dir', default='data', help='Directory for downloaded files')
    parser.add_argument('--food-types', default='foundation,sr_legacy,branded',
                       help='Comma-separated list of food types to import (foundation,sr_legacy,branded)')
    parser.add_argument('--limit', type=int, default=10000, help='Limit for branded foods (default: 10000)')
    parser.add_argument('--skip-download', action='store_true', help='Skip downloading files (use existing)')
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    data_dir = os.path.abspath(args.data_dir)
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize food database
    food_db = USDAFoodDatabase(db_path=args.db_path, api_key=args.api_key)
    
    # Parse food types
    food_types = [t.strip() for t in args.food_types.split(',')]
    
    total_foods = 0
    
    # Process each food type
    for food_type in food_types:
        if food_type not in DOWNLOAD_URLS:
            logger.warning(f"Unknown food type: {food_type}")
            continue
        
        download_url = DOWNLOAD_URLS[food_type]
        zip_filename = os.path.basename(download_url)
        zip_path = os.path.join(data_dir, zip_filename)
        
        # Download file if needed
        if not args.skip_download or not os.path.exists(zip_path):
            zip_path = download_file(download_url, data_dir)
            if not zip_path:
                continue
        
        # Extract zip file
        if not extract_zip(zip_path, data_dir):
            continue
        
        # Process the data
        if food_type == 'foundation':
            json_path = os.path.join(data_dir, 'FoodData_Central_foundation_food.json')
            count = process_foundation_foods(json_path, food_db)
        elif food_type == 'sr_legacy':
            json_path = os.path.join(data_dir, 'sr_legacy_food.json')
            count = process_sr_legacy_foods(json_path, food_db)
        elif food_type == 'branded':
            json_path = os.path.join(data_dir, 'branded_food.json')
            count = process_branded_foods(json_path, food_db, args.limit)
        else:
            count = 0
        
        total_foods += count
    
    # Map foods to meal types
    map_foods_to_meal_types(food_db)
    
    logger.info(f"Import complete. Total foods imported: {total_foods}")
    
    # Close database connection
    food_db.close()

if __name__ == '__main__':
    main() 