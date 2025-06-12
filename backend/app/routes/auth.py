# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        current_app.logger.info(f"Signup request received: {data}")
        
        # Validation
        if not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"User created: {user.id}")
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Signup error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        current_app.logger.info(f"Login attempt for: {data.get('email')}")
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            current_app.logger.info(f"Login failed: User not found for {data.get('email')}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
        if user and user.check_password(data['password']):
            # Convert user ID to string to avoid JWT subject type errors
            access_token = create_access_token(identity=str(user.id))
            
            # Fix: Check profile dengan query terpisah
            from app.models.user import UserProfile
            has_profile = UserProfile.query.filter_by(user_id=user.id).first() is not None
            
            current_app.logger.info(f"Login successful for user: {user.id}")
            
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict(),
                'has_profile': has_profile
            }), 200
        
        current_app.logger.info(f"Login failed: Invalid password for {data.get('email')}")
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'has_profile': user.profile is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500