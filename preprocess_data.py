import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_DIR = Path(r"C:\Users\jessm\OneDrive\Desktop\Hack the Track")
OUTPUT_DIR = Path("processed_data")
OUTPUT_DIR.mkdir(exist_ok=True)

TRACKS = {
    'barber': {
        'R1_telemetry': 'barber/R1_barber_telemetry_data.csv',
        'R1_laptimes': 'barber/R1_barber_lap_time.csv',
        'R2_telemetry': 'barber/R2_barber_telemetry_data.csv',
        'R2_laptimes': 'barber/R2_barber_lap_time.csv',
    },
    'cota': {
        'R1_telemetry': 'cota/Race 1/R1_cota_telemetry_data.csv',
        'R1_laptimes': 'cota/Race 1/cota_lap_time_R1.csv',
        'R2_telemetry': 'cota/Race 2/R2_cota_telemetry_data.csv',
        'R2_laptimes': 'cota/Race 2/cota_lap_time_R2.csv',
    },
    'indianapolis': {
        'R1_telemetry': 'indianapolis/R1_indianapolis_motor_speedway_telemetry.csv',
        'R1_laptimes': 'indianapolis/R1_indianapolis_motor_speedway_lap_time.csv',
        'R2_telemetry': 'indianapolis/R2_indianapolis_motor_speedway_telemetry.csv',
        'R2_laptimes': 'indianapolis/R2_indianapolis_motor_speedway_lap_time.csv',
    },
    'road-america': {
        'R1_telemetry': 'road-america/Road America/Race 1/R1_road_america_telemetry_data.csv',
        'R1_laptimes': 'road-america/Road America/Race 1/road_america_lap_time_R2.csv',
        'R2_telemetry': 'road-america/Road America/Race 2/R2_road_america_telemetry_data.csv',
        'R2_laptimes': 'road-america/Road America/Race 2/road_america_lap_time_R2.csv',
    },
    'sebring': {
        'R1_telemetry': 'sebring/Race 1/sebring_telemetry_R1.csv',
        'R1_laptimes': 'sebring/Race 1/sebring_lap_time_R1.csv',
        'R2_telemetry': 'sebring/Race 2/sebring_telemetry_data_R2.csv',
        'R2_laptimes': 'sebring/Race 2/sebring_lap_time_R2.csv',
    },
    'sonoma': {
        'R1_telemetry': 'sonoma/Race 1/sonoma_telemetry_R1.csv',
        'R1_laptimes': 'sonoma/Race 1/sonoma_lap_time_R1.csv',
        'R2_telemetry': 'sonoma/Race 2/sonoma_telemetry_R2.csv',
        'R2_laptimes': 'sonoma/Race 2/sonoma_lap_time_R2.csv',
    },
    'vir': {
        'R1_telemetry': 'virginia-international-raceway/vir/Race 1/R1_vir_telemetry_data.csv',
        'R1_laptimes': 'virginia-international-raceway/vir/Race 1/vir_lap_time_R1.csv',
        'R2_telemetry': 'virginia-international-raceway/vir/Race 2/R2_vir_telemetry_data.csv',
        'R2_laptimes': 'virginia-international-raceway/vir/Race 2/vir_lap_time_R2.csv',
    },
}

def preprocess_track(track_name, track_files):
    print(f"\n{'='*60}")
    print(f"Processing {track_name.upper()}")
    print(f"{'='*60}")
    
    track_output = OUTPUT_DIR / track_name
    track_output.mkdir(exist_ok=True)
    
    valid_laps_metadata = {'R1': {}, 'R2': {}}
    
    for race in ['R1', 'R2']:
        tel_file = DATA_DIR / track_files[f'{race}_telemetry']
        lap_file = DATA_DIR / track_files[f'{race}_laptimes']
        
        if not tel_file.exists():
            print(f"  Skipping {race} - telemetry file not found")
            continue
            
        print(f"\n  Processing {race}...")
        print(f"    Loading telemetry from {tel_file.name}...")
        
        tel_df = pd.read_csv(tel_file)
        
        print(f"    Converting to wide format...")
        tel_wide = tel_df.pivot_table(
            index=['timestamp', 'lap', 'vehicle_id'],
            columns='telemetry_name',
            values='telemetry_value',
            aggfunc='first'
        ).reset_index()
        tel_wide.columns.name = None
        
        column_mapping = {
            'Laptrigger_lapdist_dls': 'lapdist_dls',
            'trigger_lapdist_dls': 'lapdist_dls',
            'aps': 'ath',
            'Steering_Angle': 'steering_angle',
            'VBOX_Lat_Min': 'latitude',
            'VBOX_Long_Minutes': 'longitude',
        }
        tel_wide = tel_wide.rename(columns=column_mapping)
        
        distance_cols = ['lapdist_dls', 'Lap', 'distance']
        distance_col = None
        for col in distance_cols:
            if col in tel_wide.columns:
                distance_col = col
                print(f"    Found distance column: {col}")
                break
        
        if not distance_col:
            print(f"    WARNING: No distance data for {race} - processing for aggregate analysis only")
        
        print(f"    Filtering valid laps...")
        
        for vehicle_id in tel_wide['vehicle_id'].unique():
            vehicle_data = tel_wide[tel_wide['vehicle_id'] == vehicle_id]
            
            for lap_num in vehicle_data['lap'].unique():
                lap_data = vehicle_data[vehicle_data['lap'] == lap_num]
                
                if len(lap_data) < 10:
                    continue
                
                if distance_col:
                    distances = lap_data[distance_col].dropna()
                    if len(distances) < 5:
                        continue
                    
                    dist_range = distances.max() - distances.min()
                    
                    if dist_range < 500:
                        continue
                else:
                    dist_range = 0.0
                
                output_file = track_output / f"{race}_vehicle{vehicle_id}_lap{lap_num}.csv"
                lap_data.to_csv(output_file, index=False)
                
                if vehicle_id not in valid_laps_metadata[race]:
                    valid_laps_metadata[race][vehicle_id] = []
                
                valid_laps_metadata[race][vehicle_id].append({
                    'lap': int(lap_num),
                    'distance_range': float(dist_range),
                    'data_points': len(lap_data),
                    'file': output_file.name,
                    'has_distance': distance_col is not None
                })
        
        for vehicle_id, laps in valid_laps_metadata[race].items():
            print(f"      Vehicle {vehicle_id}: {len(laps)} valid laps")
    
    metadata_file = track_output / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(valid_laps_metadata, f, indent=2)
    
    print(f"\n  Saved metadata to {metadata_file}")
    return valid_laps_metadata

if __name__ == "__main__":
    print("DriveSense AI - Data Preprocessing")
    print("="*60)
    
    all_metadata = {}
    
    for track_name, track_files in TRACKS.items():
        metadata = preprocess_track(track_name, track_files)
        all_metadata[track_name] = metadata
    
    summary_file = OUTPUT_DIR / 'all_tracks_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"COMPLETE - Saved summary to {summary_file}")
    print(f"{'='*60}")