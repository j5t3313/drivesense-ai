import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def calculate_steering_smoothness(telemetry):
    if 'steering_angle' not in telemetry.columns:
        return None
    
    steering = telemetry['steering_angle'].dropna()
    if len(steering) < 10:
        return None
    
    steering_smooth = savgol_filter(steering, 
                                   window_length=min(11, len(steering) if len(steering) % 2 == 1 else len(steering)-1),
                                   polyorder=2)
    
    steering_grad = np.gradient(steering_smooth)
    steering_jerk = np.gradient(steering_grad)
    
    jerk_magnitude = np.abs(steering_jerk).mean()
    smoothness = max(0, 100 - (jerk_magnitude * 50))
    
    return {
        'smoothness_score': smoothness,
        'avg_jerk': jerk_magnitude,
        'max_jerk': np.abs(steering_jerk).max(),
        'std_steering': steering.std()
    }

def calculate_brake_consistency(telemetry):
    if 'pbrake_f' not in telemetry.columns:
        return None
    
    brake = telemetry['pbrake_f'].dropna()
    if len(brake) < 10:
        return None
    
    brake_events = brake[brake > 10]
    
    if len(brake_events) < 5:
        return None
    
    brake_gradient = np.abs(np.gradient(brake_events))
    brake_std = brake_gradient.std()
    consistency = 100 / (1 + brake_std/25)
    
    return {
        'consistency_score': consistency,
        'avg_brake_pressure': brake_events.mean(),
        'max_brake_pressure': brake_events.max(),
        'brake_applications': len(brake_events),
        'brake_variance': brake_gradient.std()
    }

def calculate_throttle_metrics(telemetry):
    if 'ath' not in telemetry.columns:
        return None
    
    throttle = telemetry['ath'].dropna()
    if len(throttle) < 10:
        return None
    
    full_throttle_pct = (throttle > 80).mean() * 100
    avg_throttle = throttle.mean()
    throttle_variance = throttle.std()
    
    confidence = min(100, full_throttle_pct * 1.2)
    
    return {
        'confidence_score': confidence,
        'full_throttle_pct': full_throttle_pct,
        'avg_throttle': avg_throttle,
        'throttle_variance': throttle_variance
    }

def classify_driver_style(smoothness_metrics, brake_metrics, throttle_metrics):
    if not smoothness_metrics or not brake_metrics:
        return 'unknown'
    
    smoothness = smoothness_metrics['smoothness_score']
    brake_consistency = brake_metrics['consistency_score']
    
    if smoothness > 70 and brake_consistency > 70:
        return 'smooth_technical'
    elif smoothness > 70:
        return 'smooth_aggressive'
    elif brake_consistency > 70:
        return 'precise_aggressive'
    else:
        return 'developing'

def generate_aggregate_recommendations(style, smoothness_metrics, brake_metrics, throttle_metrics):
    recommendations = []
    
    if smoothness_metrics:
        smoothness = smoothness_metrics['smoothness_score']
        if smoothness < 50:
            recommendations.append({
                'category': 'Steering Smoothness',
                'priority': 'HIGH',
                'issue': f'Low smoothness score: {smoothness:.1f}/100',
                'recommendation': 'Focus on smoother steering inputs throughout the lap. Reduce mid-corner corrections and plan turn-in points earlier.',
                'evidence': f"Average jerk: {smoothness_metrics['avg_jerk']:.2f}, Max jerk: {smoothness_metrics['max_jerk']:.2f}"
            })
        elif smoothness < 70:
            recommendations.append({
                'category': 'Steering Smoothness',
                'priority': 'MEDIUM',
                'issue': f'Moderate smoothness score: {smoothness:.1f}/100',
                'recommendation': 'Work on consistency in steering application. Maintain smooth arcs through corners.',
                'evidence': f"Steering std dev: {smoothness_metrics['std_steering']:.2f}°"
            })
    
    if brake_metrics:
        consistency = brake_metrics['consistency_score']
        if consistency < 50:
            recommendations.append({
                'category': 'Brake Consistency',
                'priority': 'HIGH',
                'issue': f'Low brake consistency: {consistency:.1f}/100',
                'recommendation': 'Focus on consistent brake pressure application. Establish repeatable brake points and modulation patterns.',
                'evidence': f"Brake variance: {brake_metrics['brake_variance']:.2f} bar/s"
            })
        elif consistency < 70:
            recommendations.append({
                'category': 'Brake Consistency',
                'priority': 'MEDIUM',
                'issue': f'Moderate brake consistency: {consistency:.1f}/100',
                'recommendation': 'Refine brake release technique. Work on smoother transitions from braking to throttle.',
                'evidence': f"Average brake: {brake_metrics['avg_brake_pressure']:.1f} bar"
            })
    
    if throttle_metrics:
        confidence = throttle_metrics['confidence_score']
        if confidence < 40:
            recommendations.append({
                'category': 'Throttle Application',
                'priority': 'MEDIUM',
                'issue': f'Low throttle confidence: {confidence:.1f}/100',
                'recommendation': 'Work on earlier throttle application. Build confidence in car balance to commit to power sooner.',
                'evidence': f"Full throttle: {throttle_metrics['full_throttle_pct']:.1f}% of lap"
            })
    
    if not recommendations:
        recommendations.append({
            'category': 'Overall Performance',
            'priority': 'LOW',
            'issue': 'Strong fundamentals across all metrics',
            'recommendation': 'Continue current approach. Focus on consistency and small refinements.',
            'evidence': 'All core metrics above threshold'
        })
    
    return recommendations

