import pandas as pd
from pathlib import Path

def load_endurance_data(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
        
        required_cols = ['NUMBER', 'LAP_NUMBER', 'LAP_TIME', 'KPH', 'TOP_SPEED']
        if not all(col in df.columns for col in required_cols):
            return None
        
        endurance_dict = {}
        
        for _, row in df.iterrows():
            vehicle_num = int(row['NUMBER'])
            lap_num = int(row['LAP_NUMBER'])
            
            if vehicle_num not in endurance_dict:
                endurance_dict[vehicle_num] = {}
            
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
            
            endurance_dict[vehicle_num][lap_num] = {
                'lap_time': lap_time_seconds,
                'lap_time_str': lap_time_str,
                'kph': float(row['KPH']) if pd.notna(row['KPH']) else None,
                'top_speed': float(row['TOP_SPEED']) if pd.notna(row['TOP_SPEED']) else None,
                's1': float(row['S1_SECONDS']) if 'S1_SECONDS' in row and pd.notna(row['S1_SECONDS']) else None,
                's2': float(row['S2_SECONDS']) if 'S2_SECONDS' in row and pd.notna(row['S2_SECONDS']) else None,
                's3': float(row['S3_SECONDS']) if 'S3_SECONDS' in row and pd.notna(row['S3_SECONDS']) else None,
                'flag': str(row['FLAG_AT_FL']) if 'FLAG_AT_FL' in row and pd.notna(row['FLAG_AT_FL']) else 'Unknown'
            }
        
        return endurance_dict
    except Exception as e:
        print(f"Error loading endurance data: {e}")
        return None

def match_vehicle_to_endurance(vehicle_id):
    try:
        parts = vehicle_id.split('-')
        if len(parts) >= 3:
            last_part = parts[-1]
            return int(last_part)
        return None
    except:
        return None

def get_lap_context(vehicle_id, lap_num, endurance_data):
    if not endurance_data:
        return None
    
    vehicle_num = match_vehicle_to_endurance(vehicle_id)
    if vehicle_num is None:
        return None
    
    if vehicle_num not in endurance_data:
        return None
    
    if lap_num not in endurance_data[vehicle_num]:
        return None
    
    return endurance_data[vehicle_num][lap_num]

def find_endurance_file(track_dir, race='R1'):
    track_path = Path(track_dir)
    
    race_num = race.replace('R', '')
    
    patterns = [
        f'*AnalysisEnduranceWithSections*Race*{race_num}*.CSV',
        f'*AnalysisEnduranceWithSections*Race_{race_num}*.CSV',
        f'*Endurance*Race*{race_num}*.CSV',
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
        'RED': '🔴'
    }
    return flag_map.get(flag_code, '⚪')