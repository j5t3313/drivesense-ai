import numpy as np
import pandas as pd

def calculate_lap_time(telemetry):
    time_cols = ['timestamp', 'time', 'sessiontime', 'laptime', 'elapsed_time', 'Time']
    
    for col in time_cols:
        if col in telemetry.columns:
            try:
                timestamps = pd.to_numeric(telemetry[col], errors='coerce').dropna()
                if len(timestamps) >= 2:
                    lap_time = timestamps.max() - timestamps.min()
                    if lap_time > 0 and lap_time < 500:
                        return lap_time
            except:
                continue
    
    if 'lapdist_dls' in telemetry.columns and 'speed' in telemetry.columns:
        try:
            distance = telemetry['lapdist_dls'].dropna()
            speed = telemetry['speed'].dropna()
            if len(distance) > 10 and len(speed) > 10:
                total_distance = distance.max() - distance.min()
                avg_speed = speed.mean()
                if avg_speed > 0:
                    estimated_time = total_distance / avg_speed
                    if estimated_time > 30 and estimated_time < 500:
                        return estimated_time
        except:
            pass
    
    return None

def calculate_corner_time_delta(corner_data_a, corner_data_b):
    if corner_data_a is None or corner_data_b is None:
        return None
    
    if 'timestamp' not in corner_data_a.columns or 'timestamp' not in corner_data_b.columns:
        return None
    
    time_a = pd.to_numeric(corner_data_a['timestamp'], errors='coerce').dropna()
    time_b = pd.to_numeric(corner_data_b['timestamp'], errors='coerce').dropna()
    
    if len(time_a) < 2 or len(time_b) < 2:
        return None
    
    duration_a = time_a.max() - time_a.min()
    duration_b = time_b.max() - time_b.min()
    
    return duration_a - duration_b

def interpolate_time_at_distance(telemetry, target_distance):
    distance_col = None
    for col in ['lapdist_dls', 'trigger_lapdist_dls', 'Lap', 'distance']:
        if col in telemetry.columns:
            distance_col = col
            break
    
    if distance_col is None or 'timestamp' not in telemetry.columns:
        return None
    
    df = telemetry[[distance_col, 'timestamp']].copy()
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df = df.dropna()
    
    if len(df) < 2:
        return None
    
    df = df.sort_values(distance_col)
    
    if target_distance < df[distance_col].min() or target_distance > df[distance_col].max():
        return None
    
    return np.interp(target_distance, df[distance_col], df['timestamp'])

def calculate_time_delta_at_distance(telemetry_a, telemetry_b, distance):
    time_a = interpolate_time_at_distance(telemetry_a, distance)
    time_b = interpolate_time_at_distance(telemetry_b, distance)
    
    if time_a is None or time_b is None:
        return None
    
    return time_a - time_b

def calculate_cumulative_time_deltas(telemetry_a, telemetry_b, distance_points):
    deltas = []
    
    for dist in distance_points:
        delta = calculate_time_delta_at_distance(telemetry_a, telemetry_b, dist)
        if delta is not None:
            deltas.append({'distance': dist, 'time_delta': delta})
    
    return pd.DataFrame(deltas)