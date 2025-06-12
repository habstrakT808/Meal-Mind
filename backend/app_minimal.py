# backend/app_minimal.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
# Better CORS configuration for handling preflight requests
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minimal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Simple Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    goal_weight = db.Column(db.Float)
    dietary_restrictions = db.Column(db.Text)

# Routes
@app.route('/')
def home():
    return "Minimal Meal Mind API Working!"

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('email') or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': f'Email {data["email"]} is already registered'}), 400
        
        # Check if username already exists (optional)
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({'error': f'Username {data["username"]} is already taken'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()  # Rollback jika ada error
        print(f"Signup error: {e}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id))
            
            # Check if user has profile
            has_profile = UserProfile.query.filter_by(user_id=user.id).first() is not None
            print(f"Login: User {user.id} has profile: {has_profile}")
            
            # Return explicit has_profile flag in the user object as well as at the top level
            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at.isoformat(),
                'has_profile': has_profile  # Add has_profile directly in the user object
            }
            
            return jsonify({
                'access_token': access_token,
                'user': user_data,
                'has_profile': has_profile  # Include top level flag for backward compatibility
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check profile status
        has_profile = UserProfile.query.filter_by(user_id=user.id).first() is not None
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at.isoformat()
            },
            'has_profile': has_profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/setup', methods=['POST'])
@jwt_required()
def setup_profile():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Check if profile already exists
        existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({'error': 'Profile already exists'}), 400
        
        profile = UserProfile(
            user_id=user_id,
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            gender=data['gender'],
            activity_level=data['activity_level'],
            goal_weight=data.get('goal_weight', data['weight']),
            dietary_restrictions=str(data.get('dietary_restrictions', []))
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': {
                'weight': profile.weight,
                'height': profile.height,
                'age': profile.age,
                'gender': profile.gender,
                'activity_level': profile.activity_level,
                'goal_weight': profile.goal_weight,
                'dietary_restrictions': profile.dietary_restrictions
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/setup-test', methods=['POST', 'OPTIONS'])
def setup_profile_test():
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # For testing, we'll use a fixed user ID
        user_id = 3  # Test user ID
        data = request.get_json()
        
        print(f"TEST - Profile setup data: {data}")
        
        # Check if profile already exists
        existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            # Optionally update instead of returning error
            db.session.delete(existing_profile)
            db.session.commit()
            print(f"TEST - Deleted existing profile for user {user_id}")
        
        profile = UserProfile(
            user_id=user_id,
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            gender=data['gender'],
            activity_level=data['activity_level'],
            goal_weight=data.get('goal_weight', data['weight']),
            dietary_restrictions=str(data.get('dietary_restrictions', []))
        )
        
        db.session.add(profile)
        db.session.commit()
        
        print(f"TEST - Profile created successfully for user {user_id}")
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': {
                'weight': profile.weight,
                'height': profile.height,
                'age': profile.age,
                'gender': profile.gender,
                'activity_level': profile.activity_level,
                'goal_weight': profile.goal_weight,
                'dietary_restrictions': profile.dietary_restrictions
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"TEST - Profile setup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add a profile reset endpoint for testing
@app.route('/api/profile/reset-profile-test', methods=['GET', 'OPTIONS'])
def reset_profile_test():
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # For testing, use a fixed user ID
        user_id = 3  # Test user ID
        
        print(f"TEST - Attempting to delete profile for user {user_id}")
        
        # Delete existing profile if it exists
        existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            db.session.delete(existing_profile)
            db.session.commit()
            print(f"TEST - Profile deleted for user {user_id}")
            return jsonify({'message': 'Profile reset successfully'}), 200
        else:
            print(f"TEST - No profile found for user {user_id}")
            return jsonify({'message': 'No profile exists for this user'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"TEST - Error resetting profile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/today', methods=['GET'])
@jwt_required()
def get_recommendations():
    try:
        user_id = int(get_jwt_identity())
        
        # Get user profile
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Simple BMR calculation
        if profile.gender.lower() == 'male':
            bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161
        
        # Simple TDEE calculation
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        tdee = bmr * activity_multipliers.get(profile.activity_level, 1.55)
        
        # Target calories (deficit for weight loss)
        target_calories = tdee - 300 if profile.goal_weight < profile.weight else tdee
        
        # Mock recommendations (nanti bisa diganti dengan ML engine)
        mock_rec = {
            'breakfast': {'name': 'Nasi Gudeg + Telur', 'calories': 450},
            'lunch': {'name': 'Nasi + Ayam Bakar + Lalapan', 'calories': 650},
            'dinner': {'name': 'Sandwich + Telur + Susu', 'calories': 420},
            'activities': [
                {'name': 'Jogging', 'duration_minutes': 30, 'calories_burned': 200},
                {'name': 'Bersepeda', 'duration_minutes': 45, 'calories_burned': 225}
            ],
            'total_calories': 1520,
            'target_calories': int(target_calories)
        }
        
        return jsonify({
            'recommendations': mock_rec,
            'user_stats': {
                'bmr': int(bmr),
                'tdee': int(tdee),
                'target_calories': int(target_calories)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/today-test', methods=['GET', 'OPTIONS'])
def get_recommendations_test():
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # For testing, we'll use a fixed user ID
        user_id = 3  # Test user ID
        
        print(f"TEST - Getting recommendations for user {user_id}")
        
        # Get user profile
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            print(f"TEST - User {user_id} has no profile")
            return jsonify({'error': 'Profile not found', 'code': 'PROFILE_NOT_FOUND'}), 404
        
        # Simple BMR calculation
        if profile.gender.lower() == 'male':
            bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161
        
        # Simple TDEE calculation
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        tdee = bmr * activity_multipliers.get(profile.activity_level, 1.55)
        
        # Target calories (deficit for weight loss)
        target_calories = tdee - 300 if profile.goal_weight < profile.weight else tdee
        
        # Mock recommendations
        mock_rec = {
            'breakfast': {'name': 'Nasi Gudeg + Telur', 'calories': 450, 'protein': 20, 'carbs': 60, 'fat': 15},
            'lunch': {'name': 'Nasi + Ayam Bakar + Lalapan', 'calories': 650, 'protein': 35, 'carbs': 80, 'fat': 20},
            'dinner': {'name': 'Sandwich + Telur + Susu', 'calories': 420, 'protein': 25, 'carbs': 40, 'fat': 18},
            'activities': [
                {'name': 'Jogging', 'duration_minutes': 30, 'calories_burned': 200},
                {'name': 'Bersepeda', 'duration_minutes': 45, 'calories_burned': 225}
            ],
            'total_calories': 1520,
            'target_calories': int(target_calories)
        }
        
        print(f"TEST - Successfully retrieved recommendations for user {user_id}")
        
        return jsonify({
            'recommendations': mock_rec,
            'user_stats': {
                'bmr': int(bmr),
                'tdee': int(tdee),
                'target_calories': int(target_calories)
            }
        }), 200
        
    except Exception as e:
        print(f"TEST - Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/regenerate/<meal_type>', methods=['POST'])
@jwt_required()
def regenerate_recommendation(meal_type):
    try:
        user_id = int(get_jwt_identity())
        
        # Mock regenerate data
        new_meals = {
            'breakfast': {'name': 'Bubur Ayam + Kerupuk', 'calories': 380},
            'lunch': {'name': 'Nasi + Rendang + Sayur', 'calories': 720},
            'dinner': {'name': 'Mie Ayam + Pangsit', 'calories': 450}
        }
        
        new_activities = [
            {'name': 'Berenang', 'duration_minutes': 25, 'calories_burned': 200},
            {'name': 'Senam Aerobik', 'duration_minutes': 35, 'calories_burned': 175}
        ]
        
        if meal_type in new_meals:
            return jsonify({
                'message': f'{meal_type.title()} regenerated successfully',
                'new_recommendation': new_meals[meal_type]
            }), 200
        elif meal_type == 'activities':
            return jsonify({
                'message': 'Activities regenerated successfully',
                'new_recommendation': new_activities
            }), 200
        else:
            return jsonify({'error': 'Invalid meal_type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/checkin', methods=['POST'])
@jwt_required()
def daily_checkin():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Get today's recommendation
        today = date.today()
        recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'No recommendation found for today'}), 404
        
        # Check if already checked in today for this specific recommendation
        existing_checkin = DailyCheckin.query.filter_by(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=today
        ).first()
        
        if existing_checkin:
            return jsonify({
                'error': 'Already checked in today',
                'message': 'Anda sudah melakukan check-in untuk hari ini',
                'checkin': existing_checkin.to_dict()
            }), 400
            
        food_completed = data.get('food_completed', False)
        activity_completed = data.get('activity_completed', False)
        
        # Create checkin record
        checkin = DailyCheckin(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=today,
            food_completed=food_completed,
            activity_completed=activity_completed
        )
        
        db.session.add(checkin)
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in successful',
            'food_completed': food_completed,
            'activity_completed': activity_completed,
            'will_regenerate_tomorrow': not (food_completed and activity_completed)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/regenerate-test/<meal_type>', methods=['POST', 'OPTIONS'])
def regenerate_recommendation_test(meal_type):
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # For testing, we'll use a fixed user ID
        user_id = 3  # Test user ID
        
        print(f"TEST - Regenerating {meal_type} for user {user_id}")
        
        # Mock regenerate data with more nutritional info
        new_meals = {
            'breakfast': {
                'name': 'Oatmeal dengan Pisang dan Madu', 
                'calories': 350, 
                'protein': 12, 
                'carbs': 65, 
                'fat': 8
            },
            'lunch': {
                'name': 'Nasi Merah + Ikan Bakar + Sayur Asem', 
                'calories': 580, 
                'protein': 32, 
                'carbs': 70, 
                'fat': 15
            },
            'dinner': {
                'name': 'Sup Ayam dengan Sayuran', 
                'calories': 410, 
                'protein': 28, 
                'carbs': 35, 
                'fat': 12
            }
        }
        
        new_activities = [
            {'name': 'Yoga', 'duration_minutes': 40, 'calories_burned': 180},
            {'name': 'Jalan Cepat', 'duration_minutes': 30, 'calories_burned': 150}
        ]
        
        print(f"TEST - Processing regeneration for {meal_type}")
        
        if meal_type in new_meals:
            return jsonify({
                'message': f'{meal_type.title()} regenerated successfully',
                'recommendations': {
                    meal_type: new_meals[meal_type]
                }
            }), 200
            
        elif meal_type == 'activities':
            return jsonify({
                'message': 'Activities regenerated successfully',
                'recommendations': {
                    'activities': new_activities
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid meal_type'}), 400
        
    except Exception as e:
        print(f"TEST - Error regenerating {meal_type}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/checkin-test', methods=['POST', 'OPTIONS'])
def daily_checkin_test():
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # For testing, use a fixed user ID
        user_id = 3  # Test user ID
        data = request.get_json()
        
        print(f"TEST - Check-in for user {user_id}: {data}")
        
        # Get today's recommendation
        today = date.today()
        recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        if not recommendation:
            print(f"TEST - No recommendation found for today")
            return jsonify({'error': 'No recommendation found for today'}), 404
        
        # Check if already checked in today for this specific recommendation
        existing_checkin = DailyCheckin.query.filter_by(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=today
        ).first()
        
        if existing_checkin:
            print(f"TEST - Already checked in today for recommendation {recommendation.id}")
            return jsonify({
                'error': 'Already checked in today',
                'message': 'Anda sudah melakukan check-in untuk hari ini',
                'checkin': existing_checkin.to_dict()
            }), 400
            
        food_completed = data.get('food_completed', False)
        activity_completed = data.get('activity_completed', False)
        
        print(f"TEST - Food completed: {food_completed}, Activity completed: {activity_completed}")
        
        # Create checkin record
        checkin = DailyCheckin(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=today,
            food_completed=food_completed,
            activity_completed=activity_completed
        )
        
        db.session.add(checkin)
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in successful',
            'food_completed': food_completed,
            'activity_completed': activity_completed,
            'will_regenerate_tomorrow': not (food_completed and activity_completed)
        }), 200
        
    except Exception as e:
        print(f"TEST - Check-in error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add a test endpoint for checking user profile status
@app.route('/api/auth/profile-status-test/<int:user_id>', methods=['GET'])
def check_profile_status_test(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
        
        # Check if user has profile
        has_profile = UserProfile.query.filter_by(user_id=user_id).first() is not None
        print(f"TEST - User {user_id} has profile: {has_profile}")
        
        return jsonify({
            'user_id': user_id,
            'has_profile': has_profile,
            'test_user': has_profile
        }), 200
        
    except Exception as e:
        print(f"TEST - Error checking profile status: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
        
        # Print routes
        print("\n=== REGISTERED ROUTES ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule}")
        print("========================\n")
    
    app.run(debug=True)