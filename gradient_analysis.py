import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def calculate_input_derivatives(telemetry, window=5):
    telemetry = telemetry.copy()
    
    if 'steering_angle' in telemetry.columns:
        steering_smooth = savgol_filter(telemetry['steering_angle'].fillna(0), 
                                       window_length=min(window, len(telemetry)-1 if len(telemetry) % 2 == 0 else len(telemetry)), 
                                       polyorder=2)
        telemetry['steering_derivative'] = np.gradient(steering_smooth)
        telemetry['steering_derivative_2'] = np.gradient(telemetry['steering_derivative'])
    
    if 'pbrake_f' in telemetry.columns:
        brake_smooth = savgol_filter(telemetry['pbrake_f'].fillna(0), 
                                    window_length=min(window, len(telemetry)-1 if len(telemetry) % 2 == 0 else len(telemetry)), 
                                    polyorder=2)
        telemetry['brake_derivative'] = np.gradient(brake_smooth)
    
    if 'ath' in telemetry.columns:
        throttle_smooth = savgol_filter(telemetry['ath'].fillna(0), 
                                       window_length=min(window, len(telemetry)-1 if len(telemetry) % 2 == 0 else len(telemetry)), 
                                       polyorder=2)
        telemetry['throttle_derivative'] = np.gradient(throttle_smooth)
    
    return telemetry

def classify_driver_behavior_by_gradient(corner_data_a, corner_data_b, vehicle_a_id='A', vehicle_b_id='B', 
                                         top_speed_a=None, top_speed_b=None):
    corner_a = calculate_input_derivatives(corner_data_a)
    corner_b = calculate_input_derivatives(corner_data_b)
    
    classification = {
        'type': 'normal',
        'description': 'Similar driving approach',
        'confidence': 0.0,
        'evidence': []
    }
    
    if 'steering_derivative' not in corner_a.columns or 'steering_derivative' not in corner_b.columns:
        return classification
    
    steering_grad_a = corner_a['steering_derivative'].abs()
    steering_grad_b = corner_b['steering_derivative'].abs()
    
    steering_grad_2_a = corner_a['steering_derivative_2'].abs() if 'steering_derivative_2' in corner_a.columns else pd.Series([0])
    steering_grad_2_b = corner_b['steering_derivative_2'].abs() if 'steering_derivative_2' in corner_b.columns else pd.Series([0])
    
    max_grad_a = steering_grad_a.max()
    max_grad_b = steering_grad_b.max()
    
    std_grad_a = steering_grad_a.std()
    std_grad_b = steering_grad_b.std()
    
    spikiness_a = steering_grad_2_a.max()
    spikiness_b = steering_grad_2_b.max()
    
    if spikiness_a > spikiness_b * 2 and max_grad_a > max_grad_b * 1.5:
        confidence = min((spikiness_a / (spikiness_b + 1)) / 10, 0.95)
        
        if top_speed_a is not None and top_speed_b is not None and top_speed_a < top_speed_b:
            confidence = min(confidence + 0.05, 0.98)
        
        classification = {
            'type': 'driver_mistake',
            'vehicle': 'A',
            'description': f'{vehicle_a_id} made a sudden steering correction, likely due to missed braking point or compromised corner entry',
            'confidence': confidence,
            'evidence': [
                f'Steering correction: {spikiness_a:.2f} rate-of-change vs {spikiness_b:.2f} on reference (2x higher)',
                f'Peak steering input: {max_grad_a:.2f}°/m vs {max_grad_b:.2f}°/m (1.5x higher)',
                f'Indicates: Late braking or missed turn-in point requiring correction'
            ]
        }
        
        if top_speed_a is not None and top_speed_b is not None:
            classification['evidence'].append(f'Top speed: {top_speed_a:.1f} km/h vs {top_speed_b:.1f} km/h')
    
    elif spikiness_b > spikiness_a * 2 and max_grad_b > max_grad_a * 1.5:
        confidence = min((spikiness_b / (spikiness_a + 1)) / 10, 0.95)
        
        if top_speed_a is not None and top_speed_b is not None and top_speed_b < top_speed_a:
            confidence = min(confidence + 0.05, 0.98)
        
        classification = {
            'type': 'driver_mistake',
            'vehicle': 'B',
            'description': f'{vehicle_b_id} made a sudden steering correction, likely due to missed braking point or compromised corner entry',
            'confidence': confidence,
            'evidence': [
                f'Steering correction: {spikiness_b:.2f} rate-of-change vs {spikiness_a:.2f} on reference (2x higher)',
                f'Peak steering input: {max_grad_b:.2f}°/m vs {max_grad_a:.2f}°/m (1.5x higher)',
                f'Indicates: Late braking or missed turn-in point requiring correction'
            ]
        }
        
        if top_speed_a is not None and top_speed_b is not None:
            classification['evidence'].append(f'Top speed: {top_speed_a:.1f} km/h vs {top_speed_b:.1f} km/h')
    
    elif abs(max_grad_a - max_grad_b) > 5 and abs(std_grad_a - std_grad_b) < 2:
        faster_vehicle = 'A' if max_grad_a < max_grad_b else 'B'
        faster_vehicle_id = vehicle_a_id if faster_vehicle == 'A' else vehicle_b_id
        slower_vehicle_id = vehicle_b_id if faster_vehicle == 'A' else vehicle_a_id
        smoother_grad = max_grad_a if faster_vehicle == 'A' else max_grad_b
        sharper_grad = max_grad_b if faster_vehicle == 'A' else max_grad_a
        classification = {
            'type': 'different_line',
            'vehicle': faster_vehicle,
            'description': f'{slower_vehicle_id} using different racing line with sharper steering inputs vs {faster_vehicle_id} smoother approach',
            'confidence': min(abs(max_grad_a - max_grad_b) / 20, 0.85),
            'evidence': [
                f'Steering profile difference: {sharper_grad:.2f}°/m vs {smoother_grad:.2f}°/m',
                f'Both controlled (similar variability: {std_grad_a:.2f} vs {std_grad_b:.2f})',
                f'Indicates: Intentional line choice, not a mistake'
            ]
        }
    
    if 'brake_derivative' in corner_a.columns and 'brake_derivative' in corner_b.columns:
        brake_grad_a = corner_a['brake_derivative'].abs()
        brake_grad_b = corner_b['brake_derivative'].abs()
        
        max_brake_grad_a = brake_grad_a.max()
        max_brake_grad_b = brake_grad_b.max()
        
        if abs(max_brake_grad_a - max_brake_grad_b) > 10:
            if classification['type'] == 'normal':
                smoother_vehicle = 'A' if max_brake_grad_a < max_brake_grad_b else 'B'
                sharper_vehicle = 'B' if smoother_vehicle == 'A' else 'A'
                smoother_vehicle_id = vehicle_a_id if smoother_vehicle == 'A' else vehicle_b_id
                sharper_vehicle_id = vehicle_b_id if smoother_vehicle == 'A' else vehicle_a_id
                smoother_brake = max_brake_grad_a if smoother_vehicle == 'A' else max_brake_grad_b
                sharper_brake = max_brake_grad_b if smoother_vehicle == 'A' else max_brake_grad_a
                classification = {
                    'type': 'brake_technique',
                    'vehicle': smoother_vehicle,
                    'description': f'{sharper_vehicle_id} using sharper brake inputs vs {smoother_vehicle_id} progressive braking',
                    'confidence': min(abs(max_brake_grad_a - max_brake_grad_b) / 50, 0.80),
                    'evidence': [
                        f'Brake application: {sharper_brake:.2f} bar/m vs {smoother_brake:.2f} bar/m',
                        f'Smoother braking typically yields better tire grip and corner entry stability'
                    ]
                }
            else:
                classification['evidence'].append(f'Brake difference detected: {max_brake_grad_a:.2f} vs {max_brake_grad_b:.2f} bar/m')
    
    return classification

