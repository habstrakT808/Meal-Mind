# backend/simple_recommendations.py
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-string'
jwt = JWTManager(app)

# Simple in-memory storage
users = {}
profiles = {}
recommendations = {}

@app.route('/')
def home():
    return "Simple Meal Mind API"

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    
    if email in users:
        return jsonify({'error': 'User exists'}), 400
    
    users[email] = {
        'email': email,
        'username': data['username'],
        'password': generate_password_hash(data['password'])
    }
    
    return jsonify({'message': 'User created'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    
    if email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[email]
    if check_password_hash(user['password'], data['password']):
        token = create_access_token(identity=email)
        return jsonify({
            'access_token': token,
            'user': {'email': email, 'username': user['username']},
            'has_profile': email in profiles
        })
    
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/profile/setup', methods=['POST'])
@jwt_required()
def setup_profile():
    email = get_jwt_identity()
    data = request.get_json()
    
    profiles[email] = data
    return jsonify({'message': 'Profile created', 'profile': data}), 201

@app.route('/api/recommendations/today', methods=['GET'])
@jwt_required()
def get_recommendations():
    email = get_jwt_identity()
    
    if email not in profiles:
        return jsonify({'error': 'Profile not found'}), 404
    
    # Simple mock recommendation
    mock_rec = {
        'breakfast': {'name': 'Nasi Gudeg + Telur', 'calories': 450},
        'lunch': {'name': 'Nasi + Ayam Bakar + Lalapan', 'calories': 650},
        'dinner': {'name': 'Sandwich + Telur + Susu', 'calories': 420},
        'activities': [{'name': 'Jogging', 'duration_minutes': 30}],
        'total_calories': 1520,
        'target_calories': 1800
    }
    
    return jsonify({'recommendations': mock_rec})

@app.route('/api/recommendations/regenerate/<meal_type>', methods=['POST'])
@jwt_required()
def regenerate(meal_type):
    email = get_jwt_identity()
    
    new_meals = {
        'breakfast': {'name': 'Bubur Ayam + Kerupuk', 'calories': 380},
        'lunch': {'name': 'Nasi + Rendang + Sayur', 'calories': 720},
        'dinner': {'name': 'Mie Ayam + Pangsit', 'calories': 450}
    }
    
    return jsonify({
        'message': f'{meal_type} regenerated',
        'new_meal': new_meals.get(meal_type, {})
    })

if __name__ == '__main__':
    app.run(debug=True)