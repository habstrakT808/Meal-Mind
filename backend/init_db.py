# backend/init_db.py
import os
import random
from datetime import datetime, timedelta, date

# Mengimpor modul dan objek yang diperlukan
from app import create_app, db
from app.models.user import User, UserProfile
from app.models.food import Food, Activity
from app.models.recommendation import DailyRecommendation, DailyCheckin

def init_db():
    """Inisialisasi database dan masukkan data contoh"""
    app = create_app('development')
    
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()
        
        # Masukkan contoh makanan
        print("Menambahkan contoh makanan...")
        foods = [
            Food(name="Nasi Putih", calories_per_100g=130, protein=2.7, carbs=28, fat=0.3, category="Karbohidrat"),
            Food(name="Ayam Goreng", calories_per_100g=240, protein=27, carbs=0, fat=15, category="Protein"),
            Food(name="Tahu", calories_per_100g=76, protein=8, carbs=1.9, fat=4.8, category="Protein"),
            Food(name="Tempe", calories_per_100g=193, protein=19, carbs=8.7, fat=10.8, category="Protein"),
            Food(name="Sayur Bayam", calories_per_100g=23, protein=2.9, carbs=3.6, fat=0.4, category="Sayuran"),
            Food(name="Pepaya", calories_per_100g=43, protein=0.5, carbs=11, fat=0.3, category="Buah"),
            Food(name="Pisang", calories_per_100g=89, protein=1.1, carbs=22.8, fat=0.3, category="Buah"),
            Food(name="Jeruk", calories_per_100g=47, protein=0.9, carbs=11.8, fat=0.1, category="Buah"),
            Food(name="Telur", calories_per_100g=155, protein=13, carbs=1.1, fat=11, category="Protein"),
            Food(name="Ikan Salmon", calories_per_100g=206, protein=22, carbs=0, fat=13, category="Protein"),
        ]
        db.session.add_all(foods)
        
        # Masukkan contoh aktivitas
        print("Menambahkan contoh aktivitas...")
        activities = [
            Activity(name="Jalan Kaki", calories_per_hour=280, intensity_level="Ringan"),
            Activity(name="Jogging", calories_per_hour=580, intensity_level="Sedang"),
            Activity(name="Bersepeda", calories_per_hour=450, intensity_level="Sedang"),
            Activity(name="Berenang", calories_per_hour=510, intensity_level="Sedang"),
            Activity(name="Angkat Beban", calories_per_hour=350, intensity_level="Sedang"),
            Activity(name="Yoga", calories_per_hour=250, intensity_level="Ringan"),
            Activity(name="Lari", calories_per_hour=700, intensity_level="Berat"),
            Activity(name="HIIT", calories_per_hour=860, intensity_level="Berat"),
            Activity(name="Pilates", calories_per_hour=300, intensity_level="Ringan"),
            Activity(name="Tenis", calories_per_hour=520, intensity_level="Sedang"),
        ]
        db.session.add_all(activities)
        
        # Membuat pengguna contoh
        print("Menambahkan pengguna contoh...")
        user = User(email="user@example.com", username="user_example")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()  # Commit user terlebih dahulu untuk mendapatkan ID
        
        # Menambahkan profil pengguna
        profile = UserProfile(
            user_id=user.id,
            weight=70.0,
            height=170.0,
            age=30,
            gender="Pria", 
            activity_level="Sedang",
            goal_weight=65.0,
            dietary_restrictions="None"
        )
        db.session.add(profile)
        
        # Menambahkan rekomendasi harian selama 7 hari
        print("Menambahkan rekomendasi harian...")
        today = date.today()
        
        # Contoh rekomendasi sederhana
        for i in range(7):
            day = today + timedelta(days=i)
            recommendation = DailyRecommendation(
                user_id=user.id,
                date=day,
                breakfast="Nasi putih dengan telur dadar dan sayur bayam",
                lunch="Nasi putih dengan ayam goreng dan sayur",
                dinner="Nasi putih dengan ikan dan sayur bayam",
                activities="Jogging selama 30 menit, Yoga selama 15 menit",
                total_calories=2200,
                target_calories=2500,
                is_completed=False if i > 0 else True
            )
            db.session.add(recommendation)
            
            # Tambahkan check-in untuk hari pertama
            if i == 0:
                checkin = DailyCheckin(
                    user_id=user.id,
                    recommendation_id=1,  # Akan diperbarui setelah commit
                    date=day,
                    food_completed=True,
                    activity_completed=True
                )
                db.session.add(checkin)
        
        db.session.commit()
        print("Database berhasil diinisialisasi!")

if __name__ == "__main__":
    init_db() 