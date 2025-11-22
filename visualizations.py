import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

def plot_speed_traces(telemetry_a, telemetry_b, corners, track_name, lap_info_a, lap_info_b, output_path=None):
    fig, ax = plt.subplots(figsize=(16, 6))
    
    distance_col = 'lapdist_dls'
    if distance_col not in telemetry_a.columns or distance_col not in telemetry_b.columns:
        print("Error: Distance data not available")
        return
    
    telemetry_a_clean = telemetry_a.dropna(subset=[distance_col, 'speed'])
    telemetry_b_clean = telemetry_b.dropna(subset=[distance_col, 'speed'])
    
    label_a = f"Vehicle {lap_info_a['vehicle_id']}, Lap {lap_info_a['lap']} ({lap_info_a['time']:.2f}s)"
    label_b = f"Vehicle {lap_info_b['vehicle_id']}, Lap {lap_info_b['lap']} ({lap_info_b['time']:.2f}s)"
    
    ax.plot(telemetry_a_clean[distance_col], telemetry_a_clean['speed'], 
            label=label_a, linewidth=2, alpha=0.8, color='#2E86DE')
    ax.plot(telemetry_b_clean[distance_col], telemetry_b_clean['speed'], 
            label=label_b, linewidth=2, alpha=0.8, color='#EE5A6F')
    
    for corner in corners:
        ax.axvline(x=corner['apex_dist_m'], color='gray', linestyle='--', 
                   alpha=0.3, linewidth=1)
        ax.text(corner['apex_dist_m'], ax.get_ylim()[1] * 0.95, 
                corner['name'].split('(')[0].strip(), 
                rotation=90, verticalalignment='top', fontsize=8, alpha=0.6)
    
    time_delta = lap_info_a['time'] - lap_info_b['time']
    subtitle = f"Time Delta: {time_delta:+.3f}s"
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speed (km/h)', fontsize=12, fontweight='bold')
    ax.set_title(f'Speed Trace Comparison - {track_name.upper()}\n{subtitle}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()

def plot_steering_comparison(comparison_results, track_name, lap_info_a, lap_info_b, output_path=None):
    corners_with_data = [c for c in comparison_results['corners'] 
                         if c['data_available'] and 'steering_delta' in c]
    
    if not corners_with_data:
        print("No steering data available")
        return
    
    corner_names = [c['name'] for c in corners_with_data]
    steering_a = [c['max_steering_a'] for c in corners_with_data]
    steering_b = [c['max_steering_b'] for c in corners_with_data]
    
    x = np.arange(len(corner_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    label_a = f"Vehicle {lap_info_a['vehicle_id']}, Lap {lap_info_a['lap']}"
    label_b = f"Vehicle {lap_info_b['vehicle_id']}, Lap {lap_info_b['lap']}"
    
    bars1 = ax.bar(x - width/2, steering_a, width, label=label_a, 
                   color='#2E86DE', alpha=0.8)
    bars2 = ax.bar(x + width/2, steering_b, width, label=label_b, 
                   color='#EE5A6F', alpha=0.8)
    
    ax.set_xlabel('Corner', fontsize=12, fontweight='bold')
    ax.set_ylabel('Max Steering Angle (degrees)', fontsize=12, fontweight='bold')
    ax.set_title(f'Steering Angle Comparison - {track_name.upper()}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(corner_names, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()

def plot_brake_comparison(comparison_results, track_name, lap_info_a, lap_info_b, output_path=None):
    corners_with_data = [c for c in comparison_results['corners'] 
                         if c['data_available'] and 'brake_delta' in c]
    
    if not corners_with_data:
        print("No brake data available")
        return
    
    corner_names = [c['name'] for c in corners_with_data]
    brake_a = [c['max_brake_a'] for c in corners_with_data]
    brake_b = [c['max_brake_b'] for c in corners_with_data]
    
    x = np.arange(len(corner_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    label_a = f"Vehicle {lap_info_a['vehicle_id']}, Lap {lap_info_a['lap']}"
    label_b = f"Vehicle {lap_info_b['vehicle_id']}, Lap {lap_info_b['lap']}"
    
    bars1 = ax.bar(x - width/2, brake_a, width, label=label_a, 
                   color='#2E86DE', alpha=0.8)
    bars2 = ax.bar(x + width/2, brake_b, width, label=label_b, 
                   color='#EE5A6F', alpha=0.8)
    
    ax.set_xlabel('Corner', fontsize=12, fontweight='bold')
    ax.set_ylabel('Max Brake Pressure (bar)', fontsize=12, fontweight='bold')
    ax.set_title(f'Brake Pressure Comparison - {track_name.upper()}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(corner_names, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()

def plot_delta_analysis(comparison_results, track_name, lap_info_a, lap_info_b, output_path=None):
    corners_with_data = [c for c in comparison_results['corners'] 
                         if c['data_available'] and 'speed_delta' in c]
    
    if not corners_with_data:
        print("No speed delta data available")
        return
    
    corner_names = [c['name'] for c in corners_with_data]
    speed_deltas = [c['speed_delta'] for c in corners_with_data]
    
    colors = ['#10AC84' if d > 0 else '#EE5A6F' for d in speed_deltas]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    bars = ax.bar(corner_names, speed_deltas, color=colors, alpha=0.8)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Corner', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speed Delta (km/h)', fontsize=12, fontweight='bold')
    
    subtitle = f"Vehicle {lap_info_a['vehicle_id']} vs Vehicle {lap_info_b['vehicle_id']}"
    ax.set_title(f'Corner Speed Delta - {track_name.upper()}\n{subtitle}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    green_patch = mpatches.Patch(color='#10AC84', label=f'Vehicle {lap_info_a["vehicle_id"]} Faster')
    red_patch = mpatches.Patch(color='#EE5A6F', label=f'Vehicle {lap_info_b["vehicle_id"]} Faster')
    ax.legend(handles=[green_patch, red_patch], fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()

def plot_classification_summary(pattern_analysis, track_name, lap_info_a, lap_info_b, output_path=None):
    classifications = {}
    for detail in pattern_analysis['corner_details']:
        classification_type = detail['classification']['type']
        if classification_type != 'normal':
            classifications[classification_type] = classifications.get(classification_type, 0) + 1
    
    if not classifications:
        print("No classification data to visualize")
        return
    
    labels = list(classifications.keys())
    sizes = list(classifications.values())
    
    colors_map = {
        'driver_mistake': '#EE5A6F',
        'different_line': '#F79F1F',
        'brake_technique': '#5F27CD',
        'entry_speed': '#00D2D3'
    }
    colors = [colors_map.get(label, '#95A5A6') for label in labels]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    subtitle = f"Vehicle {lap_info_a['vehicle_id']} vs Vehicle {lap_info_b['vehicle_id']}"
    ax.set_title(f'Corner Classification Summary - {track_name.upper()}\n{subtitle}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()
    
    plt.close()

def create_summary_visualizations(comparison_results, detailed_results, output_dir):
    import os
    import streamlit as st
    
    os.makedirs(output_dir, exist_ok=True)
    
    track_name = st.session_state.get('track_name', 'unknown')
    
    lap_info_a = {
        'vehicle_id': st.session_state.get('vehicle1_id', 'V1'),
        'lap': st.session_state.get('lap1_num', 1),
        'time': st.session_state.get('lap_time_1', 0.0)
    }
    lap_info_b = {
        'vehicle_id': st.session_state.get('vehicle2_id', 'V2'),
        'lap': st.session_state.get('lap2_num', 1),
        'time': st.session_state.get('lap_time_2', 0.0)
    }
    
    plot_steering_comparison(comparison_results, track_name, lap_info_a, lap_info_b,
                            f'{output_dir}/steering_comparison.png')
    
    plot_brake_comparison(comparison_results, track_name, lap_info_a, lap_info_b,
                         f'{output_dir}/brake_comparison.png')
    
    plot_delta_analysis(comparison_results, track_name, lap_info_a, lap_info_b,
                       f'{output_dir}/delta_analysis.png')
    
    if detailed_results and 'corners' in detailed_results:
        pattern_analysis = {'corner_details': []}
        for corner_name, data in detailed_results['corners'].items():
            pattern_analysis['corner_details'].append({
                'classification': {
                    'type': data.get('classification', 'normal')
                }
            })
        
        if pattern_analysis['corner_details']:
            plot_classification_summary(pattern_analysis, track_name, lap_info_a, lap_info_b,
                                       f'{output_dir}/classification_summary.png')

def generate_all_visualizations(telemetry_a, telemetry_b, comparison_results, 
                                pattern_analysis, corners, track_name, lap_info_a, 
                                lap_info_b, output_dir='visualizations'):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    plot_speed_traces(telemetry_a, telemetry_b, corners, track_name, lap_info_a, lap_info_b,
                     f'{output_dir}/{track_name}_speed_traces.png')
    
    plot_steering_comparison(comparison_results, track_name, lap_info_a, lap_info_b,
                            f'{output_dir}/{track_name}_steering.png')
    
    plot_brake_comparison(comparison_results, track_name, lap_info_a, lap_info_b,
                         f'{output_dir}/{track_name}_brake.png')
    
    plot_delta_analysis(comparison_results, track_name, lap_info_a, lap_info_b,
                       f'{output_dir}/{track_name}_delta.png')
    
    plot_classification_summary(pattern_analysis, track_name, lap_info_a, lap_info_b,
                               f'{output_dir}/{track_name}_classification.png')
    
    print(f"\nAll visualizations saved to {output_dir}/")