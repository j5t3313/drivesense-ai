import streamlit as st
import pandas as pd
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from track_configs import TRACK_CONFIGS
from lap_time_loader import find_lap_time_file, load_lap_times_from_file, get_lap_data
from endurance_data_loader import load_endurance_data, find_endurance_file, match_vehicle_to_endurance, get_lap_context

st.set_page_config(page_title="Select Data", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #ffffff;
        color: #24292f;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        color: #24292f !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    p, .stMarkdown {
        color: #24292f !important;
    }
    
    strong {
        color: #24292f !important;
    }
    
    .stMetric {
        background-color: #f6f8fa !important;
        padding: 20px !important;
        border-radius: 6px !important;
        border: 1px solid #d0d7de !important;
    }
    
    .stMetric label {
        color: #57606a !important;
        font-size: 16px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #24292f !important;
        font-size: 32px !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #24292f !important;
    }
    
    .stSelectbox > label {
        color: #24292f !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 1px solid #d0d7de !important;
        color: #24292f !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #0969da !important;
    }
    
    .stRadio > label {
        color: #24292f !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stRadio > div {
        background-color: #f6f8fa;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #d0d7de;
    }
    
    .stRadio > div label {
        color: #24292f !important;
    }
    
    .stButton > button {
        background-color: #6e7781 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    
    .stButton > button:hover {
        background-color: #57606a !important;
    }
    
    .stButton > button:disabled {
        background-color: #d0d7de !important;
        color: #57606a !important;
    }
    
    .stAlert {
        background-color: #f6f8fa !important;
        border: 1px solid #d0d7de !important;
        color: #24292f !important;
    }
    
    hr {
        border-color: #d0d7de !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f6f8fa !important;
        border-right: 1px solid #d0d7de !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #24292f !important;
    }
    
    [data-testid="stSidebar"] a {
        color: #0969da !important;
    }
    
    .stSlider > label {
        color: #24292f !important;
        font-weight: 600 !important;
    }
    
    .stCheckbox > label {
        color: #24292f !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Select Data")

PROCESSED_DATA_DIR = Path(os.getenv('PROCESSED_DATA_DIR', 'processed_data'))

if not PROCESSED_DATA_DIR.exists():
    st.error("Processed data directory not found. Run preprocess_data.py first.")
    st.stop()

all_tracks = [d.name for d in PROCESSED_DATA_DIR.iterdir() if d.is_dir()]
available_tracks = [t for t in all_tracks if t in ['barber', 'indianapolis']]

if not available_tracks:
    st.error("No processed track data found. Run preprocess_data.py first.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Track Selection")
    
    track_name = st.selectbox(
        "Select Track",
        options=available_tracks,
        key='track_selector'
    )
    
    st.session_state.track_name = track_name
    
    if track_name:
        config = TRACK_CONFIGS.get(track_name, {})
        if isinstance(config, dict):
            track_display_name = config.get('name', track_name.replace('-', ' ').title())
            st.info(f"Track: {track_display_name}")
            if 'corners' in config:
                st.metric("Corners Defined", len(config['corners']))
        else:
            st.info(f"Track: {track_name.replace('-', ' ').title()}")
    
    metadata_file = PROCESSED_DATA_DIR / track_name / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
            st.session_state.track_metadata = metadata
    else:
        st.error(f"Metadata file not found for {track_name}")
        st.stop()
    
    has_distance_data = False
    for race in ['R1', 'R2']:
        if race in metadata:
            for vehicle_id, laps in metadata[race].items():
                if laps:
                    sample_lap_file = PROCESSED_DATA_DIR / track_name / laps[0]['file']
                    if sample_lap_file.exists():
                        try:
                            sample_data = pd.read_csv(sample_lap_file)
                            distance_cols = ['lapdist_dls', 'trigger_lapdist_dls', 'Lap', 'distance']
                            for col in distance_cols:
                                if col in sample_data.columns and sample_data[col].notna().sum() > 10:
                                    has_distance_data = True
                                    break
                            if has_distance_data:
                                break
                        except:
                            pass
                if has_distance_data:
                    break
        if has_distance_data:
            break
    
    if not has_distance_data:
        st.warning(f"[WARNING] Track '{track_name}' has no distance data available. Corner-by-corner analysis and visualizations will not be available. Only aggregate lap-level analysis will be performed.")
    
    for race in ['R1', 'R2']:
        lap_time_file = find_lap_time_file(PROCESSED_DATA_DIR / track_name, race)
        if lap_time_file:
            lap_times_dict = load_lap_times_from_file(lap_time_file)
            if lap_times_dict:
                sample_vehicle = list(lap_times_dict.keys())[0]
                sample_lap = list(lap_times_dict[sample_vehicle].keys())[0]
                sample_data = lap_times_dict[sample_vehicle][sample_lap]
                
                if isinstance(sample_data, dict) and sample_data.get('s1') is not None:
                    st.success(f"{race}: Endurance timing data available (sectors, top speed, flags)")
                    break
                else:
                    st.info(f"{race}: Basic timing data available (telemetry-derived)")
                    break

with col2:
    st.subheader("Analysis Mode")
    
    analysis_mode = st.radio(
        "Select Analysis Type",
        options=['Single Lap Comparison', 'Multi-Lap Consistency'],
        horizontal=False,
        key='analysis_mode_selector'
    )
    st.session_state.analysis_mode = analysis_mode
    
    if analysis_mode == 'Single Lap Comparison':
        st.info("Compare two individual laps (same or different races)")
    else:
        st.info("Analyze all laps for a single vehicle to identify consistency patterns")

st.markdown("---")

if st.session_state.get('analysis_mode') == 'Single Lap Comparison':
    
    clean_laps_only = st.checkbox(
        "Clean laps only (exclude pit laps and yellow flags)",
        value=False,
        key='clean_laps_filter'
    )
    st.session_state.clean_laps_only = clean_laps_only
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vehicle 1 (Reference)")
        
        race1 = st.radio(
            "Select Race",
            options=['R1', 'R2'],
            horizontal=True,
            key='race1_selector'
        )
        st.session_state.race1 = race1
        
        if metadata.get(race1):
            vehicles1 = list(metadata[race1].keys())
        else:
            st.warning(f"No data for {race1}")
            st.stop()
        
        vehicle1 = st.selectbox(
            "Select Vehicle",
            options=vehicles1,
            key='vehicle1_selector'
        )
        st.session_state.vehicle1_id = vehicle1
        
        if vehicle1 and vehicle1 in metadata[race1]:
            laps1 = metadata[race1][vehicle1]
            
            lap_time_file = find_lap_time_file(PROCESSED_DATA_DIR / track_name, race1)
            if lap_time_file:
                lap_times_dict = load_lap_times_from_file(lap_time_file)
                st.session_state.lap_times_dict_r1 = lap_times_dict
            else:
                lap_times_dict = None
                st.session_state.lap_times_dict_r1 = None
            
            if clean_laps_only and lap_times_dict:
                from lap_time_loader import is_clean_lap
                lap_numbers1 = [lap['lap'] for lap in laps1 if is_clean_lap(lap_times_dict, vehicle1, lap['lap'])]
            else:
                lap_numbers1 = [lap['lap'] for lap in laps1]
            
            if not lap_numbers1:
                st.warning("No laps match filter criteria")
                st.stop()
            
            lap1 = st.selectbox(
                f"Select Lap ({len(lap_numbers1)} available)",
                options=lap_numbers1,
                key='lap1_selector'
            )
            st.session_state.lap1_num = lap1
            
            selected_lap1 = next(l for l in laps1 if l['lap'] == lap1)
            st.metric("Distance Coverage", f"{selected_lap1['distance_range']:.0f}m")
            st.metric("Data Points", selected_lap1['data_points'])
            
            if lap_times_dict:
                lap_data = get_lap_data(lap_times_dict, vehicle1, lap1)
                if lap_data:
                    lap_time_value = lap_data.get('lap_time') or lap_data.get('time')
                    if lap_time_value:
                        st.metric("Lap Time", f"{lap_time_value:.3f}s")
                    if lap_data.get('flag'):
                        flag_display = {'GF': 'Green', 'FCY': 'Yellow', 'FF': 'Finish'}.get(lap_data['flag'], lap_data['flag'])
                        st.info(f"Flag: {flag_display}")
                    if lap_data.get('s1') and lap_data.get('s2') and lap_data.get('s3'):
                        st.caption(f"Sectors: S1 {lap_data['s1']:.3f}s | S2 {lap_data['s2']:.3f}s | S3 {lap_data['s3']:.3f}s")
            
            st.session_state.lap1_file = str(PROCESSED_DATA_DIR / track_name / selected_lap1['file'])

    with col2:
        st.subheader("Vehicle 2 (Comparison)")
        
        race2 = st.radio(
            "Select Race",
            options=['R1', 'R2'],
            horizontal=True,
            key='race2_selector'
        )
        st.session_state.race2 = race2
        
        if metadata.get(race2):
            vehicles2 = list(metadata[race2].keys())
        else:
            st.warning(f"No data for {race2}")
            st.stop()
        
        vehicle2 = st.selectbox(
            "Select Vehicle",
            options=vehicles2,
            key='vehicle2_selector'
        )
        st.session_state.vehicle2_id = vehicle2
        
        if vehicle2 and vehicle2 in metadata[race2]:
            laps2 = metadata[race2][vehicle2]
            
            lap_time_file = find_lap_time_file(PROCESSED_DATA_DIR / track_name, race2)
            if lap_time_file:
                lap_times_dict = load_lap_times_from_file(lap_time_file)
                st.session_state.lap_times_dict_r2 = lap_times_dict
            else:
                lap_times_dict = None
                st.session_state.lap_times_dict_r2 = None
            
            if clean_laps_only and lap_times_dict:
                from lap_time_loader import is_clean_lap
                lap_numbers2 = [lap['lap'] for lap in laps2 if is_clean_lap(lap_times_dict, vehicle2, lap['lap'])]
            else:
                lap_numbers2 = [lap['lap'] for lap in laps2]
            
            if not lap_numbers2:
                st.warning("No laps match filter criteria")
                st.stop()
            
            lap2 = st.selectbox(
                f"Select Lap ({len(lap_numbers2)} available)",
                options=lap_numbers2,
                key='lap2_selector'
            )
            st.session_state.lap2_num = lap2
            
            selected_lap2 = next(l for l in laps2 if l['lap'] == lap2)
            st.metric("Distance Coverage", f"{selected_lap2['distance_range']:.0f}m")
            st.metric("Data Points", selected_lap2['data_points'])
            
            if lap_times_dict:
                lap_data = get_lap_data(lap_times_dict, vehicle2, lap2)
                if lap_data:
                    lap_time_value = lap_data.get('lap_time') or lap_data.get('time')
                    if lap_time_value:
                        st.metric("Lap Time", f"{lap_time_value:.3f}s")
                    if lap_data.get('flag'):
                        flag_display = {'GF': 'Green', 'FCY': 'Yellow', 'FF': 'Finish'}.get(lap_data['flag'], lap_data['flag'])
                        st.info(f"Flag: {flag_display}")
                    if lap_data.get('s1') and lap_data.get('s2') and lap_data.get('s3'):
                        st.caption(f"Sectors: S1 {lap_data['s1']:.3f}s | S2 {lap_data['s2']:.3f}s | S3 {lap_data['s3']:.3f}s")
            
            st.session_state.lap2_file = str(PROCESSED_DATA_DIR / track_name / selected_lap2['file'])
    
    st.markdown("---")
    
    if st.button("Run Analysis", use_container_width=True):
        if not all([
            st.session_state.get('track_name'),
            st.session_state.get('vehicle1_id'),
            st.session_state.get('vehicle2_id'),
            st.session_state.get('lap1_num'),
            st.session_state.get('lap2_num'),
            st.session_state.get('lap1_file'),
            st.session_state.get('lap2_file')
        ]):
            st.error("Please complete all selections")
        else:
            st.session_state.analysis_complete = False
            st.session_state.trigger_analysis = True
            st.switch_page("pages/2_Analysis_Results.py")

else:
    st.subheader("Multi-Lap Consistency Analysis")
    
    clean_laps_only = st.checkbox(
        "Clean laps only (exclude pit laps and yellow flags)",
        value=False,
        key='clean_laps_filter_multilap'
    )
    st.session_state.clean_laps_only = clean_laps_only
    
    col1, col2 = st.columns(2)
    
    with col1:
        race = st.radio(
            "Select Race",
            options=['R1', 'R2'],
            horizontal=True,
            key='multilap_race_selector'
        )
        st.session_state.race = race
        
        if metadata.get(race):
            vehicles = list(metadata[race].keys())
        else:
            st.warning(f"No data for {race}")
            st.stop()
        
        vehicle = st.selectbox(
            "Select Vehicle",
            options=vehicles,
            key='multilap_vehicle_selector'
        )
        st.session_state.vehicle1_id = vehicle
        
        if vehicle and vehicle in metadata[race]:
            laps = metadata[race][vehicle]
            
            lap_time_file = find_lap_time_file(PROCESSED_DATA_DIR / track_name, race)
            if lap_time_file:
                lap_times_dict = load_lap_times_from_file(lap_time_file)
                st.session_state.lap_times_dict = lap_times_dict
            else:
                lap_times_dict = None
                st.session_state.lap_times_dict = None
            
            if clean_laps_only and lap_times_dict:
                from lap_time_loader import is_clean_lap
                available_laps = [l for l in laps if is_clean_lap(lap_times_dict, vehicle, l['lap'])]
            else:
                available_laps = laps
            
            if not available_laps:
                st.warning("No laps match filter criteria")
                st.stop()
            
            st.metric("Total Laps Available", len(available_laps))
            
            lap_range = st.slider(
                "Select Lap Range to Analyze",
                min_value=min([l['lap'] for l in available_laps]),
                max_value=max([l['lap'] for l in available_laps]),
                value=(min([l['lap'] for l in available_laps]), max([l['lap'] for l in available_laps])),
                key='lap_range_selector'
            )
            st.session_state.lap_range = lap_range
            
            selected_laps = [l for l in available_laps if lap_range[0] <= l['lap'] <= lap_range[1]]
            st.session_state.multilap_files = [
                str(PROCESSED_DATA_DIR / track_name / lap['file']) 
                for lap in selected_laps
            ]
            st.session_state.multilap_numbers = [lap['lap'] for lap in selected_laps]
            
            st.info(f"Will analyze {len(selected_laps)} laps (Lap {lap_range[0]} to Lap {lap_range[1]})")
    
    with col2:
        st.subheader("Analysis Options")
        
        consistency_metric = st.selectbox(
            "Consistency Metric",
            options=['Lap Time Variation', 'Corner Performance', 'Driving Style Stability'],
            key='consistency_metric_selector'
        )
        
        show_progression = st.checkbox(
            "Show Performance Progression",
            value=True,
            key='show_progression'
        )
        
        st.markdown("**Analysis will show:**")
        st.markdown("- Lap-to-lap consistency scores")
        st.markdown("- Corner performance variation")
        st.markdown("- Improving/deteriorating trends")
        st.markdown("- Outlier lap identification")
        
        if lap_times_dict:
            sample_data = get_lap_data(lap_times_dict, vehicle, selected_laps[0]['lap'])
            if sample_data and sample_data.get('s1') is not None:
                st.success("Sector-level consistency will be included")
    
    st.markdown("---")
    
    if st.button("Run Multi-Lap Analysis", use_container_width=True):
        if not all([
            st.session_state.get('track_name'),
            st.session_state.get('vehicle1_id'),
            st.session_state.get('multilap_files'),
            st.session_state.get('multilap_numbers')
        ]):
            st.error("Please complete all selections")
        else:
            st.session_state.multilap_analysis_complete = False
            st.session_state.trigger_multilap_analysis = True
            st.switch_page("pages/2_Analysis_Results.py")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Reset All", use_container_width=True, type="primary"):
    keys_to_clear = [
        'telemetry_path', 'lap_times_path', 'track_name', 'analysis_complete',
        'vehicle1_id', 'vehicle2_id', 'lap1_num', 'lap2_num',
        'tel1', 'tel2', 'lap_time_1', 'lap_time_2',
        'comparison_results', 'detailed_results', 'viz_path',
        'distance_available', 'has_gradient_analysis', 'has_aggregate_analysis',
        'aggregate_results', 'aggregate_report', 'has_visualizations',
        'track_metadata', 'analysis_mode', 'race1', 'race2',
        'lap1_file', 'lap2_file', 'multilap_files', 'multilap_numbers',
        'multilap_analysis_complete', 'consistency_results', 'consistency_report',
        'trigger_analysis', 'trigger_multilap_analysis',
        'lap_times_dict', 'lap_times_dict_r1', 'lap_times_dict_r2',
        'lap_data_1', 'lap_data_2', 'race', 'lap_range'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    import shutil
    viz_dir = Path("visualizations")
    if viz_dir.exists():
        shutil.rmtree(viz_dir)
    
    st.success("All data cleared!")
    st.rerun()
