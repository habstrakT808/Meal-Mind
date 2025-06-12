from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def index():
    """Endpoint dasar untuk user"""
    return jsonify({"message": "User endpoint"})

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """Mendapatkan informasi user yang sedang login"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User tidak ditemukan"}), 404
    
    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "has_profile": user.profile is not None
        }
    })

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Mendapatkan statistik user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.profile:
        return jsonify({"error": "User profile tidak ditemukan"}), 404
    
    # Contoh statistik sederhana
    stats = {
        "progress": {
            "days_completed": 0,
            "days_remaining": 30,
            "progress_percent": 0
        },
        "weight": {
            "start": user.profile.weight,
            "current": user.profile.weight,
            "goal": user.profile.goal_weight or user.profile.weight,
            "change": 0
        }
    }
    
    return jsonify({
        "status": "success",
        "stats": stats
    }) 