def analyze_lap_comparison_aggregate(telemetry_a, telemetry_b, vehicle_a_id, vehicle_b_id):
    smoothness_a = calculate_steering_smoothness(telemetry_a)
    smoothness_b = calculate_steering_smoothness(telemetry_b)
    
    brake_a = calculate_brake_consistency(telemetry_a)
    brake_b = calculate_brake_consistency(telemetry_b)
    
    throttle_a = calculate_throttle_metrics(telemetry_a)
    throttle_b = calculate_throttle_metrics(telemetry_b)
    
    style_a = classify_driver_style(smoothness_a, brake_a, throttle_a)
    style_b = classify_driver_style(smoothness_b, brake_b, throttle_b)
    
    comparison = {
        'vehicle_a': {
            'id': vehicle_a_id,
            'smoothness': smoothness_a,
            'brake': brake_a,
            'throttle': throttle_a,
            'style': style_a,
            'recommendations': generate_aggregate_recommendations(style_a, smoothness_a, brake_a, throttle_a)
        },
        'vehicle_b': {
            'id': vehicle_b_id,
            'smoothness': smoothness_b,
            'brake': brake_b,
            'throttle': throttle_b,
            'style': style_b,
            'recommendations': generate_aggregate_recommendations(style_b, smoothness_b, brake_b, throttle_b)
        }
    }
    
    winner = None
    if smoothness_a and smoothness_b:
        avg_a = (smoothness_a['smoothness_score'] + 
                (brake_a['consistency_score'] if brake_a else 50) + 
                (throttle_a['confidence_score'] if throttle_a else 50)) / 3
        avg_b = (smoothness_b['smoothness_score'] + 
                (brake_b['consistency_score'] if brake_b else 50) + 
                (throttle_b['confidence_score'] if throttle_b else 50)) / 3
        winner = vehicle_a_id if avg_a > avg_b else vehicle_b_id
    
    comparison['summary'] = {
        'better_overall': winner,
        'analysis_type': 'aggregate'
    }
    
    return comparison

def generate_aggregate_report(comparison):
    lines = []
    lines.append("AGGREGATE LAP-LEVEL ANALYSIS")
    lines.append("=" * 80)
    lines.append("Note: Distance data unavailable - showing lap-level metrics")
    lines.append("")
    
    for vehicle_key in ['vehicle_a', 'vehicle_b']:
        vehicle = comparison[vehicle_key]
        lines.append(f"Vehicle {vehicle['id']}")
        lines.append("-" * 80)
        
        if vehicle['smoothness']:
            lines.append(f"  Steering Smoothness: {vehicle['smoothness']['smoothness_score']:.1f}/100")
            lines.append(f"    Average jerk: {vehicle['smoothness']['avg_jerk']:.2f}")
            lines.append(f"    Max jerk: {vehicle['smoothness']['max_jerk']:.2f}")
        
        if vehicle['brake']:
            lines.append(f"  Brake Consistency: {vehicle['brake']['consistency_score']:.1f}/100")
            lines.append(f"    Average pressure: {vehicle['brake']['avg_brake_pressure']:.1f} bar")
            lines.append(f"    Variance: {vehicle['brake']['brake_variance']:.2f}")
        
        if vehicle['throttle']:
            lines.append(f"  Throttle Confidence: {vehicle['throttle']['confidence_score']:.1f}/100")
            lines.append(f"    Full throttle: {vehicle['throttle']['full_throttle_pct']:.1f}% of lap")
        
        lines.append(f"  Driver Style: {vehicle['style'].replace('_', ' ').title()}")
        lines.append("")
        
        if vehicle['recommendations']:
            lines.append("  Recommendations:")
            for rec in vehicle['recommendations']:
                lines.append(f"    [{rec['priority']}] {rec['category']}")
                lines.append(f"      {rec['recommendation']}")
                lines.append(f"      Evidence: {rec['evidence']}")
                lines.append("")
        
        lines.append("")
    
    if comparison['summary']['better_overall']:
        lines.append(f"Overall: Vehicle {comparison['summary']['better_overall']} shows stronger fundamentals")
    
    return '\n'.join(lines)