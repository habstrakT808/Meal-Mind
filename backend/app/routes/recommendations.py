# backend/app/routes/recommendations.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile
from app.models.recommendation import DailyRecommendation, DailyCheckin
from app.ml.advanced_recommendation_engine import AdvancedRecommendationEngine
from app.ml.diet_progress_analyzer import DietProgressAnalyzer
from datetime import date, datetime, timedelta
import json
import calendar
import traceback
from flask import current_app
import os
import random

recommendations_bp = Blueprint('recommendations', __name__)
# Initialize the advanced recommendation engine with USDA API key from environment
api_key = os.environ.get('USDA_API_KEY')
ml_engine = AdvancedRecommendationEngine(api_key=api_key)
progress_analyzer = DietProgressAnalyzer()

# Function to generate a month of recommendations for a user
def generate_month_recommendations(user_id):
    try:
        # Check if user exists and has a profile
        user = User.query.get(user_id)
        if not user or not user.profile:
            return False, "User profile not found"
        
        # Start from today
        start_date = date.today()
        
        # Generate for 30 days ahead
        end_date = start_date + timedelta(days=30)
        
        current_date = start_date
        created_count = 0
        
        # Create a local instance of the engine for thread safety
        local_ml_engine = AdvancedRecommendationEngine()
        
        while current_date <= end_date:
            # Check if recommendation already exists for this date
            existing_rec = DailyRecommendation.query.filter_by(
                user_id=user_id, 
                date=current_date
            ).first()
            
            if not existing_rec:
                # Generate new recommendation
                user_profile_dict = user.profile.to_dict()
                recommendation_data = local_ml_engine.generate_daily_recommendation(user_profile_dict)
                
                # Save to database
                new_recommendation = DailyRecommendation(
                    user_id=user_id,
                    date=current_date,
                    breakfast=json.dumps(recommendation_data['meals']['breakfast']),
                    lunch=json.dumps(recommendation_data['meals']['lunch']),
                    dinner=json.dumps(recommendation_data['meals']['dinner']),
                    activities=json.dumps(recommendation_data['activities']),
                    total_calories=recommendation_data['meals']['total_calories'],
                    target_calories=recommendation_data['meals']['target_calories']
                )
                
                db.session.add(new_recommendation)
                created_count += 1
            
            current_date += timedelta(days=1)
        
        # Commit all changes at once
        db.session.commit()
        
        return True, f"Generated {created_count} days of recommendations"
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error auto-generating month: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False, str(e)

