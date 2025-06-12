from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/', methods=['GET'])
def index():
    """Endpoint dasar untuk activities"""
    return jsonify({"message": "Activities endpoint"})

@activities_bp.route('/list', methods=['GET'])
@jwt_required()
def get_activities():
    """Mendapatkan daftar aktivitas yang tersedia"""
    activities = [
        {'name': 'Jogging', 'calories_per_hour': 400, 'intensity': 'medium', 'met': 7.0},
        {'name': 'Bersepeda', 'calories_per_hour': 300, 'intensity': 'medium', 'met': 6.0},
        {'name': 'Berenang', 'calories_per_hour': 500, 'intensity': 'high', 'met': 8.0},
        {'name': 'Jalan Kaki', 'calories_per_hour': 200, 'intensity': 'low', 'met': 3.5},
        {'name': 'Senam Aerobik', 'calories_per_hour': 350, 'intensity': 'medium', 'met': 6.5},
        {'name': 'Push Up & Sit Up', 'calories_per_hour': 250, 'intensity': 'medium', 'met': 3.8},
        {'name': 'Yoga', 'calories_per_hour': 180, 'intensity': 'low', 'met': 3.0},
        {'name': 'Badminton', 'calories_per_hour': 320, 'intensity': 'medium', 'met': 5.5},
        {'name': 'Lari Interval', 'calories_per_hour': 450, 'intensity': 'high', 'met': 8.5},
        {'name': 'Pilates', 'calories_per_hour': 210, 'intensity': 'low', 'met': 3.5}
    ]
    
    return jsonify({
        'status': 'success',
        'activities': activities
    }) 