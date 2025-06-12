import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, date, timedelta
import logging
from sklearn.linear_model import LinearRegression

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('diet_analyzer.log'), logging.StreamHandler()]
)
logger = logging.getLogger('diet_analyzer')

class DietProgressAnalyzer:
    """
    Analyzes user diet and exercise adherence to track progress
    and make adjustments to their nutrition plans.
    """
    
    def __init__(self):
        """Initialize the diet progress analyzer"""
        pass
    
    def analyze_weight_progress(self, 
                               start_weight: float,
                               current_weight: float,
                               goal_weight: float,
                               days_elapsed: int,
                               total_days: int) -> Dict[str, Any]:
        """
        Analyze progress towards weight goal
        
        Args:
            start_weight: Starting weight in kg
            current_weight: Current weight in kg
            goal_weight: Target weight in kg
            days_elapsed: Days since plan started
            total_days: Total days in the plan
            
        Returns:
            Analysis of weight progress
        """
        # Calculate expected progress
        if total_days <= 0 or days_elapsed < 0:
            return {
                'status': 'invalid',
                'message': 'Invalid time parameters'
            }
        
        # If we're just starting, not enough data for analysis
        if days_elapsed < 3:
            return {
                'status': 'early',
                'message': 'Not enough data for analysis yet',
                'progress_percent': 0
            }
        
        # Calculate total weight change needed
        total_change_needed = goal_weight - start_weight
        
        if abs(total_change_needed) < 0.1:
            # Goal is to maintain weight
            weight_difference = abs(current_weight - start_weight)
            
            if weight_difference <= 1.0:
                status = 'on_track'
                message = 'Maintaining weight successfully'
            else:
                status = 'off_track'
                message = f'Weight has changed by {weight_difference:.1f} kg when goal is to maintain'
            
            return {
                'status': status,
                'message': message,
                'progress_percent': 100 if weight_difference <= 1.0 else 0
            }
        
        # Calculate expected progress at this point
        expected_change = total_change_needed * (days_elapsed / total_days)
        expected_weight = start_weight + expected_change
        
        # Calculate actual change
        actual_change = current_weight - start_weight
        
        # Calculate progress percentage (how much of the goal is achieved)
        if abs(total_change_needed) > 0:
            progress_percent = min(100, max(0, (actual_change / total_change_needed) * 100))
        else:
            progress_percent = 100
        
        # Calculate if we're on track (expected vs actual)
        if total_change_needed > 0:  # Weight gain goal
            on_track = current_weight >= expected_weight
        else:  # Weight loss goal
            on_track = current_weight <= expected_weight
        
        # Calculate the difference between expected and actual
        weight_difference = abs(current_weight - expected_weight)
        
        # Determine status and message
        if on_track:
            if weight_difference <= 1.0:
                status = 'on_track'
                message = 'Progress is on track'
            else:
                status = 'ahead'
                message = f'Progress is ahead of schedule by {weight_difference:.1f} kg'
        else:
            status = 'behind'
            message = f'Progress is behind schedule by {weight_difference:.1f} kg'
        
        # Calculate estimated completion based on current rate
        if days_elapsed > 0 and abs(actual_change) > 0:
            current_rate = actual_change / days_elapsed  # kg/day
            days_remaining_estimate = (total_change_needed - actual_change) / current_rate
            
            estimated_total_days = days_elapsed + days_remaining_estimate
            time_difference = abs(estimated_total_days - total_days)
            
            if time_difference > 7:  # More than a week difference
                if estimated_total_days < total_days:
                    eta_message = f'At current rate, goal will be achieved {time_difference:.0f} days ahead of schedule'
                else:
                    eta_message = f'At current rate, goal will be achieved {time_difference:.0f} days behind schedule'
            else:
                eta_message = 'Current pace is aligned with the goal timeline'
        else:
            eta_message = 'Not enough data to estimate completion date'
        
        return {
            'status': status,
            'message': message,
            'progress_percent': progress_percent,
            'expected_weight': expected_weight,
            'weight_difference': weight_difference,
            'eta_message': eta_message,
            'days_elapsed': days_elapsed,
            'days_remaining': total_days - days_elapsed
        }
    
    def analyze_adherence(self, 
                         checkin_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user adherence to diet and exercise plan
        
        Args:
            checkin_history: List of daily checkin data
            
        Returns:
            Adherence analysis
        """
        if not checkin_history:
            return {
                'status': 'no_data',
                'message': 'No checkin data available',
                'adherence_percent': 0,
                'food_adherence_percent': 0,
                'activity_adherence_percent': 0
            }
        
        total_days = len(checkin_history)
        completed_days = sum(1 for day in checkin_history 
                           if day.get('food_completed', False) and day.get('activity_completed', False))
        
        food_completed = sum(1 for day in checkin_history if day.get('food_completed', False))
        activity_completed = sum(1 for day in checkin_history if day.get('activity_completed', False))
        
        # Calculate adherence percentages
        adherence_percent = (completed_days / total_days) * 100 if total_days > 0 else 0
        food_adherence_percent = (food_completed / total_days) * 100 if total_days > 0 else 0
        activity_adherence_percent = (activity_completed / total_days) * 100 if total_days > 0 else 0
        
        # Determine status
        if adherence_percent >= 80:
            status = 'excellent'
            message = 'Excellent adherence to the plan'
        elif adherence_percent >= 60:
            status = 'good'
            message = 'Good adherence to the plan'
        elif adherence_percent >= 40:
            status = 'moderate'
            message = 'Moderate adherence to the plan'
        else:
            status = 'poor'
            message = 'Poor adherence to the plan'
        
        # Check for patterns
        food_adherence_better = food_adherence_percent > activity_adherence_percent + 20
        activity_adherence_better = activity_adherence_percent > food_adherence_percent + 20
        
        insight = None
        
        if food_adherence_better:
            insight = 'Diet adherence is stronger than exercise adherence'
        elif activity_adherence_better:
            insight = 'Exercise adherence is stronger than diet adherence'
        
        # Analysis of recent trend (last 7 days vs overall)
        if len(checkin_history) >= 10:
            recent_days = checkin_history[-7:]
            
            recent_completed = sum(1 for day in recent_days 
                                if day.get('food_completed', False) and day.get('activity_completed', False))
            
            recent_adherence = (recent_completed / len(recent_days)) * 100
            
            # Compare recent to overall
            if recent_adherence > adherence_percent + 10:
                trend = 'improving'
                trend_message = 'Recent adherence has improved compared to overall'
            elif recent_adherence < adherence_percent - 10:
                trend = 'declining'
                trend_message = 'Recent adherence has declined compared to overall'
            else:
                trend = 'stable'
                trend_message = 'Adherence has been consistent recently'
        else:
            trend = 'insufficient_data'
            trend_message = 'Not enough data to analyze trends'
        
        return {
            'status': status,
            'message': message,
            'adherence_percent': adherence_percent,
            'food_adherence_percent': food_adherence_percent,
            'activity_adherence_percent': activity_adherence_percent,
            'completed_days': completed_days,
            'total_days': total_days,
            'insight': insight,
            'trend': trend,
            'trend_message': trend_message
        }
    
    def predict_weight_trajectory(self,
                                weight_history: List[Tuple[date, float]],
                                days_to_predict: int = 30) -> List[Tuple[date, float]]:
        """
        Predict future weight trajectory based on past data
        
        Args:
            weight_history: List of (date, weight) tuples
            days_to_predict: Number of days to predict
            
        Returns:
            List of (date, weight) predictions
        """
        if not weight_history or len(weight_history) < 3:
            return []
        
        # Convert dates to days since start
        start_date = weight_history[0][0]
        
        X = np.array([(d[0] - start_date).days for d in weight_history]).reshape(-1, 1)
        y = np.array([d[1] for d in weight_history])
        
        # Create and fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future weights
        last_day = X[-1][0]
        future_days = np.array(range(last_day + 1, last_day + days_to_predict + 1)).reshape(-1, 1)
        
        predictions = model.predict(future_days)
        
        # Convert back to dates
        result = [(start_date + timedelta(days=int(day)), weight) 
                for day, weight in zip(future_days, predictions)]
        
        return result
    
    def calculate_calories_adjustment(self,
                                    current_weight: float, 
                                    target_weight: float,
                                    current_calories: float,
                                    days_remaining: int,
                                    adherence_percent: float) -> Dict[str, Any]:
        """
        Calculate calories adjustment based on progress and adherence
        
        Args:
            current_weight: Current weight in kg
            target_weight: Target weight in kg
            current_calories: Current daily caloric intake
            days_remaining: Days remaining in the plan
            adherence_percent: Plan adherence percentage
            
        Returns:
            Recommended caloric adjustment
        """
        # Weight difference remaining
        weight_diff = target_weight - current_weight
        
        # No significant difference, maintain current calories
        if abs(weight_diff) < 0.2:
            return {
                'new_calories': current_calories,
                'adjustment': 0,
                'message': 'Weight on target, maintain current caloric intake'
            }
        
        # Calculate calories per day needed to reach goal
        # Each kg of weight change requires approximately 7700 calories
        calories_needed = weight_diff * 7700
        
        # Adjust for adherence (if adherence is low, set more aggressive targets)
        adherence_factor = max(0.5, adherence_percent / 100)  # Minimum 0.5
        
        # Calculate daily calorie adjustment needed
        if days_remaining > 0:
            daily_calories_adjustment = calories_needed / (days_remaining * adherence_factor)
            
            # Limit adjustments to reasonable values
            max_adjustment = 500 if weight_diff < 0 else 300
            daily_calories_adjustment = max(min(daily_calories_adjustment, max_adjustment), -max_adjustment)
            
            new_calories = current_calories + daily_calories_adjustment
            
            # Ensure minimum healthy caloric intake
            min_calories = 1200  # Minimum healthy intake
            new_calories = max(new_calories, min_calories)
            
            adjustment = new_calories - current_calories
            
            if abs(adjustment) < 50:
                message = 'Minor adjustment recommended to stay on track'
            elif adjustment > 0:
                message = 'Increase caloric intake to meet weight gain goals'
            else:
                message = 'Reduce caloric intake to meet weight loss goals'
                
            return {
                'new_calories': round(new_calories),
                'adjustment': round(adjustment),
                'message': message
            }
        else:
            return {
                'new_calories': current_calories,
                'adjustment': 0,
                'message': 'No days remaining in plan'
            }
    
    def analyze_nutritional_balance(self, 
                                  meal_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze nutritional balance from meal history
        
        Args:
            meal_history: List of daily meal data
            
        Returns:
            Nutritional analysis
        """
        if not meal_history:
            return {
                'status': 'no_data',
                'message': 'No meal data available'
            }
        
        # Collect macronutrient ratios
        macros = []
        
        for day in meal_history:
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal = day.get(meal_type, {})
                if isinstance(meal, str):
                    try:
                        meal = json.loads(meal)
                    except:
                        continue
                
                total_calories += meal.get('calories', 0)
                total_protein += meal.get('protein', 0)
                total_carbs += meal.get('carbs', 0)
                total_fat += meal.get('fat', 0)
            
            if total_calories > 0:
                # Calculate macronutrient percentages
                protein_cals = total_protein * 4
                carb_cals = total_carbs * 4
                fat_cals = total_fat * 9
                
                protein_percent = (protein_cals / total_calories) * 100
                carb_percent = (carb_cals / total_calories) * 100
                fat_percent = (fat_cals / total_calories) * 100
                
                macros.append({
                    'protein_percent': protein_percent,
                    'carb_percent': carb_percent,
                    'fat_percent': fat_percent
                })
        
        if not macros:
            return {
                'status': 'insufficient_data',
                'message': 'Could not calculate macronutrient distribution'
            }
        
        # Calculate average macro distribution
        avg_protein = sum(m['protein_percent'] for m in macros) / len(macros)
        avg_carbs = sum(m['carb_percent'] for m in macros) / len(macros)
        avg_fat = sum(m['fat_percent'] for m in macros) / len(macros)
        
        # Evaluate balance based on common recommendations
        # Protein: 10-35%, Carbs: 45-65%, Fat: 20-35%
        protein_status = 'optimal' if 15 <= avg_protein <= 35 else ('low' if avg_protein < 15 else 'high')
        carb_status = 'optimal' if 45 <= avg_carbs <= 65 else ('low' if avg_carbs < 45 else 'high')
        fat_status = 'optimal' if 20 <= avg_fat <= 35 else ('low' if avg_fat < 20 else 'high')
        
        # Generate recommendations
        recommendations = []
        
        if protein_status == 'low':
            recommendations.append('Consider increasing protein intake (lean meat, fish, legumes)')
        elif protein_status == 'high':
            recommendations.append('Consider moderating protein intake')
        
        if carb_status == 'low':
            recommendations.append('Consider increasing complex carbohydrates (whole grains, fruits)')
        elif carb_status == 'high':
            recommendations.append('Consider reducing simple carbohydrates (sugars, refined grains)')
        
        if fat_status == 'low':
            recommendations.append('Consider increasing healthy fats (avocados, nuts, olive oil)')
        elif fat_status == 'high':
            recommendations.append('Consider reducing fat intake, especially saturated fats')
        
        return {
            'status': 'analyzed',
            'avg_protein_percent': round(avg_protein, 1),
            'avg_carb_percent': round(avg_carbs, 1),
            'avg_fat_percent': round(avg_fat, 1),
            'protein_status': protein_status,
            'carb_status': carb_status,
            'fat_status': fat_status,
            'recommendations': recommendations
        }
    
    def generate_comprehensive_analysis(self,
                                      user_profile: Dict[str, Any],
                                      start_date: date,
                                      current_date: date,
                                      end_date: date,
                                      weight_history: List[Tuple[date, float]],
                                      meal_history: List[Dict[str, Any]],
                                      checkin_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis of user's diet progress
        
        Args:
            user_profile: User profile data
            start_date: Start date of the plan
            current_date: Current date
            end_date: End date of the plan
            weight_history: List of (date, weight) tuples
            meal_history: List of daily meal data
            checkin_history: List of daily checkin data
            
        Returns:
            Comprehensive progress analysis
        """
        # Calculate days elapsed and total days
        days_elapsed = (current_date - start_date).days
        total_days = (end_date - start_date).days
        days_remaining = (end_date - current_date).days
        
        # Get the most recent weight
        current_weight = user_profile.get('weight')
        if weight_history:
            weight_history.sort(key=lambda x: x[0])
            current_weight = weight_history[-1][1]
        
        start_weight = user_profile.get('weight')  # Default to current if history not available
        if weight_history and len(weight_history) > 0:
            # Find the weight closest to the start date
            weight_history.sort(key=lambda x: abs((x[0] - start_date).days))
            start_weight = weight_history[0][1]
        
        # Goal weight from user profile
        goal_weight = user_profile.get('goal_weight', start_weight)
        
        # Calculate weight progress
        weight_progress = self.analyze_weight_progress(
            start_weight,
            current_weight,
            goal_weight,
            days_elapsed,
            total_days
        )
        
        # Analyze adherence
        adherence = self.analyze_adherence(checkin_history)
        
        # Analyze nutrition
        nutrition = self.analyze_nutritional_balance(meal_history)
        
        # Predict weight trajectory if enough data
        trajectory = []
        if len(weight_history) >= 3:
            trajectory = self.predict_weight_trajectory(
                weight_history,
                days_to_predict=min(30, days_remaining)
            )
        
        # Current caloric intake
        current_calories = 0
        if meal_history:
            recent_meals = meal_history[-min(7, len(meal_history)):]
            total_calories = sum(m.get('total_calories', 0) for m in recent_meals)
            current_calories = total_calories / len(recent_meals) if recent_meals else 0
        
        # Calculate caloric adjustment if needed
        caloric_adjustment = self.calculate_calories_adjustment(
            current_weight,
            goal_weight,
            current_calories,
            days_remaining,
            adherence.get('adherence_percent', 0)
        )
        
        # Generate overall assessment
        if weight_progress.get('status') in ['on_track', 'ahead']:
            if adherence.get('adherence_percent', 0) >= 70:
                overall_status = 'excellent'
                overall_message = 'Excellent progress, keep up the good work!'
            else:
                overall_status = 'good'
                overall_message = 'Good progress overall, but try to improve plan adherence'
        else:
            if adherence.get('adherence_percent', 0) >= 70:
                overall_status = 'mixed'
                overall_message = 'Good adherence, but progress is behind schedule'
            else:
                overall_status = 'needs_improvement'
                overall_message = 'Both progress and adherence need improvement'
        
        return {
            'overall_status': overall_status,
            'overall_message': overall_message,
            'weight_progress': weight_progress,
            'adherence': adherence,
            'nutrition': nutrition,
            'caloric_adjustment': caloric_adjustment,
            'weight_trajectory': [{'date': d.isoformat(), 'weight': w} for d, w in trajectory],
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'total_days': total_days,
            'progress_percent': (days_elapsed / total_days) * 100 if total_days > 0 else 0,
            'generated_at': datetime.now().isoformat()
        } 