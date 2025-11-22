import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from scipy.stats import variation

from gradient_analysis import classify_driver_behavior_by_gradient
from steering_track_comparator import extract_corner_data
from time_delta_calculator import calculate_lap_time
from track_configs import TRACK_CONFIGS
from lap_time_loader import load_lap_times_from_file, get_lap_time, get_lap_data, find_lap_time_file

class LiveRaceAnalyzer:
    def __init__(self, track_name, vehicle_id, race='R1', processed_data_dir='processed_data'):
        self.track_name = track_name
        self.vehicle_id = vehicle_id
        self.race = race
        
        track_config = TRACK_CONFIGS.get(track_name)
        if isinstance(track_config, dict) and 'corners' in track_config:
            self.corners = track_config['corners']
        else:
            self.corners = track_config
        
        self.lap_times_dict = None
        self.has_endurance_data = False
        track_dir = Path(processed_data_dir) / track_name
        if track_dir.exists():
            lap_time_file = find_lap_time_file(track_dir, race)
            if lap_time_file:
                print(f"Loading lap times from: {lap_time_file.name}")
                self.lap_times_dict = load_lap_times_from_file(lap_time_file)
                if self.lap_times_dict:
                    print(f"  Loaded lap times for {len(self.lap_times_dict)} vehicles")
                    self.has_endurance_data = True
        
        self.session_state = {
            'track_name': track_name,
            'vehicle_id': vehicle_id,
            'race': race,
            'reference_lap': None,
            'reference_lap_time': None,
            'reference_lap_data': None,
            'best_lap_telemetry': None,
            'laps_processed': 0,
            'lap_times': [],
            'corner_history': {},
            'consistency_scores': {},
            'alerts': [],
            'session_start_time': datetime.now(),
            'last_lap_time': None,
            'status': 'running'
        }
        
        for corner in self.corners:
            self.session_state['corner_history'][corner['name']] = {
                'baseline': None,
                'laps': []
            }
    
    def process_new_lap(self, lap_file, lap_number):
        try:
            telemetry = pd.read_csv(lap_file)
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load lap file: {e}",
                'lap': lap_number
            }
        
        lap_time = get_lap_time(self.lap_times_dict, self.vehicle_id, lap_number)
        lap_data = get_lap_data(self.lap_times_dict, self.vehicle_id, lap_number) if self.lap_times_dict else None
        
        if lap_data and lap_data.get('flag') == 'FCY':
            print(f"Lap {lap_number}: Skipping (Yellow Flag)")
            return {
                'success': True,
                'lap': lap_number,
                'type': 'skipped',
                'message': f'Lap {lap_number} skipped (Yellow Flag - FCY)',
                'lap_data': lap_data
            }
        
        self.session_state['laps_processed'] += 1
        self.session_state['last_lap_time'] = datetime.now()
        
        if lap_time:
            print(f"Lap {lap_number} time: {lap_time:.3f}s (from lap time file)")
            self.session_state['lap_times'].append({
                'lap': lap_number,
                'time': lap_time
            })
        else:
            lap_time_calculated = calculate_lap_time(telemetry)
            if lap_time_calculated:
                print(f"Lap {lap_number} time: {lap_time_calculated:.3f}s (calculated from telemetry)")
                lap_time = lap_time_calculated
                self.session_state['lap_times'].append({
                    'lap': lap_number,
                    'time': lap_time
                })
            else:
                print(f"Lap {lap_number}: Could not find lap time")
                lap_time = None
        
        if self.session_state['reference_lap'] is None:
            return self._process_baseline_lap(telemetry, lap_number, lap_time, lap_data)
        else:
            return self._process_comparison_lap(telemetry, lap_number, lap_time, lap_data)
    
    def _process_baseline_lap(self, telemetry, lap_number, lap_time, lap_data=None):
        self.session_state['reference_lap'] = lap_number
        self.session_state['reference_lap_time'] = lap_time
        self.session_state['reference_lap_data'] = lap_data
        self.session_state['best_lap_telemetry'] = telemetry
        
        for corner in self.corners:
            corner_data = extract_corner_data(telemetry, corner['apex_dist_m'])
            if corner_data is not None:
                self.session_state['corner_history'][corner['name']]['baseline'] = corner_data
                self.session_state['corner_history'][corner['name']]['laps'].append({
                    'lap': lap_number,
                    'data': corner_data,
                    'classification': 'baseline'
                })
        
        message = f'Baseline lap established (Lap {lap_number})'
        if lap_time is None:
            message += ' - waiting for lap time data'
        else:
            message += f' - {lap_time:.3f}s'
        
        return {
            'success': True,
            'lap': lap_number,
            'type': 'baseline',
            'lap_time': lap_time,
            'lap_data': lap_data,
            'message': message,
            'corners_recorded': len([c for c in self.corners if self.session_state['corner_history'][c['name']]['baseline'] is not None])
        }
    
    def _process_comparison_lap(self, telemetry, lap_number, lap_time, lap_data=None):
        results = {
            'success': True,
            'lap': lap_number,
            'type': 'comparison',
            'lap_time': lap_time,
            'lap_data': lap_data,
            'delta_to_reference': None,
            'top_speed_delta': None,
            'corners': {},
            'alerts': [],
            'new_reference': False
        }
        
        if lap_time and self.session_state['reference_lap_time'] is not None:
            results['delta_to_reference'] = lap_time - self.session_state['reference_lap_time']
        
        if lap_data and lap_data.get('top_speed') and self.session_state.get('reference_lap_data'):
            ref_data = self.session_state['reference_lap_data']
            if ref_data.get('top_speed'):
                results['top_speed_delta'] = lap_data['top_speed'] - ref_data['top_speed']
        
        for corner in self.corners:
            corner_name = corner['name']
            corner_data_new = extract_corner_data(telemetry, corner['apex_dist_m'])
            corner_data_ref = self.session_state['corner_history'][corner_name]['baseline']
            
            if corner_data_new is None or corner_data_ref is None:
                continue
            
            classification = classify_driver_behavior_by_gradient(
                corner_data_ref,
                corner_data_new,
                f"Reference (Lap {self.session_state['reference_lap']})",
                f"Current (Lap {lap_number})"
            )
            
            results['corners'][corner_name] = {
                'classification': classification['type'],
                'confidence': classification['confidence'],
                'description': classification['description'],
                'evidence': classification.get('evidence', [])
            }
            
            if classification['type'] == 'driver_mistake' and classification['confidence'] > 0.75:
                alert = {
                    'lap': lap_number,
                    'corner': corner_name,
                    'type': 'mistake',
                    'confidence': classification['confidence'],
                    'message': f"Lap {lap_number}: Mistake detected at {corner_name}"
                }
                results['alerts'].append(alert)
                self.session_state['alerts'].append(alert)
            
            self.session_state['corner_history'][corner_name]['laps'].append({
                'lap': lap_number,
                'data': corner_data_new,
                'classification': classification['type'],
                'confidence': classification['confidence']
            })
        
        if lap_time:
            if self.session_state['reference_lap_time'] is None:
                self.session_state['reference_lap_time'] = lap_time
                self.session_state['reference_lap'] = lap_number
                results['message'] = f"Reference lap time established: {lap_time:.3f}s"
            elif lap_time < self.session_state['reference_lap_time']:
                self.session_state['reference_lap'] = lap_number
                self.session_state['reference_lap_time'] = lap_time
                self.session_state['reference_lap_data'] = lap_data
                self.session_state['best_lap_telemetry'] = telemetry
                
                for corner in self.corners:
                    corner_name = corner['name']
                    corner_data = extract_corner_data(telemetry, corner['apex_dist_m'])
                    if corner_data is not None:
                        self.session_state['corner_history'][corner_name]['baseline'] = corner_data
                
                results['new_reference'] = True
                results['message'] = f"New best lap! {lap_time:.3f}s"
        
        if self.session_state['laps_processed'] >= 3:
            self._update_consistency_scores()
        
        return results
    
    def _update_consistency_scores(self):
        for corner_name, history in self.session_state['corner_history'].items():
            laps_data = history['laps']
            
            if len(laps_data) < 3:
                continue
            
            smoothness_values = []
            for lap_entry in laps_data:
                if lap_entry['data'] is not None and 'steering_angle' in lap_entry['data'].columns:
                    smoothness = np.abs(np.gradient(
                        lap_entry['data']['steering_angle'].dropna()
                    )).mean()
                    if not np.isnan(smoothness):
                        smoothness_values.append(smoothness)
            
            if len(smoothness_values) >= 3:
                cv = variation(smoothness_values) * 100
                consistency_score = 100 / (1 + cv/50)
                
                trend = 'stable'
                if len(smoothness_values) >= 5:
                    early = np.mean(smoothness_values[:len(smoothness_values)//2])
                    late = np.mean(smoothness_values[len(smoothness_values)//2:])
                    if late > early * 1.2:
                        trend = 'declining'
                    elif late < early * 0.8:
                        trend = 'improving'
                
                self.session_state['consistency_scores'][corner_name] = {
                    'score': consistency_score,
                    'laps_analyzed': len(smoothness_values),
                    'trend': trend
                }
                
                if consistency_score < 65 and trend == 'declining':
                    recent_laps = [l['lap'] for l in laps_data[-3:] if l.get('classification') == 'driver_mistake']
                    if len(recent_laps) >= 2:
                        alert = {
                            'lap': laps_data[-1]['lap'],
                            'corner': corner_name,
                            'type': 'consistency_alert',
                            'message': f"{corner_name}: Consistency declining (now {consistency_score:.0f}/100)",
                            'severity': 'high'
                        }
                        if alert not in self.session_state['alerts']:
                            self.session_state['alerts'].append(alert)
    
    def get_session_summary(self):
        summary = {
            'laps_processed': self.session_state['laps_processed'],
            'reference_lap': self.session_state['reference_lap'],
            'reference_lap_time': self.session_state['reference_lap_time'],
            'total_alerts': len(self.session_state['alerts']),
            'consistency_scores': self.session_state['consistency_scores'],
            'lap_times': self.session_state['lap_times'],
            'problem_corners': [],
            'good_corners': []
        }
        
        valid_lap_times = [lt['time'] for lt in self.session_state['lap_times'] if lt['time'] is not None]
        if len(valid_lap_times) >= 2:
            lap_times_array = np.array(valid_lap_times)
            mean_time = lap_times_array.mean()
            std_time = lap_times_array.std()
            cv = (std_time / mean_time) * 100 if mean_time > 0 else 0
            
            summary['laptime_analysis'] = {
                'fastest': lap_times_array.min(),
                'slowest': lap_times_array.max(),
                'mean': mean_time,
                'std': std_time,
                'range': lap_times_array.max() - lap_times_array.min(),
                'consistency_score': 100 / (1 + cv/50)
            }
            
            if len(valid_lap_times) >= 3:
                first_third = valid_lap_times[:len(valid_lap_times)//3]
                last_third = valid_lap_times[-len(valid_lap_times)//3:]
                
                if len(first_third) > 0 and len(last_third) > 0:
                    avg_early = np.mean(first_third)
                    avg_late = np.mean(last_third)
                    
                    if avg_late < avg_early * 0.995:
                        summary['laptime_analysis']['trend'] = 'improving'
                    elif avg_late > avg_early * 1.005:
                        summary['laptime_analysis']['trend'] = 'deteriorating'
                    else:
                        summary['laptime_analysis']['trend'] = 'stable'
        
        if self.session_state['best_lap_telemetry'] is not None:
            telemetry = self.session_state['best_lap_telemetry']
            
            if 'steering_angle' in telemetry.columns:
                steering = telemetry['steering_angle'].dropna()
                if len(steering) > 0:
                    abs_steering = np.abs(steering)
                    steering_grad = np.abs(np.gradient(steering))
                    smoothness = max(0, 100 - (steering_grad.mean() * 50))
                    
                    summary['steering_metrics'] = {
                        'mean_abs_steering': abs_steering.mean(),
                        'max_abs_steering': abs_steering.max(),
                        'std_steering': steering.std(),
                        'smoothness': smoothness
                    }
            
            if 'pbrake_f' in telemetry.columns:
                brake = telemetry['pbrake_f'].dropna()
                brake_events = brake[brake > 10]
                if len(brake_events) > 0:
                    brake_grad = np.abs(np.gradient(brake_events))
                    consistency = max(0, 100 - (brake_grad.std() * 2))
                    
                    summary['brake_metrics'] = {
                        'mean_brake': brake_events.mean(),
                        'max_brake': brake_events.max(),
                        'brake_applications': len(brake_events),
                        'consistency': consistency
                    }
            
            if 'ath' in telemetry.columns:
                throttle = telemetry['ath'].dropna()
                if len(throttle) > 0:
                    full_throttle_pct = (throttle > 80).mean() * 100
                    confidence = min(100, full_throttle_pct * 1.2)
                    
                    summary['throttle_metrics'] = {
                        'mean_throttle': throttle.mean(),
                        'full_throttle_pct': full_throttle_pct,
                        'std_throttle': throttle.std(),
                        'confidence': confidence
                    }
        
        for corner_name, data in self.session_state['consistency_scores'].items():
            if data['score'] < 70:
                summary['problem_corners'].append({
                    'corner': corner_name,
                    'score': data['score'],
                    'trend': data['trend']
                })
            elif data['score'] >= 85:
                summary['good_corners'].append({
                    'corner': corner_name,
                    'score': data['score']
                })
        
        summary['problem_corners'].sort(key=lambda x: x['score'])
        summary['good_corners'].sort(key=lambda x: x['score'], reverse=True)
        
        return summary
    
    def get_state(self):
        return self.session_state
    
    def save_session(self, output_path):
        session_copy = self.session_state.copy()
        session_copy['best_lap_telemetry'] = None
        
        for corner_name in session_copy['corner_history']:
            session_copy['corner_history'][corner_name]['baseline'] = None
            for lap_entry in session_copy['corner_history'][corner_name]['laps']:
                lap_entry['data'] = None
        
        session_copy['session_start_time'] = session_copy['session_start_time'].isoformat()
        if session_copy['last_lap_time']:
            session_copy['last_lap_time'] = session_copy['last_lap_time'].isoformat()
        
        with open(output_path, 'w') as f:
            json.dump(session_copy, f, indent=2)
    
    def end_session(self):
        self.session_state['status'] = 'complete'
        return self.get_session_summary()