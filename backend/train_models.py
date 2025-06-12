#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script untuk melatih dan menyimpan model ML secara terpisah
sehingga backend bisa lebih ringan dengan hanya memuat model yang sudah dilatih.
"""

import os
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Import app modules - need to set up path first
import sys
from pathlib import Path

# Get the absolute path of the current script
current_dir = Path(__file__).resolve().parent
# Add the parent directory to sys.path
sys.path.append(str(current_dir))

from app import create_app
from app.ml.food_database import USDAFoodDatabase
from app.ml.model_serializer import ModelSerializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('model_training.log'), logging.StreamHandler()]
)
logger = logging.getLogger('model_training')

def train_and_save_vectorizer():
    """
    Melatih dan menyimpan TF-IDF Vectorizer untuk rekomendasi makanan
    """
    logger.info("Memulai pelatihan TF-IDF Vectorizer...")
    
    # Pastikan direktori models ada
    os.makedirs("models", exist_ok=True)
    model_path = "models/tfidf_vectorizer.joblib"
    
    # Buat instance food database
    food_db = USDAFoodDatabase(db_path='food_database.db')
    
    # Pastikan database sudah terisi data
    food_db.seed_default_foods()
    
    try:
        # Ambil data makanan
        foods = food_db.get_all_foods(limit=2000)
        logger.info(f"Menggunakan {len(foods)} data makanan untuk pelatihan vectorizer")
    except Exception as e:
        logger.error(f"Gagal mengambil data makanan: {str(e)}")
        # Gunakan data makanan dummy jika gagal mengambil dari database
        foods = [
            {'name': 'Nasi Putih', 'description': 'Nasi putih matang'},
            {'name': 'Ayam Goreng', 'description': 'Ayam goreng renyah'},
            {'name': 'Sayur Bayam', 'description': 'Sayur bayam rebus segar'},
            {'name': 'Ikan Bakar', 'description': 'Ikan bakar bumbu rica rica'},
            {'name': 'Telur Dadar', 'description': 'Telur dadar dengan bawang dan wortel'},
        ]
        logger.info(f"Menggunakan {len(foods)} data makanan dummy untuk pelatihan vectorizer")
    
    # Siapkan teks untuk vectorizer
    food_texts = []
    for food in foods:
        name = food.get('name', '')
        description = food.get('description', '')
        text = f"{name} {description}"
        food_texts.append(text)
    
    # Buat dan latih vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer.fit(food_texts)
    
    # Simpan model
    ModelSerializer.save_model(vectorizer, model_path)
    
    logger.info(f"TF-IDF Vectorizer berhasil dilatih dan disimpan ke {model_path}")
    return vectorizer

def main():
    """
    Fungsi utama untuk melatih semua model
    """
    logger.info("Memulai pelatihan model...")
    
    # Buat app context
    app = create_app()
    with app.app_context():
        # Train TF-IDF Vectorizer
        vectorizer = train_and_save_vectorizer()
        
        # Tambahkan pelatihan model lain di sini jika diperlukan
    
    logger.info("Pelatihan model selesai!")

if __name__ == "__main__":
    main() 