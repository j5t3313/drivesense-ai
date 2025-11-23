import streamlit as st
from pathlib import Path
import sys
import re
import os

st.set_page_config(page_title="Corner Details", page_icon="", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("Corner Details")

if not st.session_state.get('analysis_complete'):
    st.warning("Please run analysis first in the Analysis Results page")
    st.stop()

st.info(f"Reference: Vehicle {st.session_state.vehicle1_id} | Comparison: Vehicle {st.session_state.vehicle2_id}")

st.markdown("Per-corner detailed visualizations showing steering, brake, and throttle overlays")

viz_path = st.session_state.get('viz_path')
if not viz_path:
    st.error("Visualization path not found")
    st.stop()

corner_path = viz_path / "corners"

if not corner_path.exists():
    st.error("Corner visualizations not found")
    st.stop()

def natural_sort_key(path):
    parts = re.split(r'(\d+)', str(path.stem))
    return [int(p) if p.isdigit() else p for p in parts]

corner_files = sorted(corner_path.glob("*.png"), key=natural_sort_key)

if not corner_files:
    st.warning("No corner visualizations generated")
    st.stop()

detailed_results = st.session_state.get('detailed_results')

for corner_file in corner_files:
    corner_name = corner_file.stem
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(corner_name)
    
    with col2:
        if detailed_results and corner_name in detailed_results['corners']:
            analysis = detailed_results['corners'][corner_name]
            
            if analysis.get('vehicle'):
                st.markdown(f"**Vehicle:** {analysis['vehicle']}")
            
            st.markdown(f"**Classification:** {analysis['classification']}")
            st.markdown(f"**Confidence:** {analysis['confidence']:.1f}%")
            st.markdown(f"**Priority:** {analysis['recommendation']['priority']}")
    
    st.image(str(corner_file))
    
    if detailed_results and corner_name in detailed_results['corners']:
        analysis = detailed_results['corners'][corner_name]
        
        with st.expander("Detailed Analysis"):
            st.markdown(f"**Recommendation:** {analysis['recommendation']['action']}")
            st.markdown(f"**Explanation:** {analysis['recommendation']['explanation']}")
            
            if analysis['evidence']:
                st.markdown("**Evidence:**")
                for key, value in analysis['evidence'].items():
                    if isinstance(value, (int, float)):
                        st.markdown(f"- {key}: {value:.4f}")
                    else:
                        st.markdown(f"- {key}: {value}")

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
