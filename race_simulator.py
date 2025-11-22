import time
import shutil
from pathlib import Path
import threading

class RaceSessionSimulator:
    def __init__(self, lap_files, incoming_dir, interval=30):
        self.lap_files = lap_files
        self.incoming_dir = Path(incoming_dir)
        self.interval = interval
        self.running = False
        self.thread = None
        self.current_lap = 0
    
    def start(self):
        if not self.incoming_dir.exists():
            self.incoming_dir.mkdir(parents=True, exist_ok=True)
        
        existing_files = list(self.incoming_dir.glob('*.csv'))
        for f in existing_files:
            f.unlink()
        
        self.running = True
        self.current_lap = 0
        self.thread = threading.Thread(target=self._simulate_session, daemon=True)
        self.thread.start()
        
        print(f"Race simulation started: {len(self.lap_files)} laps at {self.interval}s intervals")
    
    def _simulate_session(self):
        for i, lap_file in enumerate(self.lap_files, 1):
            if not self.running:
                break
            
            self.current_lap = i
            
            print(f"\n[Simulator] Lap {i}/{len(self.lap_files)} arriving...")
            
            dest_file = self.incoming_dir / f'lap_{i:03d}.csv'
            shutil.copy(lap_file, dest_file)
            
            print(f"[Simulator] Copied {Path(lap_file).name} -> {dest_file.name}")
            
            if i < len(self.lap_files):
                time.sleep(self.interval)
        
        self.running = False
        print("\n[Simulator] Race session complete!")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[Simulator] Stopped")
    
    def is_running(self):
        return self.running
    
    def get_progress(self):
        return {
            'current_lap': self.current_lap,
            'total_laps': len(self.lap_files),
            'is_running': self.running
        }

def setup_demo_session(track_name, vehicle_id, race, lap_range, processed_data_dir='processed_data'):
    processed_dir = Path(processed_data_dir) / track_name
    
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")
    
    import json
    metadata_file = processed_dir / 'metadata.json'
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    if race not in metadata:
        raise ValueError(f"Race {race} not found in metadata")
    
    if vehicle_id not in metadata[race]:
        raise ValueError(f"Vehicle {vehicle_id} not found in {race}")
    
    laps = metadata[race][vehicle_id]
    
    start_lap, end_lap = lap_range
    selected_laps = [l for l in laps if start_lap <= l['lap'] <= end_lap]
    
    if not selected_laps:
        raise ValueError(f"No laps found in range {start_lap}-{end_lap}")
    
    selected_laps.sort(key=lambda x: x['lap'])
    
    lap_files = [str(processed_dir / lap['file']) for lap in selected_laps]
    
    for f in lap_files:
        if not Path(f).exists():
            raise FileNotFoundError(f"Lap file not found: {f}")
    
    print(f"Demo session configured:")
    print(f"  Track: {track_name}")
    print(f"  Vehicle: {vehicle_id}")
    print(f"  Race: {race}")
    print(f"  Laps: {len(lap_files)} (Lap {start_lap} to Lap {end_lap})")
    
    return lap_files