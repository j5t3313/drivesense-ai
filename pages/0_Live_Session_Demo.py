import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import time
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from live_analysis import LiveRaceAnalyzer
from race_simulator import setup_demo_session

st.set_page_config(page_title="Live Race Analysis", page_icon="🏁", layout="wide")

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
    
    .stExpander {
        background-color: #f6f8fa !important;
        border: 1px solid #d0d7de !important;
        border-radius: 6px !important;
    }
    
    .stDataFrame {
        background-color: #ffffff !important;
    }
    
    .stSlider > label {
        color: #24292f !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔴 Live Race Analysis Demo")

PROCESSED_DATA_DIR = Path("processed_data")

if 'live_analyzer' not in st.session_state:
    st.session_state.live_analyzer = None
if 'demo_lap_files' not in st.session_state:
    st.session_state.demo_lap_files = []
if 'demo_lap_numbers' not in st.session_state:
    st.session_state.demo_lap_numbers = []
if 'demo_current_index' not in st.session_state:
    st.session_state.demo_current_index = 0
if 'latest_results' not in st.session_state:
    st.session_state.latest_results = None
if 'final_summary' not in st.session_state:
    st.session_state.final_summary = None

available_tracks = [d.name for d in PROCESSED_DATA_DIR.iterdir() if d.is_dir()] if PROCESSED_DATA_DIR.exists() else []

if not available_tracks:
    st.error("No processed track data found.")
    st.stop()

with st.sidebar:
    st.header("Session Configuration")
    
    is_session_active = st.session_state.live_analyzer is not None
    
    if is_session_active:
        st.warning("⚠️ Session active - stop to change settings")
    
    st.markdown("---")
    
    track_name = 'barber'
    st.info("**Track:** Barber Motorsports Park (Demo)")
    
    metadata_file = PROCESSED_DATA_DIR / track_name / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
    else:
        st.error(f"Metadata not found for {track_name}")
        st.stop()
    
    race = st.radio(
        "Race",
        options=['R1', 'R2'],
        horizontal=True,
        key='live_race',
        disabled=is_session_active
    )
    
    if race in metadata:
        vehicles = list(metadata[race].keys())
        vehicle_id = st.selectbox(
            "Vehicle",
            options=vehicles,
            key='live_vehicle',
            disabled=is_session_active
        )
    else:
        st.warning(f"No data for {race}")
        st.stop()
    
    st.markdown("---")
    st.subheader("Demo Configuration")
    
    if vehicle_id in metadata[race]:
        all_laps = metadata[race][vehicle_id]
        lap_numbers = [l['lap'] for l in all_laps]
        
        lap_range = st.slider(
            "Lap Range",
            min_value=min(lap_numbers),
            max_value=max(lap_numbers),
            value=(min(lap_numbers), min(min(lap_numbers) + 14, max(lap_numbers))),
            key='live_lap_range',
            disabled=is_session_active
        )
        
        st.info(f"Will analyze {lap_range[1] - lap_range[0] + 1} laps")

st.markdown("---")

if st.session_state.live_analyzer is None and st.session_state.final_summary is None:
    st.header("Session Setup")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Track", "Barber Motorsports Park")
    
    with col2:
        st.metric("Race", st.session_state.get('live_race', 'Not selected'))
    
    with col3:
        st.metric("Vehicle", st.session_state.get('live_vehicle', 'Not selected'))
    
    if st.session_state.get('live_lap_range'):
        start_lap, end_lap = st.session_state.live_lap_range
        st.info(f"📊 Will analyze {end_lap - start_lap + 1} laps (Laps {start_lap}-{end_lap}) for **{st.session_state.live_vehicle}**")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    can_start = all([
        st.session_state.get('live_race'),
        st.session_state.get('live_vehicle')
    ])
    
    if not can_start:
        st.warning("⚙️ Complete configuration in sidebar first")
    
    if st.button("▶ Start Session", type="primary", disabled=(st.session_state.live_analyzer is not None or not can_start)):
        st.session_state.live_analyzer = LiveRaceAnalyzer(
            track_name=track_name,
            vehicle_id=st.session_state.live_vehicle,
            race=st.session_state.live_race,
            processed_data_dir=str(PROCESSED_DATA_DIR)
        )
        
        try:
            lap_files = setup_demo_session(
                track_name,
                st.session_state.live_vehicle,
                st.session_state.live_race,
                st.session_state.live_lap_range,
                str(PROCESSED_DATA_DIR)
            )
            
            st.session_state.demo_lap_files = lap_files
            st.session_state.demo_lap_numbers = list(range(st.session_state.live_lap_range[0], st.session_state.live_lap_range[1] + 1))
            st.session_state.demo_current_index = 0
            st.session_state.latest_results = None
            
        except Exception as e:
            st.error(f"Error setting up demo: {e}")
            st.session_state.live_analyzer = None
            st.stop()
        
        st.success("Session started! Click 'Process Next Lap' below.")
        time.sleep(1)
        st.rerun()

with col2:
    if st.button("⏹ Stop Session", disabled=st.session_state.live_analyzer is None):
        if st.session_state.live_analyzer:
            summary = st.session_state.live_analyzer.end_session()
            st.session_state.final_summary = summary
        
        st.session_state.live_analyzer = None
        st.session_state.demo_lap_files = []
        st.session_state.demo_lap_numbers = []
        st.session_state.demo_current_index = 0
        st.session_state.latest_results = None
        
        st.success("Session stopped")
        time.sleep(1)
        st.rerun()

with col3:
    if st.button("🔄 Reset", disabled=st.session_state.live_analyzer is None):
        st.session_state.live_analyzer = None
        st.session_state.demo_lap_files = []
        st.session_state.demo_lap_numbers = []
        st.session_state.demo_current_index = 0
        st.session_state.latest_results = None
        st.session_state.final_summary = None
        
        st.success("Session reset")
        time.sleep(1)
        st.rerun()

st.markdown("---")

if st.session_state.live_analyzer is not None:
    state = st.session_state.live_analyzer.get_state()
    
    st.success(f"🔴 **SESSION ACTIVE** - Analyzing **{state['vehicle_id']}** at **{state['track_name'].replace('-', ' ').title()}** ({state['race']})")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Laps Processed", state['laps_processed'])
    
    with col2:
        if state['reference_lap']:
            st.metric("Reference Lap", f"Lap {state['reference_lap']}")
        else:
            st.metric("Reference Lap", "Waiting...")
    
    with col3:
        if state['reference_lap_time']:
            st.metric("Best Lap Time", f"{state['reference_lap_time']:.3f}s")
        else:
            st.metric("Best Lap Time", "—")
    
    with col4:
        total_laps = len(st.session_state.demo_lap_files)
        current = st.session_state.demo_current_index
        st.metric("Progress", f"{current}/{total_laps}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.session_state.demo_current_index < len(st.session_state.demo_lap_files):
            if st.button("▶ Process Next Lap", type="primary", use_container_width=True):
                lap_file = st.session_state.demo_lap_files[st.session_state.demo_current_index]
                lap_num = st.session_state.demo_lap_numbers[st.session_state.demo_current_index]
                
                with st.spinner(f"Processing Lap {lap_num}..."):
                    results = st.session_state.live_analyzer.process_new_lap(lap_file, lap_num)
                    st.session_state.latest_results = results
                    st.session_state.demo_current_index += 1
                
                st.rerun()
        else:
            st.success("✅ All laps processed!")
    
    with col2:
        if st.session_state.demo_current_index < len(st.session_state.demo_lap_files):
            next_lap = st.session_state.demo_lap_numbers[st.session_state.demo_current_index]
            st.info(f"Ready to process Lap {next_lap}")
        else:
            st.info("Click 'Stop Session' to view final summary")
    
    if st.session_state.latest_results:
        st.markdown("---")
        st.header(f"📊 Latest Lap (Lap {st.session_state.latest_results['lap']}) Results")
        
        results = st.session_state.latest_results
        
        if results['type'] == 'skipped':
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"⚠️ {results.get('message', 'Lap skipped')}")
            
            with col2:
                if results.get('lap_data') and results['lap_data'].get('flag'):
                    from lap_time_loader import get_flag_emoji
                    flag = results['lap_data']['flag']
                    flag_emoji = get_flag_emoji(flag)
                    st.warning(f"{flag_emoji} {flag}")
        
        elif results['type'] == 'baseline':
            st.info(f"🎯 {results['message']}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if results.get('lap_time'):
                    st.metric("Baseline Lap Time", f"{results['lap_time']:.3f}s")
                st.metric("Corners Recorded", results['corners_recorded'])
            
            with col2:
                if results.get('lap_data') and results['lap_data'].get('flag'):
                    from lap_time_loader import get_flag_emoji
                    flag = results['lap_data']['flag']
                    flag_emoji = get_flag_emoji(flag)
                    st.metric("Flag", f"{flag_emoji} {flag}")
        
        else:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if results.get('new_reference'):
                    st.success(f"🏆 {results.get('message', 'New best lap!')}")
                else:
                    if results.get('lap_time') is not None:
                        if results['delta_to_reference'] is not None:
                            delta = results['delta_to_reference']
                            if delta > 0:
                                st.warning(f"⏱️ Lap Time: {results['lap_time']:.3f}s (+{delta:.3f}s vs reference)")
                            else:
                                st.success(f"⏱️ Lap Time: {results['lap_time']:.3f}s ({delta:.3f}s vs reference)")
                        else:
                            st.info(f"⏱️ Lap Time: {results['lap_time']:.3f}s")
                    else:
                        st.info("⏱️ Lap Time: Unable to calculate")
                
                if results.get('top_speed_delta'):
                    st.metric("Top Speed vs Reference", f"{results['top_speed_delta']:+.1f} km/h")
                
                if results.get('lap_data'):
                    lap_data = results['lap_data']
                    if lap_data.get('s1') and lap_data.get('s2') and lap_data.get('s3'):
                        st.caption(f"S1: {lap_data['s1']:.3f}s | S2: {lap_data['s2']:.3f}s | S3: {lap_data['s3']:.3f}s")
                    
                    if lap_data.get('top_speed'):
                        st.caption(f"Top Speed: {lap_data['top_speed']:.1f} km/h")
            
            with col2:
                if results.get('alerts'):
                    st.error(f"⚠️ {len(results['alerts'])} Alert(s)")
            
            with col3:
                if results.get('lap_data') and results['lap_data'].get('flag'):
                    from lap_time_loader import get_flag_emoji
                    flag = results['lap_data']['flag']
                    flag_emoji = get_flag_emoji(flag)
                    if flag == 'GF':
                        st.success(f"{flag_emoji} {flag}")
                    elif flag in ['FCY', 'SC']:
                        st.warning(f"{flag_emoji} {flag}")
                    else:
                        st.info(f"{flag_emoji} {flag}")
            
            if results.get('corners'):
                mistakes = []
                different_lines = []
                brake_technique = []
                driver_style = []
                clean_corners = []
                
                for corner_name, corner_result in results['corners'].items():
                    classification = corner_result['classification']
                    confidence = corner_result['confidence']
                    
                    if classification == 'driver_mistake' and confidence > 0.75:
                        mistakes.append((corner_name, confidence))
                    elif classification == 'different_line':
                        different_lines.append(corner_name)
                    elif classification == 'brake_technique':
                        brake_technique.append(corner_name)
                    elif classification == 'driver_style':
                        driver_style.append(corner_name)
                    else:
                        clean_corners.append(corner_name)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mistakes", len(mistakes), delta=None, delta_color="inverse")
                with col2:
                    st.metric("Different Lines", len(different_lines))
                with col3:
                    st.metric("Clean", len(clean_corners), delta=None, delta_color="normal")
                
                if mistakes:
                    st.error(f"**Issues at:** {', '.join([f'{c} ({conf*100:.0f}%)' for c, conf in mistakes])}")
                elif different_lines:
                    st.warning(f"**Line variations at:** {', '.join(different_lines)}")
                elif brake_technique:
                    st.info(f"**Brake technique differences at:** {', '.join(brake_technique)}")
                elif driver_style:
                    st.info(f"**Style variations at:** {', '.join(driver_style)}")
                else:
                    st.success("**All corners executed cleanly!**")
                
                st.markdown("---")
                st.subheader("Detailed Corner Analysis")
                
                for corner_name, corner_result in results['corners'].items():
                    classification = corner_result['classification']
                    confidence = corner_result['confidence']
                    description = corner_result.get('description', '')
                    evidence = corner_result.get('evidence', [])
                    
                    with st.expander(
                        f"**{corner_name}**" + 
                        (f" - 🔴 Mistake ({confidence*100:.0f}%)" if classification == 'driver_mistake' and confidence > 0.75 
                         else f" - 🟡 Different line" if classification == 'different_line'
                         else f" - 🔵 Style variation" if classification == 'driver_style'
                         else " - 🟢 Clean"),
                        expanded=(classification == 'driver_mistake' and confidence > 0.75)
                    ):
                        st.markdown(f"**Classification:** {classification.replace('_', ' ').title()}")
                        st.markdown(f"**Confidence:** {confidence*100:.0f}%")
                        st.markdown(f"**Analysis:** {description}")
                        
                        if evidence:
                            st.markdown("**Telemetry Evidence:**")
                            for ev in evidence:
                                st.markdown(f"- {ev}")
                        
                        if classification == 'driver_mistake' and confidence > 0.75:
                            st.error("**Coaching:** Focus on consistency at this corner. You executed it correctly on your reference lap - repeat that approach.")
                        elif classification == 'different_line':
                            st.warning("**Coaching:** You're using a different racing line than your reference lap. If reference was faster, revert to that line.")
                        elif classification == 'driver_style':
                            st.info("**Coaching:** Different driving style detected. Consider which approach (smooth vs aggressive) works better for this corner.")

if st.session_state.final_summary and st.session_state.live_analyzer is None:
    st.markdown("---")
    st.header("SESSION SUMMARY REPORT")
    
    summary = st.session_state.final_summary
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Laps", summary['laps_processed'])
    with col2:
        if summary['reference_lap_time']:
            st.metric("Best Lap Time", f"{summary['reference_lap_time']:.3f}s")
        else:
            st.metric("Best Lap Time", "N/A")
    with col3:
        st.metric("Total Alerts", summary['total_alerts'])
    with col4:
        if summary.get('laptime_analysis'):
            st.metric("Lap Time Range", f"{summary['laptime_analysis']['range']:.3f}s")
        else:
            st.metric("Lap Time Range", "N/A")
    
    st.markdown("---")
    st.subheader("LAP TIME ANALYSIS")
    
    if summary.get('laptime_analysis'):
        lt = summary['laptime_analysis']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fastest Lap", f"{lt['fastest']:.3f}s")
            st.metric("Slowest Lap", f"{lt['slowest']:.3f}s")
        with col2:
            st.metric("Average Lap Time", f"{lt['mean']:.3f}s")
            st.metric("Standard Deviation", f"{lt['std']:.3f}s")
        with col3:
            st.metric("Consistency Score", f"{lt['consistency_score']:.1f}/100")
            if 'trend' in lt:
                trend_emoji = {'improving': '[UP]', 'deteriorating': '[DOWN]', 'stable': '[->]'}
                st.metric("Performance Trend", f"{trend_emoji.get(lt['trend'], '[->]')} {lt['trend'].upper()}")
        
        if summary['lap_times']:
            st.markdown("**All Lap Times:**")
            lap_times_text = []
            for lt_data in summary['lap_times']:
                if lt_data['time']:
                    lap_times_text.append(f"Lap {lt_data['lap']}: {lt_data['time']:.3f}s")
            st.text(" | ".join(lap_times_text))
    else:
        st.warning("Insufficient lap time data for analysis")
    
    st.markdown("---")
    st.subheader("STEERING ANALYSIS")
    
    if summary.get('steering_metrics'):
        sm = summary['steering_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Abs Steering", f"{sm['mean_abs_steering']:.2f}°")
        with col2:
            st.metric("Max Abs Steering", f"{sm['max_abs_steering']:.2f}°")
        with col3:
            st.metric("Std Deviation", f"{sm['std_steering']:.2f}°")
        with col4:
            st.metric("Smoothness Score", f"{sm['smoothness']:.1f}/100")
        
        if sm['smoothness'] >= 80:
            st.success("Excellent steering smoothness - very controlled inputs")
        elif sm['smoothness'] >= 60:
            st.info("Good steering smoothness - minor corrections present")
        else:
            st.warning("Poor steering smoothness - excessive corrections detected")
    else:
        st.warning("No steering data available")
    
    st.markdown("---")
    st.subheader("BRAKE ANALYSIS")
    
    if summary.get('brake_metrics'):
        bm = summary['brake_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Brake Pressure", f"{bm['mean_brake']:.1f} bar")
        with col2:
            st.metric("Max Brake Pressure", f"{bm['max_brake']:.1f} bar")
        with col3:
            st.metric("Brake Applications", bm['brake_applications'])
        with col4:
            st.metric("Consistency Score", f"{bm['consistency']:.1f}/100")
        
        if bm['consistency'] >= 80:
            st.success("Excellent brake consistency - very repeatable braking")
        elif bm['consistency'] >= 60:
            st.info("Good brake consistency - minor variations present")
        else:
            st.warning("Poor brake consistency - inconsistent brake application")
    else:
        st.warning("No brake data available")
    
    st.markdown("---")
    st.subheader("THROTTLE ANALYSIS")
    
    if summary.get('throttle_metrics'):
        tm = summary['throttle_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Throttle", f"{tm['mean_throttle']:.1f}%")
        with col2:
            st.metric("Full Throttle %", f"{tm['full_throttle_pct']:.1f}%")
        with col3:
            st.metric("Std Deviation", f"{tm['std_throttle']:.1f}%")
        with col4:
            st.metric("Confidence Score", f"{tm['confidence']:.1f}/100")
        
        if tm['confidence'] >= 80:
            st.success("Excellent throttle confidence - aggressive throttle application")
        elif tm['confidence'] >= 60:
            st.info("Good throttle confidence - moderate throttle use")
        else:
            st.warning("Low throttle confidence - conservative on throttle")
    else:
        st.warning("No throttle data available")
    
    st.markdown("---")
    st.subheader("CORNER PERFORMANCE")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if summary['problem_corners']:
            st.error(f"**Problem Corners ({len(summary['problem_corners'])}):**")
            for corner in summary['problem_corners'][:5]:
                st.markdown(f"- **{corner['corner']}**: {corner['score']:.1f}/100 ({corner['trend']})")
        else:
            st.success("No problem corners identified!")
    
    with col2:
        if summary['good_corners']:
            st.success(f"**Strong Corners ({len(summary['good_corners'])}):**")
            for corner in summary['good_corners'][:5]:
                st.markdown(f"- **{corner['corner']}**: {corner['score']:.1f}/100")
        else:
            st.info("No standout strong corners")
    
    if st.button("Clear Summary and Start New Session", type="primary"):
        st.session_state.final_summary = None
        st.rerun()

if st.session_state.live_analyzer is None and st.session_state.final_summary is None:
    st.info("Click 'Start Session' to begin live race analysis")
    st.markdown("""
    ### How it works:
    
    **Setup:**
    1. Configure session in sidebar (track, race, vehicle, lap range)
    2. Click "Start Session"
    3. Click "Process Next Lap" to analyze each lap sequentially
    4. View real-time analysis after each lap
    5. Click "Stop Session" when finished to see full summary
    
    ### Features:
    - Lap-by-lap comparison to reference lap
    - Corner-by-corner behavioral classification
    - Mistake detection with confidence scores
    - Consistency tracking
    - Final session summary with detailed metrics
    
    **Note:** Process laps at your own pace by clicking "Process Next Lap" button.
    """)