@recommendations_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_recommendations():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Hitung progress program diet
        today = date.today()
        start_date = user.profile.created_at.date()
        diet_duration = 30  # Default ke 30 hari
        day_in_program = (today - start_date).days + 1  # Hari pertama = 1
        days_remaining = max(0, diet_duration - day_in_program + 1)
        
        # Check if we need to generate a month of recommendations
        recommendations_count = DailyRecommendation.query.filter(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.date >= date.today()
        ).count()
        
        if recommendations_count < 30:
            # Generate a month of recommendations if fewer than 30 days exist
            success, message = generate_month_recommendations(user_id)
            if not success:
                current_app.logger.warning(f"Could not auto-generate month: {message}")
        
        # Cek apakah sudah ada rekomendasi hari ini
        existing_rec = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        # Dapatkan data check-in
        checkin_stats = {
            'total_completed': 0,
            'streak': 0,
            'last_week': 0
        }
        
        # Dapatkan statistik check-in
        try:
            # Hitung total check-in yang selesai (food dan activity)
            total_completed = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.food_completed == True,
                DailyCheckin.activity_completed == True
            ).count()
            
            # Hitung streak saat ini
            streak = 0
            check_date = today - timedelta(days=1)  # Mulai dari kemarin
            
            while True:
                checkin = DailyCheckin.query.filter(
                    DailyCheckin.user_id == user_id,
                    DailyCheckin.date == check_date,
                    DailyCheckin.food_completed == True,
                    DailyCheckin.activity_completed == True
                ).first()
                
                if not checkin:
                    break
                    
                streak += 1
                check_date -= timedelta(days=1)
            
            # Hitung check-ins minggu lalu
            last_week_start = today - timedelta(days=7)
            last_week_completed = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.date >= last_week_start,
                DailyCheckin.date < today,
                DailyCheckin.food_completed == True,
                DailyCheckin.activity_completed == True
            ).count()
            
            checkin_stats = {
                'total_completed': total_completed,
                'streak': streak,
                'last_week': last_week_completed
            }
        except Exception as e:
            current_app.logger.error(f"Error calculating checkin stats: {str(e)}")
        
        if existing_rec:
            # Check if user has already checked in today for this recommendation
            today_checkin = DailyCheckin.query.filter_by(
                user_id=user_id,
                recommendation_id=existing_rec.id,
                date=today
            ).first()
            
            already_checked_in = today_checkin is not None
            
            # Return existing recommendation
            return jsonify({
                'recommendations': existing_rec.to_dict(),
                'is_new': False,
                'already_checked_in': already_checked_in,
                'program_progress': {
                    'day_in_program': day_in_program,
                    'diet_duration': diet_duration,
                    'days_remaining': days_remaining
                },
                'checkin_stats': checkin_stats
            }), 200
        
        # Generate new recommendation
        user_profile_dict = user.profile.to_dict()
        
        # Create a new instance to avoid thread issues
        local_ml_engine = AdvancedRecommendationEngine()
        recommendation_data = local_ml_engine.generate_daily_recommendation(user_profile_dict)
        
        # Save to database
        new_recommendation = DailyRecommendation(
            user_id=user_id,
            date=today,
            breakfast=json.dumps(recommendation_data['meals']['breakfast']),
            lunch=json.dumps(recommendation_data['meals']['lunch']),
            dinner=json.dumps(recommendation_data['meals']['dinner']),
            activities=json.dumps(recommendation_data['activities']),
            total_calories=recommendation_data['meals']['total_calories'],
            target_calories=recommendation_data['meals']['target_calories']
        )
        
        db.session.add(new_recommendation)
        db.session.commit()
        
        return jsonify({
            'recommendations': new_recommendation.to_dict(),
            'user_stats': recommendation_data['user_stats'],
            'is_new': True,
            'already_checked_in': False,
            'program_progress': {
                'day_in_program': day_in_program,
                'diet_duration': diet_duration,
                'days_remaining': days_remaining
            },
            'checkin_stats': checkin_stats
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error getting today recommendations: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/regenerate/<meal_type>', methods=['POST'])
@jwt_required()
def regenerate_recommendation(meal_type):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get today's recommendation
        today = date.today()
        recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'No recommendation found for today'}), 404
        
        # Parse dietary restrictions
        dietary_restrictions = []
        if user.profile.dietary_restrictions:
            try:
                dietary_restrictions = json.loads(user.profile.dietary_restrictions)
            except:
                dietary_restrictions = []
                
        # Create a new instance to avoid thread issues
        local_ml_engine = AdvancedRecommendationEngine()
        
        if meal_type in ['breakfast', 'lunch', 'dinner']:
            # Get current meal to exclude
            current_meal = json.loads(getattr(recommendation, meal_type))
            exclude_previous = current_meal.get('name', '')
            
            # Regenerate specific meal
            new_meal = local_ml_engine.regenerate_meal(
                meal_type, 
                recommendation.target_calories,
                dietary_restrictions,
                exclude_previous
            )
            
            # Update database
            setattr(recommendation, meal_type, json.dumps(new_meal))
            
            # Recalculate total calories
            breakfast = json.loads(recommendation.breakfast)
            lunch = json.loads(recommendation.lunch)
            dinner = json.loads(recommendation.dinner)
            recommendation.total_calories = breakfast['calories'] + lunch['calories'] + dinner['calories']
            
        elif meal_type == 'activities':
            # Get current activities to exclude
            current_activities = json.loads(recommendation.activities)
            exclude_previous = [act.get('name', '') for act in current_activities]
            
            # Calculate calories to burn
            user_profile_dict = user.profile.to_dict()
            bmr = local_ml_engine.calculate_bmr(
                user_profile_dict['weight'],
                user_profile_dict['height'],
                user_profile_dict['age'],
                user_profile_dict['gender']
            )
            tdee = local_ml_engine.calculate_tdee(bmr, user_profile_dict['activity_level'])
            calories_to_burn = max(0, tdee - recommendation.target_calories)
            
            # Regenerate activities
            new_activities = local_ml_engine.regenerate_activities(calories_to_burn, exclude_previous)
            
            # Update database
            recommendation.activities = json.dumps(new_activities)
        
        else:
            return jsonify({'error': 'Invalid meal_type. Use: breakfast, lunch, dinner, or activities'}), 400
        
        db.session.commit()
        
        return jsonify({
            'recommendations': recommendation.to_dict(),
            'message': f'{meal_type.title()} regenerated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/checkin', methods=['POST'])
@jwt_required()
def daily_checkin():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'food_completed' not in data or 'activity_completed' not in data:
            return jsonify({'error': 'Missing food_completed or activity_completed'}), 400
        
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
        
        # Create checkin record
        checkin = DailyCheckin(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=today,
            food_completed=data['food_completed'],
            activity_completed=data['activity_completed']
        )
        
        # Update recommendation completion status
        recommendation.is_completed = data['food_completed'] and data['activity_completed']
        
        db.session.add(checkin)
        db.session.commit()
        
        # Calculate next day's recommendation
        tomorrow = date.today() + timedelta(days=1)
        next_day_recommendation = None
        
        # Check if tomorrow's recommendation already exists
        existing_recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=tomorrow
        ).first()
        
        # If both food and activities were completed, keep existing recommendation as is
        if data['food_completed'] and data['activity_completed']:
            next_day_recommendation = existing_recommendation
        else:
            # Get user profile
            user = User.query.get(user_id)
            if not user or not user.profile:
                return jsonify({'error': 'User profile not found'}), 404
                
            # Get recommendations for the past week to analyze progress
            past_week = today - timedelta(days=7)
            past_recommendations = DailyRecommendation.query.filter(
                DailyRecommendation.user_id == user_id,
                DailyRecommendation.date >= past_week,
                DailyRecommendation.date <= today
            ).all()
            
            past_checkins = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.date >= past_week,
                DailyCheckin.date <= today
            ).all()
            
            # Convert to dictionary for easier lookup
            checkin_dict = {c.date: c for c in past_checkins}
            
            # Calculate adherence metrics
            days_passed = len(past_recommendations)
            successful_days = sum(1 for r in past_recommendations if 
                                 r.date in checkin_dict and 
                                 checkin_dict[r.date].food_completed and 
                                 checkin_dict[r.date].activity_completed)
            
            # Create a recommendation engine instance
            ml_engine_local = AdvancedRecommendationEngine()
            
            # Calculate new target calories based on adherence
            user_profile_dict = user.profile.to_dict()
            
            # Calculate remaining days in the diet plan (assume 30 days total)
            start_date = user.profile.created_at.date()
            diet_duration = 30  # Default to 30 days
            days_elapsed = (today - start_date).days
            days_remaining = max(1, diet_duration - days_elapsed)
            
            # Adjust for missed days
            if days_passed > 0 and successful_days < days_passed:
                # Get original target calories (before any adjustments)
                bmr = ml_engine_local.calculate_bmr(
                    user_profile_dict['weight'],
                    user_profile_dict['height'],
                    user_profile_dict['age'],
                    user_profile_dict['gender']
                )
                
                tdee = ml_engine_local.calculate_tdee(bmr, user_profile_dict['activity_level'])
                
                # Calculate base target calories
                original_target = ml_engine_local.calculate_target_calories(
                    user_profile_dict['weight'],
                    user_profile_dict['goal_weight'],
                    tdee,
                    timeframe=diet_duration,
                    gender=user_profile_dict['gender']
                )
                
                # Adjust for missed days
                adjusted_target = ml_engine_local.adjust_target_calories_for_missed_days(
                    original_target,
                    user_profile_dict['weight'],
                    user_profile_dict['goal_weight'],
                    days_passed,
                    successful_days,
                    days_remaining,
                    tdee,
                    gender=user_profile_dict['gender']
                )
                
                # Generate new recommendation with adjusted calories
                recommendation_data = ml_engine_local.generate_daily_recommendation(
                    user_profile_dict,
                    user_id=user_id,
                    day_in_plan=days_elapsed + 1,  # Current day in the plan
                    plan_length=diet_duration,
                    previous_days=[]  # We already accounted for adherence
                )
                
                # Create or update recommendation for tomorrow
                if existing_recommendation:
                    # Update existing
                    existing_recommendation.breakfast = json.dumps(recommendation_data['meals']['breakfast'])
                    existing_recommendation.lunch = json.dumps(recommendation_data['meals']['lunch'])
                    existing_recommendation.dinner = json.dumps(recommendation_data['meals']['dinner'])
                    existing_recommendation.activities = json.dumps(recommendation_data['activities'])
                    existing_recommendation.total_calories = recommendation_data['meals']['total_calories']
                    existing_recommendation.target_calories = recommendation_data['meals']['target_calories']
                    next_day_recommendation = existing_recommendation
                else:
                    # Create new
                    next_day_recommendation = DailyRecommendation(
                        user_id=user_id,
                        date=tomorrow,
                        breakfast=json.dumps(recommendation_data['meals']['breakfast']),
                        lunch=json.dumps(recommendation_data['meals']['lunch']),
                        dinner=json.dumps(recommendation_data['meals']['dinner']),
                        activities=json.dumps(recommendation_data['activities']),
                        total_calories=recommendation_data['meals']['total_calories'],
                        target_calories=recommendation_data['meals']['target_calories']
                    )
                    db.session.add(next_day_recommendation)
            else:
                # All activities completed, keep recommendation as is
                next_day_recommendation = existing_recommendation
            
            db.session.commit()
        
        # Prepare response with tomorrow's recommendation
        next_day_data = {}
        if next_day_recommendation:
            next_day_data = next_day_recommendation.to_dict()
        
        return jsonify({
            'message': 'Check-in successful',
            'checkin': checkin.to_dict(),
            'recommendation_updated': recommendation.is_completed,
            'next_day_recommendation': next_day_data,
            'next_date': tomorrow.isoformat(),
            'will_regenerate_tomorrow': not (data['food_completed'] and data['activity_completed'])
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error during check-in: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/history', methods=['GET'])
@jwt_required()
def get_recommendation_history():
    try:
        user_id = get_jwt_identity()
        
        # Get last 7 days of recommendations
        recommendations = DailyRecommendation.query.filter_by(
            user_id=user_id
        ).order_by(DailyRecommendation.date.desc()).limit(7).all()
        
        history = []
        for rec in recommendations:
            rec_dict = rec.to_dict()
            
            # Get checkin for this date
            checkin = DailyCheckin.query.filter_by(
                user_id=user_id,
                recommendation_id=rec.id
            ).first()
            
            rec_dict['checkin'] = checkin.to_dict() if checkin else None
            history.append(rec_dict)
        
        return jsonify({
            'history': history,
            'total_days': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a test endpoint without JWT for debugging
@recommendations_bp.route('/today-test', methods=['GET'])
def get_today_recommendations_test():
    try:
        # For testing, we'll use user ID 3
        user_id = 3
        user = User.query.get(user_id)
        
        print(f"TEST - Getting recommendations for user {user_id}")
        
        if not user:
            print(f"TEST - User {user_id} not found")
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
        
        # Check if user has a profile
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            print(f"TEST - User {user_id} has no profile")
            return jsonify({'error': 'User profile not found', 'code': 'PROFILE_NOT_FOUND'}), 404
        
        # Hitung progress program diet
        today = date.today()
        start_date = profile.created_at.date() if profile.created_at else today - timedelta(days=5)  # Default jika tidak ada created_at
        diet_duration = 30  # Default ke 30 hari
        day_in_program = (today - start_date).days + 1  # Hari pertama = 1
        days_remaining = max(0, diet_duration - day_in_program + 1)
        
        print(f"TEST - Program progress: Day {day_in_program} of {diet_duration} ({days_remaining} days remaining)")
            
        # Check if there are recommendations for today
        existing_rec = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        # Dapatkan data check-in untuk test
        checkin_stats = {
            'total_completed': 0,
            'streak': 0,
            'last_week': 0
        }
        
        # Dapatkan statistik check-in untuk test
        try:
            # Hitung total check-in yang selesai (food dan activity)
            total_completed = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.food_completed == True,
                DailyCheckin.activity_completed == True
            ).count()
            
            # Hitung streak saat ini
            streak = 0
            check_date = today - timedelta(days=1)  # Mulai dari kemarin
            
            while True:
                checkin = DailyCheckin.query.filter(
                    DailyCheckin.user_id == user_id,
                    DailyCheckin.date == check_date,
                    DailyCheckin.food_completed == True,
                    DailyCheckin.activity_completed == True
                ).first()
                
                if not checkin:
                    break
                    
                streak += 1
                check_date -= timedelta(days=1)
            
            # Hitung check-ins minggu lalu
            last_week_start = today - timedelta(days=7)
            last_week_completed = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.date >= last_week_start,
                DailyCheckin.date < today,
                DailyCheckin.food_completed == True,
                DailyCheckin.activity_completed == True
            ).count()
            
            checkin_stats = {
                'total_completed': total_completed,
                'streak': streak,
                'last_week': last_week_completed
            }
            
            print(f"TEST - Checkin stats: Total={total_completed}, Streak={streak}, Last Week={last_week_completed}")
        except Exception as e:
            print(f"TEST - Error calculating checkin stats: {str(e)}")
        
        if existing_rec:
            # Check if user has already checked in today for this recommendation
            today_checkin = DailyCheckin.query.filter_by(
                user_id=user_id,
                recommendation_id=existing_rec.id,
                date=today
            ).first()
            
            already_checked_in = today_checkin is not None
            
            # Return existing recommendation
            print(f"TEST - Returning existing recommendation for today, already checked in: {already_checked_in}")
            return jsonify({
                'recommendations': existing_rec.to_dict(),
                'is_new': False,
                'already_checked_in': already_checked_in,
                'program_progress': {
                    'day_in_program': day_in_program,
                    'diet_duration': diet_duration,
                    'days_remaining': days_remaining
                },
                'checkin_stats': checkin_stats
            }), 200
        
        # Generate new recommendation
        print(f"TEST - Generating new recommendation for user {user_id}")
        user_profile_dict = profile.to_dict()  # Use profile directly instead of user.profile
        
        # Create a local instance to avoid thread issues
        local_ml_engine = AdvancedRecommendationEngine()
        recommendation_data = local_ml_engine.generate_daily_recommendation(user_profile_dict)
        
        # Save to database
        new_recommendation = DailyRecommendation(
            user_id=user_id,
            date=today,
            breakfast=json.dumps(recommendation_data['meals']['breakfast']),
            lunch=json.dumps(recommendation_data['meals']['lunch']),
            dinner=json.dumps(recommendation_data['meals']['dinner']),
            activities=json.dumps(recommendation_data['activities']),
            total_calories=recommendation_data['meals']['total_calories'],
            target_calories=recommendation_data['meals']['target_calories']
        )
        
        db.session.add(new_recommendation)
        db.session.commit()
        
        print(f"TEST - New recommendation created for user {user_id}")
        
        return jsonify({
            'recommendations': new_recommendation.to_dict(),
            'user_stats': recommendation_data['user_stats'],
            'is_new': True,
            'already_checked_in': False,
            'program_progress': {
                'day_in_program': day_in_program,
                'diet_duration': diet_duration,
                'days_remaining': days_remaining
            },
            'checkin_stats': checkin_stats
        }), 201
        
    except Exception as e:
        print(f"TEST - Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add a test endpoint for regenerating recommendations
@recommendations_bp.route('/regenerate-test/<meal_type>', methods=['POST'])
def regenerate_recommendation_test(meal_type):
    try:
        # For testing, we'll use user ID 3
        user_id = 3
        user = User.query.get(user_id)
        
        print(f"TEST - Regenerating {meal_type} for user {user_id}")
        
        if not user:
            print(f"TEST - User {user_id} not found")
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
        
        # Get today's recommendation
        today = date.today()
        recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        if not recommendation:
            print(f"TEST - No recommendation found for today")
            return jsonify({'error': 'No recommendation found for today'}), 404
        
        # Get profile
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            print(f"TEST - User {user_id} has no profile")
            return jsonify({'error': 'User profile not found'}), 404
        
        # Parse dietary restrictions
        dietary_restrictions = []
        if profile.dietary_restrictions:
            try:
                dietary_restrictions = json.loads(profile.dietary_restrictions)
            except:
                dietary_restrictions = []
        
        print(f"TEST - Processing regeneration for {meal_type}")
        
        # Create a new instance of the recommendation engine to avoid thread issues
        local_ml_engine = AdvancedRecommendationEngine()

        if meal_type in ['breakfast', 'lunch', 'dinner']:
            # Get current meal to exclude
            current_meal = json.loads(getattr(recommendation, meal_type))
            exclude_previous = current_meal.get('name', '')
            
            # Regenerate specific meal
            new_meal = local_ml_engine.regenerate_meal(
                meal_type, 
                recommendation.target_calories,
                dietary_restrictions,
                exclude_previous
            )
            
            # Update database
            setattr(recommendation, meal_type, json.dumps(new_meal))
            
            # Recalculate total calories
            breakfast = json.loads(recommendation.breakfast)
            lunch = json.loads(recommendation.lunch)
            dinner = json.loads(recommendation.dinner)
            recommendation.total_calories = breakfast['calories'] + lunch['calories'] + dinner['calories']
            
        elif meal_type == 'activities':
            # Get current activities to exclude
            current_activities = json.loads(recommendation.activities)
            exclude_previous = [act.get('name', '') for act in current_activities]
            
            # Calculate calories to burn
            user_profile_dict = profile.to_dict()
            bmr = local_ml_engine.calculate_bmr(
                user_profile_dict['weight'],
                user_profile_dict['height'],
                user_profile_dict['age'],
                user_profile_dict['gender']
            )
            tdee = local_ml_engine.calculate_tdee(bmr, user_profile_dict['activity_level'])
            calories_to_burn = max(200, tdee - recommendation.target_calories)
            
            # Regenerate activities
            new_activities = local_ml_engine.regenerate_activities(calories_to_burn, exclude_previous)
            
            # Update database
            recommendation.activities = json.dumps(new_activities)
        
        else:
            print(f"TEST - Invalid meal_type: {meal_type}")
            return jsonify({'error': 'Invalid meal_type. Use: breakfast, lunch, dinner, or activities'}), 400
        
        db.session.commit()
        print(f"TEST - Successfully regenerated {meal_type}")
        
        return jsonify({
            'recommendations': recommendation.to_dict(),
            'message': f'{meal_type.title()} regenerated successfully'
        }), 200
        
    except Exception as e:
        print(f"TEST - Error regenerating {meal_type}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add a test endpoint for daily check-in
@recommendations_bp.route('/checkin-test', methods=['POST'])
def daily_checkin_test():
    try:
        # For testing, we'll use user ID 3
        user_id = 3
        data = request.get_json()
        
        print(f"TEST - Check-in attempt for user {user_id}")
        
        if 'food_completed' not in data or 'activity_completed' not in data:
            print(f"TEST - Missing check-in data")
            return jsonify({'error': 'Missing food_completed or activity_completed'}), 400
        
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
            # Untuk test mode, kita bisa perbarui existing checkin
            return jsonify({
                'error': 'Already checked in today',
                'message': 'Anda sudah melakukan check-in untuk hari ini',
                'checkin': existing_checkin.to_dict()
            }), 400
        else:
            # Create checkin record
            checkin = DailyCheckin(
                user_id=user_id,
                recommendation_id=recommendation.id,
                date=today,
                food_completed=data['food_completed'],
                activity_completed=data['activity_completed']
            )
            db.session.add(checkin)
        
        # Update recommendation completion status
        recommendation.is_completed = data['food_completed'] and data['activity_completed']
        
        db.session.commit()
        
        # Calculate next day's recommendation
        tomorrow = date.today() + timedelta(days=1)
        next_day_recommendation = None
        
        # Check if tomorrow's recommendation already exists
        existing_recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=tomorrow
        ).first()
        
        # If both food and activities were completed, keep existing recommendation as is
        if data['food_completed'] and data['activity_completed']:
            next_day_recommendation = existing_recommendation
            print(f"TEST - All activities completed, keeping recommendation as is")
        else:
            # Get user profile
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                print(f"TEST - User {user_id} has no profile")
                return jsonify({'error': 'User profile not found'}), 404
                
            # Get recommendations for the past week to analyze progress
            past_week = today - timedelta(days=7)
            past_recommendations = DailyRecommendation.query.filter(
                DailyRecommendation.user_id == user_id,
                DailyRecommendation.date >= past_week,
                DailyRecommendation.date <= today
            ).all()
            
            past_checkins = DailyCheckin.query.filter(
                DailyCheckin.user_id == user_id,
                DailyCheckin.date >= past_week,
                DailyCheckin.date <= today
            ).all()
            
            # Convert to dictionary for easier lookup
            checkin_dict = {c.date: c for c in past_checkins}
            
            # Calculate adherence metrics
            days_passed = len(past_recommendations)
            successful_days = sum(1 for r in past_recommendations if 
                                 r.date in checkin_dict and 
                                 checkin_dict[r.date].food_completed and 
                                 checkin_dict[r.date].activity_completed)
            
            print(f"TEST - Adherence: {successful_days}/{days_passed} days successful")
            
            # Create a recommendation engine instance
            ml_engine_local = AdvancedRecommendationEngine()
            
            # Calculate new target calories based on adherence
            user_profile_dict = profile.to_dict()
            
            # Calculate remaining days in the diet plan (assume 30 days total)
            start_date = profile.created_at.date() if profile.created_at else today - timedelta(days=3)  # Default to 3 days ago for testing
            diet_duration = 30  # Default to 30 days
            days_elapsed = (today - start_date).days
            days_remaining = max(1, diet_duration - days_elapsed)
            
            print(f"TEST - Diet progress: Day {days_elapsed + 1} of {diet_duration} ({days_remaining} days remaining)")
            
            # Adjust for missed days
            if days_passed > 0 and successful_days < days_passed:
                print(f"TEST - Recalculating recommendations due to missed activities")
                # Get original target calories (before any adjustments)
                bmr = ml_engine_local.calculate_bmr(
                    user_profile_dict['weight'],
                    user_profile_dict['height'],
                    user_profile_dict['age'],
                    user_profile_dict['gender']
                )
                
                tdee = ml_engine_local.calculate_tdee(bmr, user_profile_dict['activity_level'])
                
                # Calculate base target calories
                original_target = ml_engine_local.calculate_target_calories(
                    user_profile_dict['weight'],
                    user_profile_dict['goal_weight'],
                    tdee,
                    timeframe=diet_duration,
                    gender=user_profile_dict['gender']
                )
                
                # Adjust for missed days
                adjusted_target = ml_engine_local.adjust_target_calories_for_missed_days(
                    original_target,
                    user_profile_dict['weight'],
                    user_profile_dict['goal_weight'],
                    days_passed,
                    successful_days,
                    days_remaining,
                    tdee,
                    gender=user_profile_dict['gender']
                )
                
                print(f"TEST - Calories adjusted: {original_target:.0f} -> {adjusted_target:.0f}")
                
                # Generate new recommendation with adjusted calories
                recommendation_data = ml_engine_local.generate_daily_recommendation(
                    user_profile_dict,
                    user_id=user_id,
                    day_in_plan=days_elapsed + 1,
                    plan_length=diet_duration,
                    previous_days=[]
                )
                
                # Create or update recommendation for tomorrow
                if existing_recommendation:
                    # Update existing
                    existing_recommendation.breakfast = json.dumps(recommendation_data['meals']['breakfast'])
                    existing_recommendation.lunch = json.dumps(recommendation_data['meals']['lunch'])
                    existing_recommendation.dinner = json.dumps(recommendation_data['meals']['dinner'])
                    existing_recommendation.activities = json.dumps(recommendation_data['activities'])
                    existing_recommendation.total_calories = recommendation_data['meals']['total_calories']
                    existing_recommendation.target_calories = recommendation_data['meals']['target_calories']
                    next_day_recommendation = existing_recommendation
                    print(f"TEST - Updated recommendation for tomorrow")
                else:
                    # Create new
                    next_day_recommendation = DailyRecommendation(
                        user_id=user_id,
                        date=tomorrow,
                        breakfast=json.dumps(recommendation_data['meals']['breakfast']),
                        lunch=json.dumps(recommendation_data['meals']['lunch']),
                        dinner=json.dumps(recommendation_data['meals']['dinner']),
                        activities=json.dumps(recommendation_data['activities']),
                        total_calories=recommendation_data['meals']['total_calories'],
                        target_calories=recommendation_data['meals']['target_calories']
                    )
                    db.session.add(next_day_recommendation)
                    print(f"TEST - Created new recommendation for tomorrow")
            else:
                # All activities completed or insufficient data, keep recommendation as is
                next_day_recommendation = existing_recommendation
                print(f"TEST - Keeping existing recommendation for tomorrow")
            
            db.session.commit()
        
        # Prepare response with tomorrow's recommendation
        next_day_data = {}
        if next_day_recommendation:
            next_day_data = next_day_recommendation.to_dict()
        
        print(f"TEST - Check-in successful for user {user_id}")
        
        return jsonify({
            'message': 'Check-in successful',
            'checkin': checkin.to_dict(),
            'recommendation_updated': recommendation.is_completed,
            'next_day_recommendation': next_day_data,
            'next_date': tomorrow.isoformat(),
            'will_regenerate_tomorrow': not (data['food_completed'] and data['activity_completed'])
        }), 201
        
    except Exception as e:
        print(f"TEST - Error during check-in: {str(e)}")
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/month/<int:year>/<int:month>', methods=['GET'])
@jwt_required()
def get_month_recommendations(year, month):
    """Get recommendations for a specific month"""
    user_id = get_jwt_identity()
    
    try:
        # Validate year and month
        if not (2020 <= year <= 2050) or not (1 <= month <= 12):
            return jsonify({'error': 'Invalid year or month'}), 400
            
        # Get the first and last day of the month
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Query recommendations for the month
        recommendations = DailyRecommendation.query.filter(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.date >= start_date,
            DailyRecommendation.date <= end_date
        ).all()
        
        # Get check-ins for the month
        checkins = DailyCheckin.query.filter(
            DailyCheckin.user_id == user_id,
            DailyCheckin.date >= start_date,
            DailyCheckin.date <= end_date
        ).all()
        
        # Create a lookup dictionary for checkins based on recommendation_id
        checkin_dict = {c.recommendation_id: c for c in checkins}
        
        # Convert recommendations to dict and add checkin data
        result = []
        for rec in recommendations:
            rec_dict = rec.to_dict()
            
            # Add checkin data if exists for this specific recommendation
            if rec.id in checkin_dict:
                checkin = checkin_dict[rec.id]
                rec_dict['checkin'] = {
                    'food_completed': checkin.food_completed,
                    'activity_completed': checkin.activity_completed
                }
            
            result.append(rec_dict)
        
        return jsonify({
            'status': 'success',
            'recommendations': result
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting month recommendations: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/day/<string:date_str>', methods=['GET'])
@jwt_required()
def get_day_recommendation(date_str):
    """Get recommendation for a specific day"""
    user_id = get_jwt_identity()
    
    try:
        # Parse date from string (format: YYYY-MM-DD)
        try:
            from datetime import datetime
            req_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Query recommendation for the day
        recommendation = DailyRecommendation.query.filter_by(
            user_id=user_id,
            date=req_date
        ).first()
        
        if not recommendation:
            return jsonify({
                'status': 'not_found',
                'message': f'No recommendation found for {date_str}'
            }), 404
            
        # Get check-in for this specific recommendation
        checkin = DailyCheckin.query.filter_by(
            user_id=user_id,
            recommendation_id=recommendation.id,
            date=req_date
        ).first()
        
        result = recommendation.to_dict()
        
        # Add checkin data if exists
        if checkin:
            checkin_data = {
                'food_completed': checkin.food_completed,
                'activity_completed': checkin.activity_completed
            }
        else:
            checkin_data = {
                'food_completed': False,
                'activity_completed': False
            }
        
        return jsonify({
            'status': 'success',
            'recommendation': result,
            'checkin': checkin_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting day recommendation: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/generate_for_date', methods=['POST'])
@jwt_required()
def generate_for_date():
    """Generate a recommendation for a specific date"""
    user_id = get_jwt_identity()
    
    try:
        data = request.get_json()
        if not data or 'date' not in data:
            return jsonify({'error': 'Date parameter is required'}), 400
            
        # Parse date from string (format: YYYY-MM-DD)
        try:
            req_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
        # Check if user exists and has a profile
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
            
        # Check if recommendation already exists for this date
        existing_rec = DailyRecommendation.query.filter_by(
            user_id=user_id, 
            date=req_date
        ).first()
        
        if existing_rec:
            # Return existing recommendation
            return jsonify({
                'status': 'exists',
                'recommendation': existing_rec.to_dict(),
                'message': f'Recommendation for {data["date"]} already exists'
            }), 200
            
        # Generate new recommendation
        user_profile_dict = user.profile.to_dict()
        recommendation_data = ml_engine.generate_daily_recommendation(user_profile_dict)
        
        # Save to database
        new_recommendation = DailyRecommendation(
            user_id=user_id,
            date=req_date,
            breakfast=json.dumps(recommendation_data['meals']['breakfast']),
            lunch=json.dumps(recommendation_data['meals']['lunch']),
            dinner=json.dumps(recommendation_data['meals']['dinner']),
            activities=json.dumps(recommendation_data['activities']),
            total_calories=recommendation_data['meals']['total_calories'],
            target_calories=recommendation_data['meals']['target_calories']
        )
        
        db.session.add(new_recommendation)
        db.session.commit()
        
        return jsonify({
            'status': 'created',
            'recommendation': new_recommendation.to_dict(),
            'message': f'Created new recommendation for {data["date"]}'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error generating recommendation for date: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/generate_month_ahead', methods=['POST'])
@jwt_required()
def generate_month_ahead():
    """Generate recommendations for the entire month ahead"""
    user_id = get_jwt_identity()
    
    try:
        # Check if user exists and has a profile
        user = User.query.get(user_id)
        if not user or not user.profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Start from tomorrow
        start_date = date.today() + timedelta(days=1)
        
        # Generate for 30 days ahead
        end_date = start_date + timedelta(days=30)
        
        current_date = start_date
        created_recommendations = []
        existing_recommendations = []
        
        while current_date <= end_date:
            # Check if recommendation already exists for this date
            existing_rec = DailyRecommendation.query.filter_by(
                user_id=user_id, 
                date=current_date
            ).first()
            
            if existing_rec:
                existing_recommendations.append({
                    'date': current_date.isoformat(),
                    'id': existing_rec.id
                })
            else:
                # Generate new recommendation
                user_profile_dict = user.profile.to_dict()
                recommendation_data = ml_engine.generate_daily_recommendation(user_profile_dict)
                
                # Save to database
                new_recommendation = DailyRecommendation(
                    user_id=user_id,
                    date=current_date,
                    breakfast=json.dumps(recommendation_data['meals']['breakfast']),
                    lunch=json.dumps(recommendation_data['meals']['lunch']),
                    dinner=json.dumps(recommendation_data['meals']['dinner']),
                    activities=json.dumps(recommendation_data['activities']),
                    total_calories=recommendation_data['meals']['total_calories'],
                    target_calories=recommendation_data['meals']['target_calories']
                )
                
                db.session.add(new_recommendation)
                created_recommendations.append({
                    'date': current_date.isoformat()
                })
            
            current_date += timedelta(days=1)
        
        # Commit all changes at once
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'created': len(created_recommendations),
            'already_existed': len(existing_recommendations),
            'created_dates': created_recommendations,
            'message': 'Successfully generated recommendations for the next 30 days'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating month ahead: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500