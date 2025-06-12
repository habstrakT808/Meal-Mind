# backend/app/ml/recommendation_engine.py
import json
import random
from typing import Dict, List, Any

class MealRecommendationEngine:
    def __init__(self):
        # Data makanan Indonesia (sementara hardcode, nanti bisa dari database)
        self.foods_data = {
            'breakfast': [
                {'name': 'Nasi Gudeg + Telur', 'calories': 450, 'protein': 15, 'carbs': 65, 'fat': 12},
                {'name': 'Roti Bakar + Selai + Susu', 'calories': 320, 'protein': 12, 'carbs': 45, 'fat': 10},
                {'name': 'Bubur Ayam + Kerupuk', 'calories': 380, 'protein': 18, 'carbs': 55, 'fat': 8},
                {'name': 'Nasi Uduk + Ayam Goreng', 'calories': 520, 'protein': 25, 'carbs': 60, 'fat': 18},
                {'name': 'Lontong Sayur + Telur', 'calories': 350, 'protein': 14, 'carbs': 50, 'fat': 9}
            ],
            'lunch': [
                {'name': 'Nasi + Ayam Bakar + Lalapan', 'calories': 650, 'protein': 35, 'carbs': 70, 'fat': 20},
                {'name': 'Nasi + Rendang + Sayur', 'calories': 720, 'protein': 30, 'carbs': 75, 'fat': 25},
                {'name': 'Nasi + Ikan Bakar + Tumis Kangkung', 'calories': 580, 'protein': 32, 'carbs': 65, 'fat': 18},
                {'name': 'Nasi + Soto Ayam + Kerupuk', 'calories': 620, 'protein': 28, 'carbs': 70, 'fat': 22},
                {'name': 'Nasi + Gado-gado + Kerupuk', 'calories': 550, 'protein': 20, 'carbs': 68, 'fat': 20}
            ],
            'dinner': [
                {'name': 'Nasi + Pecel Lele + Lalapan', 'calories': 480, 'protein': 25, 'carbs': 55, 'fat': 15},
                {'name': 'Sandwich + Telur + Susu', 'calories': 420, 'protein': 18, 'carbs': 45, 'fat': 16},
                {'name': 'Nasi + Ayam Geprek + Sayur', 'calories': 520, 'protein': 30, 'carbs': 58, 'fat': 18},
                {'name': 'Mie Ayam + Pangsit + Bakso', 'calories': 450, 'protein': 22, 'carbs': 60, 'fat': 12},
                {'name': 'Nasi + Tempe Goreng + Sayur Asem', 'calories': 380, 'protein': 16, 'carbs': 55, 'fat': 10}
            ]
        }
        
        # Data aktivitas fisik
        self.activities_data = [
            {'name': 'Jogging', 'calories_per_hour': 400, 'intensity': 'medium'},
            {'name': 'Bersepeda', 'calories_per_hour': 300, 'intensity': 'medium'},
            {'name': 'Berenang', 'calories_per_hour': 500, 'intensity': 'high'},
            {'name': 'Jalan Kaki', 'calories_per_hour': 200, 'intensity': 'low'},
            {'name': 'Senam Aerobik', 'calories_per_hour': 350, 'intensity': 'medium'},
            {'name': 'Push Up & Sit Up', 'calories_per_hour': 250, 'intensity': 'medium'},
            {'name': 'Yoga', 'calories_per_hour': 180, 'intensity': 'low'},
            {'name': 'Badminton', 'calories_per_hour': 320, 'intensity': 'medium'}
        ]

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Hitung Basal Metabolic Rate menggunakan rumus Mifflin-St Jeor"""
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return bmr

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Hitung Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,      # Tidak berolahraga
            'light': 1.375,        # Olahraga ringan 1-3 hari/minggu
            'moderate': 1.55,      # Olahraga sedang 3-5 hari/minggu
            'active': 1.725,       # Olahraga berat 6-7 hari/minggu
            'very_active': 1.9     # Olahraga sangat berat 2x sehari
        }
        return bmr * activity_multipliers.get(activity_level, 1.55)

    def calculate_target_calories(self, current_weight: float, goal_weight: float, tdee: float) -> float:
        """Hitung target kalori untuk diet"""
        if goal_weight < current_weight:
            # Untuk menurunkan berat badan: deficit 500-750 kalori per hari
            target_calories = tdee - 500
        elif goal_weight > current_weight:
            # Untuk menaikkan berat badan: surplus 300-500 kalori per hari
            target_calories = tdee + 300
        else:
            # Maintain berat badan
            target_calories = tdee
        
        # Pastikan tidak terlalu rendah (minimal 1200 kalori untuk wanita, 1500 untuk pria)
        min_calories = 1200
        return max(target_calories, min_calories)

    def filter_foods_by_restrictions(self, foods: List[Dict], dietary_restrictions: List[str]) -> List[Dict]:
        """Filter makanan berdasarkan pantangan diet"""
        if not dietary_restrictions:
            return foods
        
        filtered_foods = []
        for food in foods:
            food_name = food['name'].lower()
            is_restricted = False
            
            for restriction in dietary_restrictions:
                if restriction.lower() in food_name:
                    is_restricted = True
                    break
            
            if not is_restricted:
                filtered_foods.append(food)
        
        return filtered_foods

    def recommend_meals(self, target_calories: float, dietary_restrictions: List[str] = None) -> Dict[str, Any]:
        """Generate rekomendasi makanan"""
        # Distribusi kalori: 25% sarapan, 35% makan siang, 40% makan malam
        breakfast_target = target_calories * 0.25
        lunch_target = target_calories * 0.35
        dinner_target = target_calories * 0.40
        
        # Filter makanan berdasarkan pantangan
        breakfast_options = self.filter_foods_by_restrictions(
            self.foods_data['breakfast'], dietary_restrictions or []
        )
        lunch_options = self.filter_foods_by_restrictions(
            self.foods_data['lunch'], dietary_restrictions or []
        )
        dinner_options = self.filter_foods_by_restrictions(
            self.foods_data['dinner'], dietary_restrictions or []
        )
        
        # Pilih makanan yang kalorinya paling mendekati target
        def find_closest_meal(options, target):
            if not options:
                return {'name': 'Pilihan makanan tidak tersedia, mohon tambahkan lebih banyak makanan', 'calories': 0}
            return min(options, key=lambda x: abs(x['calories'] - target))
        
        breakfast = find_closest_meal(breakfast_options, breakfast_target)
        lunch = find_closest_meal(lunch_options, lunch_target)
        dinner = find_closest_meal(dinner_options, dinner_target)
        
        total_calories = breakfast['calories'] + lunch['calories'] + dinner['calories']
        
        return {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'total_calories': total_calories,
            'target_calories': int(target_calories)
        }

    def recommend_activities(self, calories_to_burn: float) -> List[Dict[str, Any]]:
        """Generate rekomendasi aktivitas fisik"""
        recommendations = []
        
        for activity in self.activities_data:
            # Hitung durasi yang diperlukan (dalam menit)
            duration_hours = calories_to_burn / activity['calories_per_hour']
            duration_minutes = duration_hours * 60
            
            # Hanya rekomendasikan aktivitas yang masuk akal (15-120 menit)
            if 15 <= duration_minutes <= 120:
                recommendations.append({
                    'name': activity['name'],
                    'duration_minutes': round(duration_minutes),
                    'calories_burned': round(calories_to_burn),
                    'intensity': activity['intensity']
                })
        
        # Return top 3 recommendations
        return recommendations[:3]

    def generate_daily_recommendation(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rekomendasi harian lengkap"""
        # Hitung BMR dan TDEE
        bmr = self.calculate_bmr(
            user_profile['weight'],
            user_profile['height'],
            user_profile['age'],
            user_profile['gender']
        )
        
        tdee = self.calculate_tdee(bmr, user_profile['activity_level'])
        
        # Hitung target kalori
        target_calories = self.calculate_target_calories(
            user_profile['weight'],
            user_profile.get('goal_weight', user_profile['weight']),
            tdee
        )
        
        # Parse dietary restrictions
        dietary_restrictions = []
        if user_profile.get('dietary_restrictions'):
            try:
                dietary_restrictions = json.loads(user_profile['dietary_restrictions'])
            except:
                dietary_restrictions = []
        
        # Generate meal recommendations
        meals = self.recommend_meals(target_calories, dietary_restrictions)
        
        # Hitung kalori yang perlu dibakar (jika ada deficit)
        calories_to_burn = max(0, tdee - target_calories)
        if calories_to_burn < 100:
            calories_to_burn = 200  # Minimal aktivitas untuk kesehatan
        
        # Generate activity recommendations
        activities = self.recommend_activities(calories_to_burn)
        
        return {
            'meals': meals,
            'activities': activities,
            'user_stats': {
                'bmr': round(bmr),
                'tdee': round(tdee),
                'target_calories': round(target_calories),
                'calories_to_burn': round(calories_to_burn)
            }
        }

    def regenerate_meal(self, meal_type: str, target_calories: float, dietary_restrictions: List[str] = None, exclude_previous: str = None) -> Dict[str, Any]:
        """Regenerate specific meal (breakfast, lunch, dinner)"""
        if meal_type not in ['breakfast', 'lunch', 'dinner']:
            raise ValueError("meal_type must be 'breakfast', 'lunch', or 'dinner'")
        
        # Target kalori per meal type
        meal_targets = {
            'breakfast': target_calories * 0.25,
            'lunch': target_calories * 0.35,
            'dinner': target_calories * 0.40
        }
        
        target = meal_targets[meal_type]
        options = self.filter_foods_by_restrictions(
            self.foods_data[meal_type], dietary_restrictions or []
        )
        
        # Exclude previous recommendation
        if exclude_previous:
            options = [opt for opt in options if opt['name'] != exclude_previous]
        
        if not options:
            return {'name': 'Pilihan makanan tidak tersedia, mohon tambahkan lebih banyak makanan', 'calories': 0}
        
        # Pilih random dari 3 opsi terbaik
        sorted_options = sorted(options, key=lambda x: abs(x['calories'] - target))
        top_options = sorted_options[:3]
        
        return random.choice(top_options)

    def regenerate_activities(self, calories_to_burn: float, exclude_previous: List[str] = None) -> List[Dict[str, Any]]:
        """Regenerate activity recommendations"""
        available_activities = [
            act for act in self.activities_data 
            if not exclude_previous or act['name'] not in exclude_previous
        ]
        
        recommendations = []
        for activity in available_activities:
            duration_hours = calories_to_burn / activity['calories_per_hour']
            duration_minutes = duration_hours * 60
            
            if 15 <= duration_minutes <= 120:
                recommendations.append({
                    'name': activity['name'],
                    'duration_minutes': round(duration_minutes),
                    'calories_burned': round(calories_to_burn),
                    'intensity': activity['intensity']
                })
        
        # Shuffle untuk variasi
        random.shuffle(recommendations)
        return recommendations[:3]