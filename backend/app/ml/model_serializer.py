import pickle
import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('model_serializer.log'), logging.StreamHandler()]
)
logger = logging.getLogger('model_serializer')

class ModelSerializer:
    """
    Class untuk menyimpan dan memuat model ML secara terpisah
    agar backend lebih ringan
    """
    
    @staticmethod
    def save_model(model, model_path):
        """
        Menyimpan model ML ke file
        
        Args:
            model: Model ML yang akan disimpan
            model_path: Path untuk menyimpan model
        """
        try:
            # Buat direktori jika belum ada
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Simpan model dengan joblib (lebih efisien untuk model sklearn)
            joblib.dump(model, model_path, compress=3)
            logger.info(f"Model berhasil disimpan ke {model_path}")
            return True
        except Exception as e:
            logger.error(f"Gagal menyimpan model: {str(e)}")
            return False
    
    @staticmethod
    def load_model(model_path):
        """
        Memuat model ML dari file
        
        Args:
            model_path: Path file model yang akan dimuat
            
        Returns:
            Model ML yang dimuat
        """
        try:
            if os.path.exists(model_path):
                # Muat model dengan joblib
                model = joblib.load(model_path)
                logger.info(f"Model berhasil dimuat dari {model_path}")
                return model
            else:
                logger.warning(f"File model tidak ditemukan di {model_path}")
                return None
        except Exception as e:
            logger.error(f"Gagal memuat model: {str(e)}")
            return None
    
    @staticmethod
    def initialize_vectorizer(food_data=None, model_path="models/tfidf_vectorizer.joblib"):
        """
        Inisialisasi atau muat TfidfVectorizer
        
        Args:
            food_data: Data makanan untuk inisialisasi vectorizer jika perlu
            model_path: Path untuk menyimpan/memuat model
            
        Returns:
            TfidfVectorizer yang sudah diinisialisasi
        """
        # Coba muat model yang sudah ada
        vectorizer = ModelSerializer.load_model(model_path)
        
        # Jika tidak ada, buat model baru
        if vectorizer is None and food_data is not None:
            vectorizer = TfidfVectorizer(stop_words='english')
            # Fit vectorizer dengan data makanan
            food_texts = [f"{food.get('name', '')} {food.get('description', '')}" for food in food_data]
            vectorizer.fit(food_texts)
            # Simpan model baru
            ModelSerializer.save_model(vectorizer, model_path)
        
        return vectorizer 