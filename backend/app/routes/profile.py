# backend/app/routes/profile.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserProfile
import json
import traceback

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/setup', methods=['POST'])
@jwt_required()
def setup_profile():
    """Setup user profile"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Check if profile already exists - if it does, delete it first
        existing_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        if existing_profile:
            current_app.logger.info(f"Deleting existing profile for user {current_user_id} before creating new one")
            db.session.delete(existing_profile)
            db.session.commit()
        
        # Get profile data from request
        data = request.get_json()
        current_app.logger.info(f"Profile setup request for user {current_user_id}: {data}")
        
        # Validate required fields
        required_fields = ['weight', 'height', 'age', 'gender', 'activity_level', 'goal_weight']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert dietary_restrictions list to JSON string
        dietary_restrictions = json.dumps(data.get('dietary_restrictions', []))
        
        # Create profile
        profile = UserProfile(
            user_id=current_user_id,
            weight=data['weight'],
            height=data['height'],
            age=data['age'],
            gender=data['gender'],
            activity_level=data['activity_level'],
            goal_weight=data['goal_weight'],
            dietary_restrictions=dietary_restrictions
        )
        
        # Add profile to database
        db.session.add(profile)
        db.session.commit()
        
        current_app.logger.info(f"Profile created successfully for user {current_user_id}")
        
        return jsonify({'message': 'Profile created successfully'}), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating profile: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/get', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({'profile': profile.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'weight' in data:
            profile.weight = float(data['weight'])
        if 'height' in data:
            profile.height = float(data['height'])
        if 'age' in data:
            profile.age = int(data['age'])
        if 'gender' in data:
            profile.gender = data['gender']
        if 'activity_level' in data:
            profile.activity_level = data['activity_level']
        if 'goal_weight' in data:
            profile.goal_weight = float(data['goal_weight'])
        if 'dietary_restrictions' in data:
            profile.dietary_restrictions = json.dumps(data['dietary_restrictions'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a test endpoint without JWT for debugging
@profile_bp.route('/setup-test', methods=['POST'])
def setup_profile_test():
    try:
        data = request.get_json()
        
        # For testing, we'll use user ID 3
        user_id = 3
        
        # Print raw request data for debugging
        print(f"TEST - Raw profile setup data: {request.data}")
        print(f"TEST - Parsed profile setup data: {data}")
        current_app.logger.info(f"TEST - Profile setup request for user {user_id}: {data}")
        
        # More detailed validation with specific errors
        if not data:
            return jsonify({'error': 'No data provided'}), 422
            
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            current_app.logger.error(f"User with ID {user_id} not found")
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        # Check profile existence
        existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            current_app.logger.warning(f"Profile already exists for user {user_id}")
            return jsonify({'error': 'Profile already exists'}), 400
        
        # Required fields with type checking
        validations = [
            ('weight', float, 'weight must be a number'),
            ('height', float, 'height must be a number'),
            ('age', int, 'age must be an integer'),
            ('gender', str, 'gender is required'),
            ('activity_level', str, 'activity_level is required')
        ]
        
        profile_data = {}
        validation_errors = []
        
        # Validate each field
        for field, field_type, error_msg in validations:
            if field not in data:
                validation_errors.append(f"Missing field: {field}")
                continue
                
            try:
                if field_type == float:
                    profile_data[field] = float(data[field])
                elif field_type == int:
                    profile_data[field] = int(data[field])
                else:
                    profile_data[field] = data[field]
            except (ValueError, TypeError):
                validation_errors.append(error_msg)
        
        if validation_errors:
            return jsonify({'error': 'Validation errors', 'details': validation_errors}), 422
            
        # Optional fields with defaults
        if 'goal_weight' in data:
            try:
                profile_data['goal_weight'] = float(data['goal_weight'])
            except (ValueError, TypeError):
                profile_data['goal_weight'] = profile_data['weight']  # Default to current weight
        else:
            profile_data['goal_weight'] = profile_data['weight']
            
        # Dietary restrictions
        profile_data['dietary_restrictions'] = json.dumps(data.get('dietary_restrictions', []))
        
        # Create profile with validated data
        profile = UserProfile(
            user_id=user_id,
            **profile_data
        )
        
        db.session.add(profile)
        db.session.commit()
        
        current_app.logger.info(f"TEST - Profile created successfully for user {user_id}")
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': profile.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Profile setup test error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Add a test endpoint to reset/delete profile
@profile_bp.route('/reset-profile-test', methods=['GET'])
def reset_profile_test():
    try:
        # For testing, we'll use user ID 3
        user_id = 3
        
        print(f"TEST - Attempting to delete profile for user {user_id}")
        
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if profile:
            db.session.delete(profile)
            db.session.commit()
            print(f"TEST - Profile deleted for user {user_id}")
            return jsonify({'message': 'Profile deleted successfully'}), 200
        else:
            print(f"TEST - No profile found for user {user_id}")
            return jsonify({'message': 'No profile found to delete'}), 404
            
    except Exception as e:
        print(f"TEST - Error deleting profile: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset_profile():
    """Reset user profile"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Delete existing profile
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        if user_profile:
            db.session.delete(user_profile)
            db.session.commit()
            return {"message": "Profile reset successfully"}, 200
        else:
            return {"message": "No profile found"}, 404
            
    except Exception as e:
        current_app.logger.error(f"Error resetting profile: {str(e)}")
        return {"error": "Failed to reset profile"}, 500