def generate_gradient_based_recommendations(classification, corner_comparison):
    if classification['type'] == 'normal':
        return []
    
    vehicle_a_id = corner_comparison.get('vehicle_a_id', 'A')
    vehicle_b_id = corner_comparison.get('vehicle_b_id', 'B')
    
    recommendations = []
    
    if classification['type'] == 'driver_mistake':
        vehicle = classification['vehicle']
        vehicle_id = vehicle_a_id if vehicle == 'A' else vehicle_b_id
        recommendations.append({
            'vehicle': vehicle_id,
            'issue': 'Steering correction/mistake detected',
            'recommendation': 'Focus on smoother initial turn-in to avoid mid-corner corrections. Practice consistency in entry speed and brake point.',
            'priority': 'high',
            'confidence': classification['confidence'],
            'evidence': classification['evidence']
        })
    
    elif classification['type'] == 'different_line':
        vehicle = classification['vehicle']
        vehicle_id = vehicle_a_id if vehicle == 'A' else vehicle_b_id
        other_vehicle_id = vehicle_b_id if vehicle == 'A' else vehicle_a_id
        recommendations.append({
            'vehicle': other_vehicle_id,
            'issue': 'Suboptimal racing line',
            'recommendation': f'Study Vehicle {vehicle_id}\'s smoother steering profile - indicates better line geometry through this corner.',
            'priority': 'medium',
            'confidence': classification['confidence'],
            'evidence': classification['evidence']
        })
    
    elif classification['type'] == 'brake_technique':
        vehicle = classification['vehicle']
        vehicle_id = vehicle_a_id if vehicle == 'A' else vehicle_b_id
        other_vehicle_id = vehicle_b_id if vehicle == 'A' else vehicle_a_id
        recommendations.append({
            'vehicle': other_vehicle_id,
            'issue': 'Aggressive brake application',
            'recommendation': f'Work on smoother brake release like Vehicle {vehicle_id} - reduces tire load spikes and improves rotation.',
            'priority': 'medium',
            'confidence': classification['confidence'],
            'evidence': classification['evidence']
        })
    
    return recommendations