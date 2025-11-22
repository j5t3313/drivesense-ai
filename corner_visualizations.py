import matplotlib.pyplot as plt
import numpy as np

def plot_corner_detail(corner_detail, lap_info_a, lap_info_b, output_path):
    corner_data_a = corner_detail['data_a']
    corner_data_b = corner_detail['data_b']
    
    if len(corner_data_a) < 2 or len(corner_data_b) < 2:
        return
    
    distance_col = 'lapdist_dls'
    
    corner_data_a = corner_data_a.dropna(subset=[distance_col])
    corner_data_b = corner_data_b.dropna(subset=[distance_col])
    
    if len(corner_data_a) < 2 or len(corner_data_b) < 2:
        return
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    label_a = f"Vehicle {lap_info_a['vehicle_id']}"
    label_b = f"Vehicle {lap_info_b['vehicle_id']}"
    
    if 'steering_angle' in corner_data_a.columns and 'steering_angle' in corner_data_b.columns:
        steering_a = corner_data_a.dropna(subset=['steering_angle'])
        steering_b = corner_data_b.dropna(subset=['steering_angle'])
        
        if len(steering_a) > 0:
            ax1.plot(steering_a[distance_col], np.abs(steering_a['steering_angle']), 
                    label=label_a, linewidth=2, color='#2E86DE', alpha=0.8)
        if len(steering_b) > 0:
            ax1.plot(steering_b[distance_col], np.abs(steering_b['steering_angle']), 
                    label=label_b, linewidth=2, color='#EE5A6F', alpha=0.8)
        
        ax1.set_ylabel('Steering Angle (°)', fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
    
    if 'pbrake_f' in corner_data_a.columns and 'pbrake_f' in corner_data_b.columns:
        brake_a = corner_data_a.dropna(subset=['pbrake_f'])
        brake_b = corner_data_b.dropna(subset=['pbrake_f'])
        
        if len(brake_a) > 0:
            ax2.plot(brake_a[distance_col], brake_a['pbrake_f'], 
                    label=label_a, linewidth=2, color='#2E86DE', alpha=0.8)
        if len(brake_b) > 0:
            ax2.plot(brake_b[distance_col], brake_b['pbrake_f'], 
                    label=label_b, linewidth=2, color='#EE5A6F', alpha=0.8)
        
        ax2.set_ylabel('Brake Pressure (bar)', fontweight='bold')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
    
    if 'ath' in corner_data_a.columns and 'ath' in corner_data_b.columns:
        throttle_a = corner_data_a.dropna(subset=['ath'])
        throttle_b = corner_data_b.dropna(subset=['ath'])
        
        if len(throttle_a) > 0:
            ax3.plot(throttle_a[distance_col], throttle_a['ath'], 
                    label=label_a, linewidth=2, color='#2E86DE', alpha=0.8)
        if len(throttle_b) > 0:
            ax3.plot(throttle_b[distance_col], throttle_b['ath'], 
                    label=label_b, linewidth=2, color='#EE5A6F', alpha=0.8)
        
        ax3.set_ylabel('Throttle Position (%)', fontweight='bold')
        ax3.set_xlabel('Distance (m)', fontweight='bold')
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
    
    title = f"{corner_detail['corner_name']} Detail Analysis"
    if corner_detail['time_delta'] is not None:
        title += f"\nTime Delta: {corner_detail['time_delta']:+.3f}s"
    
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def generate_corner_visualizations(detailed_report, lap_info_a, lap_info_b, output_dir='visualizations/corners'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    track_name = detailed_report['track']
    
    for corner in detailed_report['corners']:
        if len(corner['data_a']) < 2 or len(corner['data_b']) < 2:
            continue
        
        corner_name_clean = corner['corner_name'].replace('/', '-').replace(' ', '_')
        output_path = f"{output_dir}/{track_name}_{corner_name_clean}_detail.png"
        
        plot_corner_detail(corner, lap_info_a, lap_info_b, output_path)
        print(f"Saved: {output_path}")
    
    print(f"\nAll corner visualizations saved to {output_dir}/")