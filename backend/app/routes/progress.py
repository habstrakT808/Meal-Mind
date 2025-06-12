from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile
from app.models.recommendation import DailyRecommendation, DailyCheckin
from app.ml.diet_progress_analyzer import DietProgressAnalyzer
from datetime import date, datetime, timedelta
import json
import traceback
from flask import current_app

progress_bp = Blueprint('progress', __name__)
progress_analyzer = DietProgressAnalyzer()

@progress_bp.route('/analysis', methods=['GET'])
@jwt_required()
def get_progress_analysis():
    """Get comprehensive progress analysis for the user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Parse dates
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                # Default to 30 days ago
                start_date = date.today() - timedelta(days=30)
                
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                # Default to today + 30 days (for goal projection)
                end_date = date.today() + timedelta(days=30)
                
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get weight history (check if we have a dedicated table or use profile updates)
        weight_history = []
        
        # For now, just use the current weight as a stand-in
        weight_history.append((date.today(), user.profile.weight))
        
        # Get meal history
        recommendations = DailyRecommendation.query.filter(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.date >= start_date,
            DailyRecommendation.date <= date.today()
        ).order_by(DailyRecommendation.date).all()
        
        meal_history = []
        for rec in recommendations:
            try:
                meal_data = {
                    'date': rec.date.isoformat(),
                    'breakfast': json.loads(rec.breakfast),
                    'lunch': json.loads(rec.lunch),
                    'dinner': json.loads(rec.dinner),
                    'total_calories': rec.total_calories
                }
                meal_history.append(meal_data)
            except:
                # Skip invalid data
                continue
        
        # Get checkin history
        checkins = DailyCheckin.query.filter(
            DailyCheckin.user_id == user_id,
            DailyCheckin.date >= start_date,
            DailyCheckin.date <= date.today()
        ).order_by(DailyCheckin.date).all()
        
        checkin_history = [checkin.to_dict() for checkin in checkins]
        
        # Generate comprehensive analysis
        analysis = progress_analyzer.generate_comprehensive_analysis(
            user_profile=user.profile.to_dict(),
            start_date=start_date,
            current_date=date.today(),
            end_date=end_date,
            weight_history=weight_history,
            meal_history=meal_history,
            checkin_history=checkin_history
        )
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting progress analysis: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/weight/record', methods=['POST'])
@jwt_required()
def record_weight():
    """Record a new weight measurement"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'weight' not in data:
            return jsonify({'error': 'Weight is required'}), 400
        
        # Parse weight
        try:
            weight = float(data['weight'])
            if weight <= 0 or weight > 500:  # Basic validation
                return jsonify({'error': 'Invalid weight value'}), 400
        except ValueError:
            return jsonify({'error': 'Weight must be a number'}), 400
        
        # Parse date if provided, otherwise use today
        measurement_date = date.today()
        if 'date' in data:
            try:
                measurement_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Update user profile with the new weight
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # TODO: In the future, store weight history in a dedicated table
        # For now, just update the user profile
        user.profile.weight = weight
        user.profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Weight recorded: {weight} kg on {measurement_date.isoformat()}',
            'weight': weight,
            'date': measurement_date.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error recording weight: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/nutritional-balance', methods=['GET'])
@jwt_required()
def get_nutritional_balance():
    """Get analysis of nutritional balance from meal history"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters for date range
        days = request.args.get('days', default=30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get meal history
        recommendations = DailyRecommendation.query.filter(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.date >= start_date,
            DailyRecommendation.date <= end_date
        ).order_by(DailyRecommendation.date).all()
        
        meal_history = []
        for rec in recommendations:
            try:
                meal_data = {
                    'date': rec.date.isoformat(),
                    'breakfast': json.loads(rec.breakfast),
                    'lunch': json.loads(rec.lunch),
                    'dinner': json.loads(rec.dinner),
                    'total_calories': rec.total_calories
                }
                meal_history.append(meal_data)
            except:
                # Skip invalid data
                continue
        
        # Analyze nutritional balance
        analysis = progress_analyzer.analyze_nutritional_balance(meal_history)
        
        return jsonify({
            'status': 'success',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'analysis': analysis
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing nutritional balance: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/adherence', methods=['GET'])
@jwt_required()
def get_adherence_analysis():
    """Get analysis of user adherence to diet and exercise plan"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters for date range
        days = request.args.get('days', default=30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get checkin history
        checkins = DailyCheckin.query.filter(
            DailyCheckin.user_id == user_id,
            DailyCheckin.date >= start_date,
            DailyCheckin.date <= end_date
        ).order_by(DailyCheckin.date).all()
        
        checkin_history = [checkin.to_dict() for checkin in checkins]
        
        # Analyze adherence
        analysis = progress_analyzer.analyze_adherence(checkin_history)
        
        return jsonify({
            'status': 'success',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'analysis': analysis
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing adherence: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/calorie-adjustment', methods=['GET'])
@jwt_required()
def get_calorie_adjustment():
    """Get recommended calorie adjustment based on progress"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get current weight and goal weight
        current_weight = user.profile.weight
        goal_weight = user.profile.goal_weight or current_weight
        
        # Get current caloric intake from recent recommendations
        days_to_check = 7
        end_date = date.today()
        start_date = end_date - timedelta(days=days_to_check)
        
        recommendations = DailyRecommendation.query.filter(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.date >= start_date,
            DailyRecommendation.date <= end_date
        ).all()
        
        # Calculate average caloric intake
        if recommendations:
            current_calories = sum(r.total_calories for r in recommendations) / len(recommendations)
        else:
            # Fallback to target calories from the most recent recommendation
            latest_rec = DailyRecommendation.query.filter_by(
                user_id=user_id
            ).order_by(DailyRecommendation.date.desc()).first()
            
            if latest_rec:
                current_calories = latest_rec.target_calories
            else:
                return jsonify({'error': 'No recommendation history found'}), 404
        
        # Get adherence data for adjustment calculation
        checkins = DailyCheckin.query.filter(
            DailyCheckin.user_id == user_id,
            DailyCheckin.date >= start_date,
            DailyCheckin.date <= end_date
        ).all()
        
        # Calculate adherence percentage
        total_days = len(checkins)
        completed_days = sum(1 for c in checkins 
                           if c.food_completed and c.activity_completed)
        
        adherence_percent = (completed_days / total_days) * 100 if total_days > 0 else 50
        
        # Calculate days remaining in the plan
        # This is a placeholder - in reality you might want to use the actual plan end date
        days_remaining = 30
        
        # Calculate calorie adjustment
        adjustment = progress_analyzer.calculate_calories_adjustment(
            current_weight=current_weight,
            target_weight=goal_weight,
            current_calories=current_calories,
            days_remaining=days_remaining,
            adherence_percent=adherence_percent
        )
        
        return jsonify({
            'status': 'success',
            'current_weight': current_weight,
            'goal_weight': goal_weight,
            'current_calories': current_calories,
            'adherence_percent': adherence_percent,
            'adjustment': adjustment
        })
        
    except Exception as e:
        current_app.logger.error(f"Error calculating calorie adjustment: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500 