import pandas as pd
import numpy as np
from track_configs import TRACK_CONFIGS

def extract_corner_data(telemetry, target_distance, window=100):
    distance_col = None
    for col in ['lapdist_dls', 'trigger_lapdist_dls', 'Lap', 'distance']:
        if col in telemetry.columns:
            distance_col = col
            break
    
    if distance_col is None:
        return None
    
    telemetry_clean = telemetry.dropna(subset=[distance_col])
    
    if len(telemetry_clean) == 0:
        return None
    
    nearby = telemetry_clean[
        (telemetry_clean[distance_col] >= target_distance - window) &
        (telemetry_clean[distance_col] <= target_distance + window)
    ]
    
    if len(nearby) < 5:
        return None
    
    return nearby.sort_values(distance_col)

def analyze_corner_steering_brake(corner_data):
    result = {'data_points': len(corner_data)}
    if 'steering_angle' in corner_data.columns:
        steering = np.abs(corner_data['steering_angle'].dropna())
        if len(steering) > 0:
            result['max_steering'] = steering.max()
            result['avg_steering'] = steering.mean()
    if 'pbrake_f' in corner_data.columns:
        braking = corner_data['pbrake_f'].dropna()
        if len(braking) > 0:
            result['max_brake'] = braking.max()
            result['avg_brake'] = braking.mean()
    if 'ath' in corner_data.columns:
        throttle = corner_data['ath'].dropna()
        if len(throttle) > 0:
            result['min_throttle'] = throttle.min()
    if 'speed' in corner_data.columns:
        speed = corner_data['speed'].dropna()
        if len(speed) > 0:
            result['min_speed'] = speed.min()
            result['max_speed'] = speed.max()
    return result

def compare_corner_performance(corner_a, corner_b):
    comparison = {}
    if 'max_steering' in corner_a and 'max_steering' in corner_b:
        comparison['steering_delta'] = corner_a['max_steering'] - corner_b['max_steering']
        comparison['max_steering_a'] = corner_a['max_steering']
        comparison['max_steering_b'] = corner_b['max_steering']
    if 'max_brake' in corner_a and 'max_brake' in corner_b:
        comparison['brake_delta'] = corner_a['max_brake'] - corner_b['max_brake']
        comparison['max_brake_a'] = corner_a['max_brake']
        comparison['max_brake_b'] = corner_b['max_brake']
    if 'min_speed' in corner_a and 'min_speed' in corner_b:
        comparison['speed_delta'] = corner_a['min_speed'] - corner_b['min_speed']
        comparison['min_speed_a'] = corner_a['min_speed']
        comparison['min_speed_b'] = corner_b['min_speed']
    return comparison

def compare_laps_by_track(telemetry_a, telemetry_b, track_name='barber'):
    corners = TRACK_CONFIGS[track_name]['corners']
    comparison = {
        'summary': {'total_corners': len(corners), 'corners_analyzed': 0, 'corners_with_speed': 0},
        'corners': []
    }
    steering_deltas = []
    brake_deltas = []
    for corner_def in corners:
        corner_data_a = extract_corner_data(telemetry_a, corner_def['apex_dist_m'])
        corner_data_b = extract_corner_data(telemetry_b, corner_def['apex_dist_m'])
        corner_comparison = {
            'name': corner_def['name'],
            'expected_distance': corner_def['apex_dist_m'],
            'type': corner_def['type']
        }
        if corner_data_a is not None and corner_data_b is not None:
            corner_a = analyze_corner_steering_brake(corner_data_a)
            corner_b = analyze_corner_steering_brake(corner_data_b)
            perf_comp = compare_corner_performance(corner_a, corner_b)
            if perf_comp:
                corner_comparison.update(perf_comp)
                corner_comparison['data_available'] = True
                comparison['summary']['corners_analyzed'] += 1
                if 'steering_delta' in perf_comp:
                    steering_deltas.append(perf_comp['steering_delta'])
                if 'brake_delta' in perf_comp:
                    brake_deltas.append(perf_comp['brake_delta'])
                if perf_comp.get('min_speed_a') and perf_comp.get('min_speed_b'):
                    comparison['summary']['corners_with_speed'] += 1
        else:
            corner_comparison['data_available'] = False
        comparison['corners'].append(corner_comparison)
    if steering_deltas:
        comparison['summary']['avg_steering_delta'] = np.mean(steering_deltas)
    if brake_deltas:
        comparison['summary']['avg_brake_delta'] = np.mean(brake_deltas)
    return comparison