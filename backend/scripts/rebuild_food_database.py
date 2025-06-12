#!/usr/bin/env python
"""
Script untuk membuat ulang food database tanpa harus menghapus file lama terlebih dahulu.
"""

import os
import sys
import sqlite3

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.food_database import USDAFoodDatabase
from scripts.initialize_food_database import initialize_database

def rebuild_database():
    """Rebuild the database by clearing all tables and reinitializing"""
    db_path = 'food_database.db'
    
    # Open database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Mengosongkan tabel pada database...")
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop all tables
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # Don't drop the SQLite internal table
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Membuat ulang struktur database dan mengisi data...")
    
    # Reinitialize database
    food_db = USDAFoodDatabase(db_path=db_path)
    food_db._initialize_database()
    food_db.close()
    
    # Use the initialize_database function to populate data
    count = initialize_database(db_path=db_path)
    
    print(f"Database berhasil dibuat ulang dengan {count} item makanan")

if __name__ == "__main__":
    rebuild_database() 