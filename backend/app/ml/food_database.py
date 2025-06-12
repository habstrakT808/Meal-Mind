import os
import json
import csv
import requests
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('food_database.log'), logging.StreamHandler()]
)
logger = logging.getLogger('food_database')

class USDAFoodDatabase:
    """
    A class to manage the USDA food database for the meal recommendation system.
    This handles downloading, processing, and querying food data from USDA FoodData Central.
    """
    
    def __init__(self, db_path='food_database.db', api_key=None):
        """
        Initialize the USDA food database handler
        
        Args:
            db_path: Path to SQLite database file
            api_key: USDA FoodData Central API key
        """
        self.db_path = db_path
        self.api_key = api_key or os.environ.get('USDA_API_KEY')
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.foods_cache = {}
        self._conn = None
        
        # Create database if it doesn't exist
        self._initialize_database()
        
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create foods table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY,
            fdc_id TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            fiber REAL,
            sugar REAL,
            sodium REAL,
            serving_size REAL,
            serving_unit TEXT,
            data_source TEXT,
            data_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create nutrients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrients (
            id INTEGER PRIMARY KEY,
            food_id INTEGER,
            nutrient_id INTEGER,
            name TEXT,
            amount REAL,
            unit TEXT,
            FOREIGN KEY (food_id) REFERENCES foods(id),
            UNIQUE(food_id, nutrient_id)
        )
        ''')
        
        # Create food categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            description TEXT
        )
        ''')
        
        # Create meal types table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_types (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
        ''')
        
        # Create food_meal_types mapping table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_meal_types (
            id INTEGER PRIMARY KEY,
            food_id INTEGER,
            meal_type_id INTEGER,
            FOREIGN KEY (food_id) REFERENCES foods(id),
            FOREIGN KEY (meal_type_id) REFERENCES meal_types(id),
            UNIQUE(food_id, meal_type_id)
        )
        ''')
        
        # Insert default meal types if they don't exist
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        for meal_type in meal_types:
            cursor.execute(
                "INSERT OR IGNORE INTO meal_types (name) VALUES (?)",
                (meal_type,)
            )
        
        conn.commit()
    
    def _get_connection(self):
        """Get SQLite database connection"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        """Close the database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
            
    def count_foods(self) -> int:
        """Get the total number of foods in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM foods")
        return cursor.fetchone()[0]
        
    def count_foods_by_meal_type(self, meal_type: str) -> int:
        """Get the number of foods for a specific meal type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT f.id)
            FROM foods f
            JOIN food_meal_types fmt ON f.id = fmt.food_id
            WHERE fmt.meal_type = ?
        """, (meal_type,))
        return cursor.fetchone()[0]
    
    def search_food(self, query: str, data_type: List[str] = None, page_size: int = 20) -> List[Dict]:
        """
        Search for foods by name using the USDA API
        
        Args:
            query: Food name to search for
            data_type: List of data types to filter by
                (e.g. ["Foundation", "SR Legacy", "Survey (FNDDS)", "Branded"])
            page_size: Number of results to return
            
        Returns:
            List of food items matching the search query
        """
        if not self.api_key:
            logger.error("API key is required to search for foods")
            return []
        
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size
        }
        
        if data_type:
            params["dataType"] = data_type
        
        try:
            response = requests.get(f"{self.base_url}/foods/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information from each food item
            foods = []
            for item in data.get('foods', []):
                food = {
                    'fdc_id': item.get('fdcId'),
                    'name': item.get('description'),
                    'category': item.get('foodCategory'),
                    'data_type': item.get('dataType'),
                }
                
                # Extract nutrients
                nutrients = {}
                for nutrient in item.get('foodNutrients', []):
                    nutrient_name = nutrient.get('nutrientName', '').lower()
                    if 'protein' in nutrient_name:
                        nutrients['protein'] = nutrient.get('value', 0)
                    elif 'carbohydrate' in nutrient_name:
                        nutrients['carbs'] = nutrient.get('value', 0)
                    elif 'fat' in nutrient_name and 'total' in nutrient_name:
                        nutrients['fat'] = nutrient.get('value', 0)
                    elif 'energy' in nutrient_name:
                        nutrients['calories'] = nutrient.get('value', 0)
                
                food.update(nutrients)
                foods.append(food)
            
            return foods
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for food: {e}")
            return []
    
    def get_food_details(self, fdc_id: str) -> Dict:
        """
        Get detailed information for a specific food by its FDC ID
        
        Args:
            fdc_id: USDA FoodData Central ID
            
        Returns:
            Detailed food information dictionary
        """
        if not self.api_key:
            logger.error("API key is required to get food details")
            return {}
        
        # Check cache first
        if fdc_id in self.foods_cache:
            return self.foods_cache[fdc_id]
        
        # Check database
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM foods WHERE fdc_id = ?", 
            (fdc_id,)
        )
        row = cursor.fetchone()
        
        if row:
            # Convert row to dictionary
            food = {key: row[key] for key in row.keys()}
            
            # Get nutrients
            cursor.execute(
                "SELECT * FROM nutrients WHERE food_id = ?",
                (row['id'],)
            )
            nutrients = cursor.fetchall()
            food['nutrients'] = [{key: nutrient[key] for key in nutrient.keys()} 
                               for nutrient in nutrients]
            
            self.foods_cache[fdc_id] = food
            return food
        
        # If not in database, fetch from API
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(f"{self.base_url}/food/{fdc_id}", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            food = {
                'fdc_id': data.get('fdcId'),
                'name': data.get('description'),
                'category': data.get('foodCategory', {}).get('description'),
                'data_type': data.get('dataType'),
                'serving_size': None,
                'serving_unit': None
            }
            
            # Get serving size if available
            portions = data.get('foodPortions', [])
            if portions:
                food['serving_size'] = portions[0].get('amount')
                food['serving_unit'] = portions[0].get('measureUnit', {}).get('name')
            
            # Extract nutrients
            nutrients = []
            for nutrient in data.get('foodNutrients', []):
                nutrient_data = {
                    'id': nutrient.get('nutrient', {}).get('id'),
                    'name': nutrient.get('nutrient', {}).get('name'),
                    'amount': nutrient.get('amount'),
                    'unit': nutrient.get('nutrient', {}).get('unitName')
                }
                nutrients.append(nutrient_data)
                
                # Extract macronutrients into the main food dictionary
                nutrient_name = nutrient_data['name'].lower() if nutrient_data['name'] else ''
                
                if 'protein' in nutrient_name:
                    food['protein'] = nutrient_data['amount']
                elif 'carbohydrate' in nutrient_name and 'total' in nutrient_name:
                    food['carbs'] = nutrient_data['amount']
                elif 'fat' in nutrient_name and 'total' in nutrient_name:
                    food['fat'] = nutrient_data['amount']
                elif 'energy' in nutrient_name:
                    food['calories'] = nutrient_data['amount']
                elif 'fiber' in nutrient_name and 'total' in nutrient_name:
                    food['fiber'] = nutrient_data['amount']
                elif 'sugar' in nutrient_name and 'total' in nutrient_name:
                    food['sugar'] = nutrient_data['amount']
                elif 'sodium' in nutrient_name:
                    food['sodium'] = nutrient_data['amount']
            
            food['nutrients'] = nutrients
            
            # Save to database for future queries
            self._save_food_to_db(food)
            
            self.foods_cache[fdc_id] = food
            return food
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting food details: {e}")
            return {}
    
    def _save_food_to_db(self, food: Dict):
        """Save food data to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO foods 
                (fdc_id, name, category, calories, protein, carbs, fat, 
                fiber, sugar, sodium, serving_size, serving_unit, data_source, data_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (fdc_id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                calories = excluded.calories,
                protein = excluded.protein,
                carbs = excluded.carbs,
                fat = excluded.fat,
                fiber = excluded.fiber,
                sugar = excluded.sugar,
                sodium = excluded.sodium,
                serving_size = excluded.serving_size,
                serving_unit = excluded.serving_unit,
                data_source = excluded.data_source,
                data_type = excluded.data_type
                """,
                (
                    food.get('fdc_id'),
                    food.get('name'),
                    food.get('category'),
                    food.get('calories'),
                    food.get('protein'),
                    food.get('carbs'),
                    food.get('fat'),
                    food.get('fiber'),
                    food.get('sugar'),
                    food.get('sodium'),
                    food.get('serving_size'),
                    food.get('serving_unit'),
                    'USDA',
                    food.get('data_type')
                )
            )
            
            # Get the food ID
            food_id = cursor.lastrowid
            if not food_id:
                cursor.execute(
                    "SELECT id FROM foods WHERE fdc_id = ?",
                    (food.get('fdc_id'),)
                )
                row = cursor.fetchone()
                food_id = row['id']
            
            # Save nutrients
            for nutrient in food.get('nutrients', []):
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO nutrients
                    (food_id, nutrient_id, name, amount, unit)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        food_id,
                        nutrient.get('id'),
                        nutrient.get('name'),
                        nutrient.get('amount'),
                        nutrient.get('unit')
                    )
                )
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving food to database: {e}")
    
    def import_from_csv(self, file_path: str, data_type: str = 'custom') -> int:
        """
        Import food data from a CSV file
        
        Args:
            file_path: Path to CSV file
            data_type: Type of data being imported
            
        Returns:
            Number of records imported
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Basic validation
            required_columns = ['name', 'calories', 'protein', 'carbs', 'fat']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                logger.error(f"Missing required columns: {missing}")
                return 0
            
            conn = self._get_connection()
            count = 0
            
            for _, row in df.iterrows():
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO foods
                        (name, category, calories, protein, carbs, fat,
                        fiber, sugar, sodium, data_source, data_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row['name'],
                            row.get('category', ''),
                            row['calories'],
                            row['protein'],
                            row['carbs'],
                            row['fat'],
                            row.get('fiber', None),
                            row.get('sugar', None),
                            row.get('sodium', None),
                            'CSV Import',
                            data_type
                        )
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"Error importing row: {e}")
            
            conn.commit()
            logger.info(f"Successfully imported {count} foods from CSV")
            return count
            
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return 0
    
    def bulk_download_usda_data(self, data_type: str = 'Foundation') -> bool:
        """
        Download and process bulk USDA data
        
        Args:
            data_type: Type of data to download 
                ('Foundation', 'SR Legacy', 'Survey', 'Branded')
                
        Returns:
            True if successful, False otherwise
        """
        # This method would handle bulk data download
        # Implementation would depend on specific requirements and format
        # of the USDA data files
        logger.warning("Bulk download not yet implemented")
        return False
    
    def get_foods_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """
        Get foods by category
        
        Args:
            category: Food category
            limit: Maximum number of results
            
        Returns:
            List of food items in the category
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM foods WHERE category LIKE ? LIMIT ?",
            (f"%{category}%", limit)
        )
        
        rows = cursor.fetchall()
        return [{key: row[key] for key in row.keys()} for row in rows]
    
    def get_foods_by_meal_type(self, 
                              meal_type: str, 
                              limit: int = 100, 
                              min_calories: float = None, 
                              max_calories: float = None,
                              dietary_restrictions: List[str] = None,
                              exclude_foods: List[str] = None) -> List[Dict]:
        """
        Get foods suitable for a specific meal type with filtering options
        
        Args:
            meal_type: Meal type (breakfast, lunch, dinner, snack)
            limit: Maximum number of results
            min_calories: Minimum calories
            max_calories: Maximum calories
            dietary_restrictions: List of dietary restrictions to avoid
            exclude_foods: List of food names to exclude
            
        Returns:
            List of food items for the meal type
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query_parts = [
            """
            SELECT f.* FROM foods f
            JOIN food_meal_types fmt ON f.id = fmt.food_id
            JOIN meal_types mt ON fmt.meal_type_id = mt.id
            WHERE mt.name = ?
            """
        ]
        params = [meal_type]
        
        # Add calorie filtering
        if min_calories is not None:
            query_parts.append("AND f.calories >= ?")
            params.append(min_calories)
        if max_calories is not None:
            query_parts.append("AND f.calories <= ?")
            params.append(max_calories)
            
        # Add dietary restrictions filtering
        if dietary_restrictions and len(dietary_restrictions) > 0:
            restrictions_conditions = []
            for restriction in dietary_restrictions:
                if restriction:
                    restrictions_conditions.append("f.name NOT LIKE ?")
                    params.append(f"%{restriction}%")
            if restrictions_conditions:
                query_parts.append(f"AND ({' AND '.join(restrictions_conditions)})")
                
        # Add exclude foods filtering
        if exclude_foods and len(exclude_foods) > 0:
            exclude_conditions = []
            for exclude in exclude_foods:
                if exclude:
                    exclude_conditions.append("f.name != ?")
                    params.append(exclude)
            if exclude_conditions:
                query_parts.append(f"AND ({' AND '.join(exclude_conditions)})")
                
        # Add limit
        query_parts.append("LIMIT ?")
        params.append(limit)
        
        # Combine all query parts
        full_query = " ".join(query_parts)
        cursor.execute(full_query, params)
        
        rows = cursor.fetchall()
        result = [{key: row[key] for key in row.keys()} for row in rows]
        
        # If no mappings exist, return foods based on category heuristics
        if not result:
            meal_type_categories = {
                'breakfast': ['Breakfast Foods', 'Cereals', 'Bakery', 'Dairy'],
                'lunch': ['Sandwiches', 'Salads', 'Soups', 'Fast Food'],
                'dinner': ['Meat', 'Poultry', 'Seafood', 'Pasta', 'Rice', 'Vegetables'],
                'snack': ['Snacks', 'Fruits', 'Nuts', 'Seeds', 'Candy']
            }
            
            categories = meal_type_categories.get(meal_type, [])
            if categories:
                query = "SELECT * FROM foods WHERE "
                conditions = []
                params = []
                
                # Category conditions
                category_conditions = []
                for cat in categories:
                    category_conditions.append("category LIKE ?")
                    params.append(f"%{cat}%")
                conditions.append(f"({' OR '.join(category_conditions)})")
                
                # Calorie conditions
                if min_calories is not None:
                    conditions.append("calories >= ?")
                    params.append(min_calories)
                if max_calories is not None:
                    conditions.append("calories <= ?")
                    params.append(max_calories)
                    
                # Dietary restrictions
                if dietary_restrictions and len(dietary_restrictions) > 0:
                    for restriction in dietary_restrictions:
                        if restriction:
                            conditions.append("name NOT LIKE ?")
                            params.append(f"%{restriction}%")
                            
                # Exclude foods
                if exclude_foods and len(exclude_foods) > 0:
                    for exclude in exclude_foods:
                        if exclude:
                            conditions.append("name != ?")
                            params.append(exclude)
                
                query += " AND ".join(conditions) + " LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                result = [{key: row[key] for key in row.keys()} for row in rows]
        
        return result
    
    def get_foods_by_calorie_range(self,
                                  min_calories: float = None,
                                  max_calories: float = None,
                                  limit: int = 100,
                                  dietary_restrictions: List[str] = None,
                                  exclude_foods: List[str] = None) -> List[Dict]:
        """
        Get foods within a calorie range
        
        Args:
            min_calories: Minimum calories
            max_calories: Maximum calories
            limit: Maximum number of results
            dietary_restrictions: List of dietary restrictions to avoid
            exclude_foods: List of food names to exclude
            
        Returns:
            List of food items within calorie range
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query_parts = ["SELECT * FROM foods WHERE 1=1"]
        params = []
        
        # Add calorie filtering
        if min_calories is not None:
            query_parts.append("AND calories >= ?")
            params.append(min_calories)
        if max_calories is not None:
            query_parts.append("AND calories <= ?")
            params.append(max_calories)
            
        # Add dietary restrictions filtering
        if dietary_restrictions and len(dietary_restrictions) > 0:
            for restriction in dietary_restrictions:
                if restriction:
                    query_parts.append("AND name NOT LIKE ?")
                    params.append(f"%{restriction}%")
                
        # Add exclude foods filtering
        if exclude_foods and len(exclude_foods) > 0:
            for exclude in exclude_foods:
                if exclude:
                    query_parts.append("AND name != ?")
                    params.append(exclude)
                
        # Add limit
        query_parts.append("LIMIT ?")
        params.append(limit)
        
        # Combine all query parts
        full_query = " ".join(query_parts)
        cursor.execute(full_query, params)
        
        rows = cursor.fetchall()
        return [{key: row[key] for key in row.keys()} for row in rows]
    
    def add_food(self, food_data: Dict) -> int:
        """
        Add a custom food to the database
        
        Args:
            food_data: Food data dictionary
            
        Returns:
            ID of the newly created food entry
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO foods
                (name, category, calories, protein, carbs, fat,
                fiber, sugar, sodium, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    food_data.get('name'),
                    food_data.get('category', ''),
                    food_data.get('calories', 0),
                    food_data.get('protein', 0),
                    food_data.get('carbs', 0),
                    food_data.get('fat', 0),
                    food_data.get('fiber'),
                    food_data.get('sugar'),
                    food_data.get('sodium'),
                    'Custom'
                )
            )
            
            food_id = cursor.lastrowid
            
            # Associate with meal types if provided
            meal_types = food_data.get('meal_types', [])
            for meal_type in meal_types:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO food_meal_types (food_id, meal_type_id)
                    SELECT ?, id FROM meal_types WHERE name = ?
                    """,
                    (food_id, meal_type)
                )
            
            conn.commit()
            return food_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding food: {e}")
            return 0
    
    def get_random_foods_by_meal_type(self, 
                                     meal_type: str, 
                                     count: int = 10,
                                     min_calories: float = None, 
                                     max_calories: float = None,
                                     dietary_restrictions: List[str] = None,
                                     exclude_foods: List[str] = None) -> List[Dict]:
        """
        Get random foods for a specific meal type with filtering options
        
        Args:
            meal_type: Meal type (breakfast, lunch, dinner, snack)
            count: Number of random foods to return
            min_calories: Minimum calories
            max_calories: Maximum calories
            dietary_restrictions: List of dietary restrictions to avoid
            exclude_foods: List of food names to exclude
            
        Returns:
            List of random food items for the meal type
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query_parts = [
            """
            SELECT f.* FROM foods f
            JOIN food_meal_types fmt ON f.id = fmt.food_id
            JOIN meal_types mt ON fmt.meal_type_id = mt.id
            WHERE mt.name = ?
            """
        ]
        params = [meal_type]
        
        # Add calorie filtering
        if min_calories is not None:
            query_parts.append("AND f.calories >= ?")
            params.append(min_calories)
        if max_calories is not None:
            query_parts.append("AND f.calories <= ?")
            params.append(max_calories)
            
        # Add dietary restrictions filtering
        if dietary_restrictions and len(dietary_restrictions) > 0:
            for restriction in dietary_restrictions:
                if restriction:
                    query_parts.append("AND f.name NOT LIKE ?")
                    params.append(f"%{restriction}%")
                
        # Add exclude foods filtering
        if exclude_foods and len(exclude_foods) > 0:
            for exclude in exclude_foods:
                if exclude:
                    query_parts.append("AND f.name != ?")
                    params.append(exclude)
                
        # Add randomization and limit
        query_parts.append("ORDER BY RANDOM() LIMIT ?")
        params.append(count)
        
        # Combine all query parts
        full_query = " ".join(query_parts)
        cursor.execute(full_query, params)
        
        rows = cursor.fetchall()
        result = [{key: row[key] for key in row.keys()} for row in rows]
        
        # If not enough results, get additional foods based on categories
        if len(result) < count:
            # Calculate how many more foods we need
            remaining = count - len(result)
            
            # IDs we already have
            existing_ids = [food.get('id') for food in result]
            
            meal_type_categories = {
                'breakfast': ['Breakfast', 'Cereal', 'Bakery', 'Dairy'],
                'lunch': ['Sandwich', 'Salad', 'Soup', 'Fast Food'],
                'dinner': ['Meat', 'Poultry', 'Seafood', 'Pasta', 'Rice', 'Vegetable'],
                'snack': ['Snack', 'Fruit', 'Nut', 'Seed', 'Candy']
            }
            
            categories = meal_type_categories.get(meal_type, [])
            if categories:
                query = "SELECT * FROM foods WHERE "
                conditions = []
                params = []
                
                # Category conditions
                category_conditions = []
                for cat in categories:
                    category_conditions.append("category LIKE ?")
                    params.append(f"%{cat}%")
                conditions.append(f"({' OR '.join(category_conditions)})")
                
                # Exclude existing IDs
                if existing_ids:
                    id_placeholders = ','.join(['?'] * len(existing_ids))
                    conditions.append(f"id NOT IN ({id_placeholders})")
                    params.extend(existing_ids)
                
                # Calorie conditions
                if min_calories is not None:
                    conditions.append("calories >= ?")
                    params.append(min_calories)
                if max_calories is not None:
                    conditions.append("calories <= ?")
                    params.append(max_calories)
                    
                # Dietary restrictions
                if dietary_restrictions and len(dietary_restrictions) > 0:
                    for restriction in dietary_restrictions:
                        if restriction:
                            conditions.append("name NOT LIKE ?")
                            params.append(f"%{restriction}%")
                            
                # Exclude foods
                if exclude_foods and len(exclude_foods) > 0:
                    for exclude in exclude_foods:
                        if exclude:
                            conditions.append("name != ?")
                            params.append(exclude)
                
                query += " AND ".join(conditions) + " ORDER BY RANDOM() LIMIT ?"
                params.append(remaining)
                
                cursor.execute(query, params)
                additional_rows = cursor.fetchall()
                result.extend([{key: row[key] for key in row.keys()} for row in additional_rows])
        
        # If still not enough, get random foods
        if len(result) < count:
            # Calculate how many more foods we need
            remaining = count - len(result)
            
            # IDs we already have
            existing_ids = [food.get('id') for food in result]
            
            query_parts = ["SELECT * FROM foods WHERE 1=1"]
            params = []
            
            # Exclude existing IDs
            if existing_ids:
                id_placeholders = ','.join(['?'] * len(existing_ids))
                query_parts.append(f"AND id NOT IN ({id_placeholders})")
                params.extend(existing_ids)
            
            # Calorie conditions
            if min_calories is not None:
                query_parts.append("AND calories >= ?")
                params.append(min_calories)
            if max_calories is not None:
                query_parts.append("AND calories <= ?")
                params.append(max_calories)
                
            # Dietary restrictions
            if dietary_restrictions and len(dietary_restrictions) > 0:
                for restriction in dietary_restrictions:
                    if restriction:
                        query_parts.append("AND name NOT LIKE ?")
                        params.append(f"%{restriction}%")
                        
            # Exclude foods
            if exclude_foods and len(exclude_foods) > 0:
                for exclude in exclude_foods:
                    if exclude:
                        query_parts.append("AND name != ?")
                        params.append(exclude)
            
            query_parts.append("ORDER BY RANDOM() LIMIT ?")
            params.append(remaining)
            
            # Combine all query parts
            full_query = " ".join(query_parts)
            cursor.execute(full_query, params)
            
            additional_rows = cursor.fetchall()
            result.extend([{key: row[key] for key in row.keys()} for row in additional_rows])
        
        return result

    def seed_default_foods(self):
        """Seed the database with default foods if empty"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if foods table is empty
        cursor.execute("SELECT COUNT(*) as count FROM foods")
        row = cursor.fetchone()
        
        if row['count'] > 0:
            return False  # Database already has foods
        
        # Indonesian breakfast foods
        breakfast_foods = [
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
            {'name': 'Ketupat Sayur', 'category': 'Breakfast', 'calories': 400, 'protein': 10, 'carbs': 70, 'fat': 12},
            # Tambahan makanan sarapan
            {'name': 'Burrito Sarapan', 'category': 'Breakfast', 'calories': 420, 'protein': 18, 'carbs': 48, 'fat': 15},
            {'name': 'Bubur Kacang Hijau', 'category': 'Breakfast', 'calories': 320, 'protein': 8, 'carbs': 62, 'fat': 5},
            {'name': 'Sandwich Tuna', 'category': 'Breakfast', 'calories': 380, 'protein': 22, 'carbs': 40, 'fat': 12},
            {'name': 'Mie Goreng Sarapan', 'category': 'Breakfast', 'calories': 410, 'protein': 15, 'carbs': 55, 'fat': 14},
            {'name': 'Nasi Kuning + Telur Balado', 'category': 'Breakfast', 'calories': 450, 'protein': 18, 'carbs': 60, 'fat': 15}
        ]
        
        # Indonesian lunch foods
        lunch_foods = [
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
            {'name': 'Nasi + Capcay Seafood', 'category': 'Lunch', 'calories': 520, 'protein': 25, 'carbs': 60, 'fat': 15},
            # Tambahan makanan makan siang
            {'name': 'Nasi + Bebek Goreng + Sambal', 'category': 'Lunch', 'calories': 750, 'protein': 38, 'carbs': 65, 'fat': 28},
            {'name': 'Nasi + Iga Bakar + Sup', 'category': 'Lunch', 'calories': 680, 'protein': 40, 'carbs': 55, 'fat': 25},
            {'name': 'Nasi + Pindang Tongkol + Tempe', 'category': 'Lunch', 'calories': 560, 'protein': 32, 'carbs': 60, 'fat': 16},
            {'name': 'Nasi + Semur Daging + Sayur', 'category': 'Lunch', 'calories': 630, 'protein': 35, 'carbs': 65, 'fat': 22},
            {'name': 'Nasi + Sop Buntut + Emping', 'category': 'Lunch', 'calories': 670, 'protein': 36, 'carbs': 58, 'fat': 25},
            {'name': 'Nasi + Ayam Betutu + Plecing', 'category': 'Lunch', 'calories': 640, 'protein': 34, 'carbs': 65, 'fat': 20}
        ]
        
        # Indonesian dinner foods
        dinner_foods = [
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
            {'name': 'Nasi + Tongkol Balado + Tumis Kacang', 'category': 'Dinner', 'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 16},
            # Tambahan makanan makan malam
            {'name': 'Nasi + Ayam Taliwang + Plecing', 'category': 'Dinner', 'calories': 510, 'protein': 28, 'carbs': 55, 'fat': 18},
            {'name': 'Nasi + Kakap Asam Manis', 'category': 'Dinner', 'calories': 480, 'protein': 26, 'carbs': 55, 'fat': 16},
            {'name': 'Nasi + Udang Balado + Tumis Terong', 'category': 'Dinner', 'calories': 460, 'protein': 24, 'carbs': 52, 'fat': 15},
            {'name': 'Nasi + Sop Ikan + Tahu Goreng', 'category': 'Dinner', 'calories': 430, 'protein': 25, 'carbs': 50, 'fat': 12},
            {'name': 'Nasi + Sayur Lodeh + Tempe Penyet', 'category': 'Dinner', 'calories': 410, 'protein': 18, 'carbs': 55, 'fat': 14}
        ]

        # Snack foods
        snack_foods = [
            {'name': 'Roti Kering + Susu', 'category': 'Snack', 'calories': 200, 'protein': 8, 'carbs': 25, 'fat': 8},
            {'name': 'Pisang + Yogurt', 'category': 'Snack', 'calories': 180, 'protein': 5, 'carbs': 35, 'fat': 2},
            {'name': 'Kacang Tanah Panggang', 'category': 'Snack', 'calories': 220, 'protein': 10, 'carbs': 10, 'fat': 16},
            {'name': 'Keripik Singkong', 'category': 'Snack', 'calories': 150, 'protein': 2, 'carbs': 20, 'fat': 8},
            {'name': 'Tempe Mendoan', 'category': 'Snack', 'calories': 180, 'protein': 8, 'carbs': 15, 'fat': 10},
            {'name': 'Ubi Rebus', 'category': 'Snack', 'calories': 120, 'protein': 2, 'carbs': 28, 'fat': 0},
            {'name': 'Telur Rebus', 'category': 'Snack', 'calories': 80, 'protein': 6, 'carbs': 1, 'fat': 5},
            {'name': 'Roti Panggang + Selai', 'category': 'Snack', 'calories': 140, 'protein': 4, 'carbs': 25, 'fat': 3},
            {'name': 'Jeruk Segar', 'category': 'Snack', 'calories': 70, 'protein': 1, 'carbs': 18, 'fat': 0},
            {'name': 'Keripik Tempe', 'category': 'Snack', 'calories': 160, 'protein': 10, 'carbs': 14, 'fat': 8},
            # Tambahan makanan ringan
            {'name': 'Risoles', 'category': 'Snack', 'calories': 180, 'protein': 5, 'carbs': 20, 'fat': 10},
            {'name': 'Lemper Ayam', 'category': 'Snack', 'calories': 150, 'protein': 8, 'carbs': 22, 'fat': 5},
            {'name': 'Lumpia Basah', 'category': 'Snack', 'calories': 160, 'protein': 6, 'carbs': 18, 'fat': 8},
            {'name': 'Donat Mini', 'category': 'Snack', 'calories': 200, 'protein': 3, 'carbs': 30, 'fat': 10}
        ]

        # Western foods
        western_foods = [
            {'name': 'Burger Sapi + Kentang Goreng', 'category': 'Western', 'calories': 750, 'protein': 30, 'carbs': 65, 'fat': 40},
            {'name': 'Pizza Keju', 'category': 'Western', 'calories': 800, 'protein': 35, 'carbs': 90, 'fat': 35},
            {'name': 'Pasta Carbonara', 'category': 'Western', 'calories': 650, 'protein': 25, 'carbs': 80, 'fat': 30},
            {'name': 'Caesar Salad dengan Ayam', 'category': 'Western', 'calories': 420, 'protein': 35, 'carbs': 15, 'fat': 22},
            {'name': 'Sandwich Tuna', 'category': 'Western', 'calories': 450, 'protein': 28, 'carbs': 40, 'fat': 18},
            # Tambahan makanan barat
            {'name': 'Lasagna', 'category': 'Western', 'calories': 580, 'protein': 26, 'carbs': 50, 'fat': 30},
            {'name': 'Steak + Kentang Panggang', 'category': 'Western', 'calories': 650, 'protein': 45, 'carbs': 35, 'fat': 32},
            {'name': 'Fish and Chips', 'category': 'Western', 'calories': 700, 'protein': 30, 'carbs': 70, 'fat': 35},
            {'name': 'Burrito Bowl', 'category': 'Western', 'calories': 550, 'protein': 25, 'carbs': 65, 'fat': 20}
        ]

        # Healthy foods
        healthy_foods = [
            {'name': 'Salad Sayur + Ayam Panggang', 'category': 'Healthy', 'calories': 350, 'protein': 30, 'carbs': 20, 'fat': 15},
            {'name': 'Bowl Quinoa + Salmon', 'category': 'Healthy', 'calories': 420, 'protein': 35, 'carbs': 40, 'fat': 12},
            {'name': 'Smoothie Bowl Buah', 'category': 'Healthy', 'calories': 320, 'protein': 12, 'carbs': 55, 'fat': 8},
            {'name': 'Oatmeal + Kacang + Buah', 'category': 'Healthy', 'calories': 380, 'protein': 15, 'carbs': 60, 'fat': 10},
            {'name': 'Wrap Hummus + Sayur', 'category': 'Healthy', 'calories': 340, 'protein': 12, 'carbs': 45, 'fat': 12},
            # Tambahan makanan sehat
            {'name': 'Tofu Scramble + Roti Gandum', 'category': 'Healthy', 'calories': 320, 'protein': 22, 'carbs': 38, 'fat': 10},
            {'name': 'Buddha Bowl dengan Tahu', 'category': 'Healthy', 'calories': 380, 'protein': 18, 'carbs': 50, 'fat': 12},
            {'name': 'Sup Sayur + Ikan Kukus', 'category': 'Healthy', 'calories': 300, 'protein': 25, 'carbs': 30, 'fat': 8},
            {'name': 'Salad Kacang-kacangan', 'category': 'Healthy', 'calories': 350, 'protein': 15, 'carbs': 40, 'fat': 16}
        ]
        
        # Insert all foods
        all_foods = breakfast_foods + lunch_foods + dinner_foods + snack_foods + western_foods + healthy_foods
        for food in all_foods:
            try:
                cursor.execute(
                    """
                    INSERT INTO foods
                    (name, category, calories, protein, carbs, fat, data_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        food['name'],
                        food['category'],
                        food['calories'],
                        food['protein'],
                        food['carbs'],
                        food['fat'],
                        'Default'
                    )
                )
                
                food_id = cursor.lastrowid
                
                # Map to meal type
                meal_type = 'breakfast'
                if 'Lunch' in food['category']:
                    meal_type = 'lunch'
                elif 'Dinner' in food['category']:
                    meal_type = 'dinner'
                elif 'Snack' in food['category']:
                    meal_type = 'snack'
                elif 'Western' in food['category']:
                    # Map western foods to all meal types for more variety
                    western_meal_types = ['breakfast', 'lunch', 'dinner']
                    for wm_type in western_meal_types:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO food_meal_types (food_id, meal_type_id)
                            SELECT ?, id FROM meal_types WHERE name = ?
                            """,
                            (food_id, wm_type)
                        )
                    continue
                elif 'Healthy' in food['category']:
                    # Map healthy foods to all meal types for more variety
                    healthy_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
                    for hm_type in healthy_meal_types:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO food_meal_types (food_id, meal_type_id)
                            SELECT ?, id FROM meal_types WHERE name = ?
                            """,
                            (food_id, hm_type)
                        )
                    continue
                
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO food_meal_types (food_id, meal_type_id)
                    SELECT ?, id FROM meal_types WHERE name = ?
                    """,
                    (food_id, meal_type)
                )
                
            except Exception as e:
                logger.error(f"Error seeding food: {e}")
        
        conn.commit()
        logger.info(f"Seeded {len(all_foods)} default foods")
        return True 

    def get_all_foods(self, limit: int = 1000) -> List[Dict]:
        """
        Get all foods from the database
        
        Args:
            limit: Maximum number of foods to return
            
        Returns:
            List of food items
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, fdc_id, name, category, calories, protein, carbs, fat, 
                   fiber, sugar, sodium, serving_size, serving_unit, data_source, data_type
            FROM foods
            LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        
        foods = []
        for row in cursor.fetchall():
            food = {
                'id': row['id'],
                'fdc_id': row['fdc_id'],
                'name': row['name'],
                'category': row['category'],
                'calories': row['calories'],
                'protein': row['protein'],
                'carbs': row['carbs'],
                'fat': row['fat'],
                'fiber': row['fiber'],
                'sugar': row['sugar'],
                'sodium': row['sodium'],
                'serving_size': row['serving_size'],
                'serving_unit': row['serving_unit'],
                'data_source': row['data_source'],
                'data_type': row['data_type'],
                'description': f"{row['name']} {row['category'] or ''}"
            }
            foods.append(food)
            
        return foods 