import pandas as pd
import numpy as np
from scipy.stats import variation
from steering_track_comparator import extract_corner_data

def analyze_multilap_consistency(lap_files, lap_numbers, track_name, track_config, vehicle_id=None, lap_times_dict=None):
    all_lap_data = []
    
    for lap_file, lap_num in zip(lap_files, lap_numbers):
        try:
            telemetry = pd.read_csv(lap_file)
            all_lap_data.append({
                'lap_num': lap_num,
                'telemetry': telemetry,
                'file': lap_file
            })
        except Exception as e:
            print(f"Error loading lap {lap_num}: {e}")
            continue
    
    if len(all_lap_data) < 2:
        return None
    
    results = {
        'num_laps': len(all_lap_data),
        'lap_numbers': lap_numbers,
        'lap_times': [],
        'corner_consistency': {},
        'overall_consistency': None,
        'outlier_laps': [],
        'trend_analysis': {}
    }
    
    from time_delta_calculator import calculate_lap_time
    if lap_times_dict:
        from lap_time_loader import get_lap_time
    
    for lap_data in all_lap_data:
        lap_time = None
        
        if lap_times_dict and vehicle_id:
            lap_time = get_lap_time(lap_times_dict, vehicle_id, lap_data['lap_num'])
        
        if lap_time is None:
            lap_time = calculate_lap_time(lap_data['telemetry'])
        
        results['lap_times'].append({
            'lap': lap_data['lap_num'],
            'time': lap_time if lap_time else None
        })
    
    valid_lap_times = [lt['time'] for lt in results['lap_times'] if lt['time'] is not None]
    if len(valid_lap_times) >= 2:
        mean_time = np.mean(valid_lap_times)
        std_time = np.std(valid_lap_times)
        cv = (std_time / mean_time) * 100 if mean_time > 0 else 0
        
        results['overall_consistency'] = {
            'mean_time': mean_time,
            'std_dev': std_time,
            'coefficient_of_variation': cv,
            'consistency_score': 100 / (1 + cv/50)
        }
        
        for lap_time_data in results['lap_times']:
            if lap_time_data['time']:
                deviation = abs(lap_time_data['time'] - mean_time)
                if deviation > (2 * std_time):
                    results['outlier_laps'].append({
                        'lap': lap_time_data['lap'],
                        'time': lap_time_data['time'],
                        'deviation': deviation,
                        'type': 'slower' if lap_time_data['time'] > mean_time else 'faster'
                    })
    
    if isinstance(track_config, dict) and 'corners' in track_config:
        corners = track_config['corners']
    else:
        corners = track_config
    
    for corner_def in corners:
        corner_name = corner_def['name']
        corner_metrics = []
        
        for lap_data in all_lap_data:
            corner_data = extract_corner_data(lap_data['telemetry'], corner_def['apex_dist_m'])
            if corner_data is not None:
                if 'steering_angle' in corner_data.columns:
                    steering_smoothness = np.abs(np.gradient(corner_data['steering_angle'].dropna())).mean()
                else:
                    steering_smoothness = None
                
                if 'pbrake_f' in corner_data.columns:
                    brake_max = corner_data['pbrake_f'].max()
                else:
                    brake_max = None
                
                corner_metrics.append({
                    'lap': lap_data['lap_num'],
                    'file': lap_data['file'],
                    'steering_smoothness': steering_smoothness,
                    'brake_max': brake_max
                })
        
        if len(corner_metrics) >= 2:
            steering_values = [m['steering_smoothness'] for m in corner_metrics if m['steering_smoothness'] is not None]
            brake_values = [m['brake_max'] for m in corner_metrics if m['brake_max'] is not None]
            
            corner_analysis = {
                'num_laps': len(corner_metrics),
                'steering_consistency': None,
                'brake_consistency': None,
                'overall_consistency_score': None,
                'best_lap': None,
                'worst_lap': None,
                'apex_dist_m': corner_def['apex_dist_m']
            }
            
            if len(steering_values) >= 2:
                steering_cv = variation(steering_values) * 100 if np.mean(steering_values) > 0 else 0
                corner_analysis['steering_consistency'] = {
                    'coefficient_of_variation': steering_cv,
                    'consistency_score': 100 / (1 + steering_cv/50)
                }
                
                metrics_with_steering = [(m, m['steering_smoothness']) for m in corner_metrics if m['steering_smoothness'] is not None]
                metrics_with_steering.sort(key=lambda x: x[1])
                
                corner_analysis['best_lap'] = {
                    'lap': metrics_with_steering[0][0]['lap'],
                    'file': metrics_with_steering[0][0]['file']
                }
                corner_analysis['worst_lap'] = {
                    'lap': metrics_with_steering[-1][0]['lap'],
                    'file': metrics_with_steering[-1][0]['file']
                }
            
            if len(brake_values) >= 2:
                brake_cv = variation(brake_values) * 100 if np.mean(brake_values) > 0 else 0
                corner_analysis['brake_consistency'] = {
                    'coefficient_of_variation': brake_cv,
                    'consistency_score': 100 / (1 + brake_cv/50)
                }
            
            consistency_scores = []
            if corner_analysis['steering_consistency']:
                consistency_scores.append(corner_analysis['steering_consistency']['consistency_score'])
            if corner_analysis['brake_consistency']:
                consistency_scores.append(corner_analysis['brake_consistency']['consistency_score'])
            
            if consistency_scores:
                corner_analysis['overall_consistency_score'] = np.mean(consistency_scores)
            
            results['corner_consistency'][corner_name] = corner_analysis
    
    if len(valid_lap_times) >= 3:
        first_third = valid_lap_times[:len(valid_lap_times)//3]
        last_third = valid_lap_times[-len(valid_lap_times)//3:]
        
        if len(first_third) > 0 and len(last_third) > 0:
            avg_early = np.mean(first_third)
            avg_late = np.mean(last_third)
            
            if avg_late < avg_early:
                trend = 'improving'
                improvement = ((avg_early - avg_late) / avg_early) * 100
            elif avg_late > avg_early:
                trend = 'deteriorating'
                improvement = ((avg_late - avg_early) / avg_early) * 100
            else:
                trend = 'stable'
                improvement = 0
            
            results['trend_analysis'] = {
                'trend': trend,
                'percentage_change': improvement,
                'early_avg': avg_early,
                'late_avg': avg_late
            }
    
    return results

def generate_consistency_report(consistency_results, vehicle_id):
    if not consistency_results:
        return "Insufficient data for consistency analysis"
    
    lines = []
    lines.append("MULTI-LAP CONSISTENCY ANALYSIS")
    lines.append("=" * 80)
    lines.append(f"Vehicle: {vehicle_id}")
    lines.append(f"Laps Analyzed: {consistency_results['num_laps']} (Laps {min(consistency_results['lap_numbers'])} - {max(consistency_results['lap_numbers'])})")
    lines.append("")
    
    if consistency_results['overall_consistency']:
        oc = consistency_results['overall_consistency']
        lines.append("OVERALL LAP TIME CONSISTENCY")
        lines.append("-" * 80)
        lines.append(f"  Average Lap Time: {oc['mean_time']:.3f}s")
        lines.append(f"  Standard Deviation: {oc['std_dev']:.3f}s")
        lines.append(f"  Consistency Score: {oc['consistency_score']:.1f}/100")
        lines.append("")
        
        if oc['consistency_score'] >= 85:
            lines.append("  Assessment: EXCELLENT - Very consistent lap times")
        elif oc['consistency_score'] >= 70:
            lines.append("  Assessment: GOOD - Reasonably consistent performance")
        elif oc['consistency_score'] >= 50:
            lines.append("  Assessment: MODERATE - Some lap-to-lap variation")
        else:
            lines.append("  Assessment: INCONSISTENT - High lap-to-lap variation")
        lines.append("")
    
    if consistency_results['outlier_laps']:
        lines.append("OUTLIER LAPS")
        lines.append("-" * 80)
        for outlier in consistency_results['outlier_laps']:
            lines.append(f"  Lap {outlier['lap']}: {outlier['time']:.3f}s ({outlier['type']}, {outlier['deviation']:.3f}s deviation)")
        lines.append("")
    
    if consistency_results['trend_analysis']:
        ta = consistency_results['trend_analysis']
        lines.append("PERFORMANCE TREND")
        lines.append("-" * 80)
        lines.append(f"  Trend: {ta['trend'].upper()}")
        lines.append(f"  Early Stint Average: {ta['early_avg']:.3f}s")
        lines.append(f"  Late Stint Average: {ta['late_avg']:.3f}s")
        lines.append(f"  Change: {ta['percentage_change']:+.2f}%")
        lines.append("")
    
    if consistency_results['corner_consistency']:
        lines.append("CORNER-BY-CORNER CONSISTENCY")
        lines.append("-" * 80)
        
        corner_scores = []
        for corner_name, analysis in consistency_results['corner_consistency'].items():
            if analysis['overall_consistency_score']:
                corner_scores.append((corner_name, analysis['overall_consistency_score']))
        
        corner_scores.sort(key=lambda x: x[1])
        
        if len(corner_scores) > 0:
            lines.append(f"  Most Inconsistent Corners (need attention):")
            for corner_name, score in corner_scores[:5]:
                lines.append(f"    {corner_name}: {score:.1f}/100")
            lines.append("")
            
            lines.append(f"  Most Consistent Corners:")
            for corner_name, score in corner_scores[-5:]:
                lines.append(f"    {corner_name}: {score:.1f}/100")
            lines.append("")
    
    return '\n'.join(lines)