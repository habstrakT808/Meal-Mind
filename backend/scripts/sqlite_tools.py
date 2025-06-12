#!/usr/bin/env python
"""
SQLite utility tools for MealMind application.
Provides backup and restore functionality for the SQLite database.
"""
import os
import sys
import argparse
import shutil
import datetime
from pathlib import Path

# Add parent directory to path to import app modules if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='MealMind SQLite Database Utility')
    parser.add_argument('action', choices=['backup', 'restore'], help='Action to perform')
    parser.add_argument('--backup-file', help='Path to backup file (for restore action)')
    parser.add_argument('--output-dir', default='backups', help='Directory to store backups')
    return parser.parse_args()

def backup_sqlite():
    """Backup SQLite database to the backups folder."""
    # Default database path
    sqlite_db_path = os.path.join('instance', 'mealmind_dev.db')
    
    if not os.path.exists(sqlite_db_path):
        print(f"Error: SQLite database not found at {sqlite_db_path}")
        return False
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.getcwd(), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp for the backup file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"mealmind_sqlite_{timestamp}.db")
    
    try:
        # Copy the database file
        shutil.copy2(sqlite_db_path, backup_file)
        print(f"Backup berhasil dibuat: {backup_file}")
        return True
    except Exception as e:
        print(f"Error saat backup database: {e}")
        return False

def restore_sqlite(backup_file):
    """Restore SQLite database from a backup file."""
    if not os.path.exists(backup_file):
        print(f"Error: Backup file {backup_file} tidak ditemukan")
        return False
    
    # Target database path
    sqlite_db_path = os.path.join('instance', 'mealmind_dev.db')
    
    try:
        # Backup existing database first (just in case)
        if os.path.exists(sqlite_db_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_backup = os.path.join('instance', f"mealmind_dev_{timestamp}.db.bak")
            print(f"Backup database saat ini ke {temp_backup}")
            shutil.copy2(sqlite_db_path, temp_backup)
        
        # Copy backup file to database location
        print(f"Memulihkan database dari {backup_file}...")
        shutil.copy2(backup_file, sqlite_db_path)
        
        print("Database berhasil dipulihkan!")
        return True
    except Exception as e:
        print(f"Error saat memulihkan database: {e}")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    if args.action == 'backup':
        success = backup_sqlite()
    elif args.action == 'restore':
        if not args.backup_file:
            print("Error: --backup-file is required for restore action")
            return 1
        success = restore_sqlite(args.backup_file)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 