import pandas as pd
from pathlib import Path

def load_lap_times_from_file(lap_time_file):
    try:
        if lap_time_file.suffix == '.CSV' or 'Endurance' in str(lap_time_file):
            return load_endurance_file(lap_time_file)
        
        df = pd.read_csv(lap_time_file)
        
        if 'timestamp' not in df.columns or 'vehicle_id' not in df.columns or 'lap' not in df.columns:
            return None
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(['vehicle_id', 'lap'])
        
        lap_times = {}
        
        for vehicle in df['vehicle_id'].unique():
            vehicle_data = df[df['vehicle_id'] == vehicle].copy()
            vehicle_data['lap_time'] = vehicle_data['timestamp'].diff().dt.total_seconds()
            
            lap_times[vehicle] = {}
            for idx, row in vehicle_data.iterrows():
                if not pd.isna(row['lap_time']) and row['lap_time'] > 0 and row['lap_time'] < 500:
                    lap_times[vehicle][int(row['lap'])] = float(row['lap_time'])
        
        return lap_times
    except Exception as e:
        print(f"Error loading lap times: {e}")
        return None

def load_endurance_file(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
        
        required_cols = ['NUMBER', 'LAP_NUMBER', 'LAP_TIME', 'KPH', 'TOP_SPEED']
        if not all(col in df.columns for col in required_cols):
            return None
        
        lap_times = {}
        vehicle_number_map = {}
        
        for _, row in df.iterrows():
            vehicle_num = int(row['NUMBER'])
            lap_num = int(row['LAP_NUMBER'])
            
            if vehicle_num not in vehicle_number_map:
                vehicle_number_map[vehicle_num] = []
            
            lap_time_str = str(row['LAP_TIME'])
            lap_time_seconds = None
            if ':' in lap_time_str:
                parts = lap_time_str.split(':')
                if len(parts) == 2:
                    try:
                        minutes = float(parts[0])
                        seconds = float(parts[1])
                        lap_time_seconds = minutes * 60 + seconds
                    except:
                        pass
            
            lap_data = {
                'time': lap_time_seconds,
                'lap_time': lap_time_seconds,
                'time_str': lap_time_str,
                'kph': float(row['KPH']) if pd.notna(row['KPH']) else None,
                'top_speed': float(row['TOP_SPEED']) if pd.notna(row['TOP_SPEED']) else None,
                's1': float(row['S1_SECONDS']) if 'S1_SECONDS' in row and pd.notna(row['S1_SECONDS']) else None,
                's2': float(row['S2_SECONDS']) if 'S2_SECONDS' in row and pd.notna(row['S2_SECONDS']) else None,
                's3': float(row['S3_SECONDS']) if 'S3_SECONDS' in row and pd.notna(row['S3_SECONDS']) else None,
                'flag': str(row['FLAG_AT_FL']) if 'FLAG_AT_FL' in row and pd.notna(row['FLAG_AT_FL']) else 'Unknown',
                'vehicle_number': vehicle_num
            }
            
            vehicle_number_map[vehicle_num].append({
                'lap': lap_num,
                'data': lap_data
            })
        
        for vehicle_num, laps in vehicle_number_map.items():
            for lap_entry in laps:
                lap_num = lap_entry['lap']
                lap_data = lap_entry['data']
                
                lap_times[str(vehicle_num)] = lap_times.get(str(vehicle_num), {})
                lap_times[str(vehicle_num)][lap_num] = lap_data
        
        return lap_times
    except Exception as e:
        print(f"Error loading endurance data: {e}")
        return None

def extract_vehicle_number(vehicle_id):
    try:
        parts = vehicle_id.split('-')
        if len(parts) >= 3:
            return str(int(parts[-1]))
        if vehicle_id.isdigit():
            return vehicle_id
        return None
    except:
        return None

def get_lap_time(lap_times_dict, vehicle_id, lap_number):
    if not lap_times_dict:
        return None
    
    vehicle_num = extract_vehicle_number(vehicle_id)
    
    if vehicle_id in lap_times_dict:
        target_vehicle = vehicle_id
    elif vehicle_num and vehicle_num in lap_times_dict:
        target_vehicle = vehicle_num
    else:
        return None
    
    if lap_number not in lap_times_dict[target_vehicle]:
        return None
    
    lap_data = lap_times_dict[target_vehicle][lap_number]
    
    if isinstance(lap_data, dict):
        return lap_data.get('time')
    else:
        return lap_data

def get_lap_data(lap_times_dict, vehicle_id, lap_number):
    if not lap_times_dict:
        return None
    
    vehicle_num = extract_vehicle_number(vehicle_id)
    
    if vehicle_id in lap_times_dict:
        target_vehicle = vehicle_id
    elif vehicle_num and vehicle_num in lap_times_dict:
        target_vehicle = vehicle_num
    else:
        return None
    
    if lap_number not in lap_times_dict[target_vehicle]:
        return None
    
    lap_data = lap_times_dict[target_vehicle][lap_number]
    
    if isinstance(lap_data, dict):
        if 'lap_time' not in lap_data and 'time' in lap_data:
            lap_data['lap_time'] = lap_data['time']
        return lap_data
    else:
        return {'time': lap_data, 'lap_time': lap_data}

def get_sector_times(lap_times_dict, vehicle_id, lap_number):
    lap_data = get_lap_data(lap_times_dict, vehicle_id, lap_number)
    
    if not lap_data or not isinstance(lap_data, dict):
        return None
    
    s1 = lap_data.get('s1')
    s2 = lap_data.get('s2')
    s3 = lap_data.get('s3')
    
    if s1 is None and s2 is None and s3 is None:
        return None
    
    return {
        's1': s1,
        's2': s2,
        's3': s3
    }

def is_clean_lap(lap_times_dict, vehicle_id, lap_number):
    lap_data = get_lap_data(lap_times_dict, vehicle_id, lap_number)
    
    if not lap_data:
        return True
    
    if isinstance(lap_data, dict):
        flag = lap_data.get('flag', 'Unknown')
        if flag in ['FCY', 'SC', 'RED', 'FF']:
            return False
    
    return True

def find_lap_time_file(track_dir, race='R1'):
    track_path = Path(track_dir)
    
    race_num = race.replace('R', '')
    
    patterns = [
        f'*AnalysisEnduranceWithSections*Race*{race_num}*.CSV',
        f'*AnalysisEnduranceWithSections*Race_{race_num}*.CSV',
        f'*Endurance*Race*{race_num}*.CSV',
        f'{race}_*_lap_time.csv',
        f'*{race}*lap_time*.csv',
        'lap_time*.csv',
        '*laptime*.csv'
    ]
    
    for pattern in patterns:
        files = list(track_path.glob(pattern))
        if files:
            return files[0]
    
    return None

def get_flag_emoji(flag_code):
    flag_map = {
        'GF': '🟢',
        'FCY': '🟡',
        'FF': '🏁',
        'SC': '🟡',
        'RED': '🔴',
        'Unknown': '⚪'
    }
    return flag_map.get(flag_code, '⚪')