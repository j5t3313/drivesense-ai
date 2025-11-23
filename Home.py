import streamlit as st
import sys
from pathlib import Path

st.set_page_config(
    page_title="DriveSense AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
from cloud_storage import CloudStorage

if os.getenv('R2_ENDPOINT'):
    storage = CloudStorage()
    if storage.ensure_data_downloaded():
        os.environ['PROCESSED_DATA_DIR'] = str(storage.get_local_data_path())

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
    
    .technical-box {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 6px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .code-inline {
        background-color: #f6f8fa;
        color: #0969da;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
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
        background-color: #f6f8fa !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    
    .stButton > button:hover {
        background-color: #2da44e !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #24292f !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
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
</style>
""", unsafe_allow_html=True)

st.title("🏁 DriveSense AI 🏁")
st.markdown("<p style='font-size: 1.2rem; color: #57606a; margin-top: -0.5rem;'><strong>Gradient-based behavioral classification for racing telemetry</strong></p>", unsafe_allow_html=True)

st.markdown("---")

st.subheader("The Problem with Traditional Telemetry Analysis")
st.markdown("""
Existing systems rely on speed-based metrics and simple time deltas to show **WHERE** time is lost. 
This approach has critical limitations:

- Cannot distinguish intentional technique variations from mistakes
- No causal attribution for performance differences
- Requires manual interpretation by experienced engineers

**DriveSense AI solves this by analyzing input derivatives rather than outputs.**
""")

st.markdown("---")

st.subheader("Core Innovation: Gradient-Based Behavioral Classification")

st.markdown("""
<div class="technical-box">
<strong>Technical Foundation</strong><br><br>
Traditional telemetry analysis examines speed traces and time deltas. DriveSense AI instead analyzes 
<span class="code-inline">steering_angle</span>, <span class="code-inline">pbrake_f</span>, and <span class="code-inline">ath</span> (throttle) 
first and second derivatives to classify the <strong>cause</strong> of performance variations.
<br><br>
<strong>Key Insight:</strong> Driver mistakes produce high steering jerk (second derivative) due to sudden corrections, 
while intentional technique variations show smooth gradient profiles even when the racing line differs. Similarly, 
throttle application patterns reveal driver confidence and corner exit optimization.
</div>
""", unsafe_allow_html=True)

st.markdown("### Classification Taxonomy")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔴 Driver Mistakes")
    st.markdown("""
    **Detection Method:**
    - Steering jerk > 2× baseline
    - Peak gradient > 1.5× reference
    - Asymmetric correction patterns
    
    **Use Cases:**
    - Real-time coaching feedback
    - Lap invalidation (qualifying)
    - Driver development tracking
    
    **Technical Details:**
    - Savitzky-Golay smoothing (window=5)
    - Second derivative threshold: `d²θ/ds²`
    - Confidence scoring via ratio metrics
    """)

with col2:
    st.markdown("#### 🟡 Racing Line Differences")
    st.markdown("""
    **Detection Method:**
    - Different peak gradients
    - Similar variance (controlled)
    - Smooth profile throughout
    
    **Use Cases:**
    - A/B testing racing lines
    - Track evolution analysis
    - Setup-induced line changes
    
    **Technical Details:**
    - Gradient consistency check: `σ(dθ/ds)`
    - Profile matching via cross-correlation
    - Geometric deviation quantification
    """)

with col3:
    st.markdown("#### 🟢 Brake/Throttle Technique")
    st.markdown("""
    **Detection Method:**
    - Brake pressure gradient analysis
    - Throttle application timing
    - Release/application modulation
    
    **Use Cases:**
    - Brake bias optimization
    - Throttle confidence assessment
    - Tire management strategy
    
    **Technical Details:**
    - Pressure derivative: `dp/ds`
    - Throttle derivative: `dath/ds`
    - Modulation frequency analysis
    """)

st.markdown("---")

st.subheader("Analysis Modes")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="technical-box">
    <h4>Single Lap Comparison</h4>
    <strong>Purpose:</strong> Corner-by-corner analysis of two laps<br><br>
    
    <strong>Methodology:</strong><br>
    1. Extract corner telemetry windows (apex_dist ± 100m)<br>
    2. Calculate input derivatives via Savitzky-Golay filter<br>
    3. Classify behavioral patterns per corner<br>
    4. Generate actionable recommendations<br>
    5. Compare sector times and top speeds<br><br>
    
    <strong>Output:</strong> Classification, confidence score, evidence, coaching, sector deltas<br><br>
    
    <strong>Best For:</strong> Post-session debriefs, qualifying analysis, setup validation
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="technical-box">
    <h4>Multi-Lap Consistency</h4>
    <strong>Purpose:</strong> Identify consistency patterns across stint<br><br>
    
    <strong>Methodology:</strong><br>
    1. Calculate steering smoothness metrics per lap<br>
    2. Compute coefficient of variation: <span class="code-inline">CV = σ/μ × 100</span><br>
    3. Trend analysis (improving/stable/declining)<br>
    4. Outlier detection via 2σ threshold<br>
    5. Sector-level consistency tracking (S1, S2, S3)<br><br>
    
    <strong>Output:</strong> Consistency scores, trend analysis, problematic corners, sector performance<br><br>
    
    <strong>Best For:</strong> Race simulation, driver development, tire degradation analysis
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.subheader("Live Session Monitoring")

st.markdown("""
<div class="technical-box">
<strong>Real-Time Analysis Pipeline</strong><br><br>

<strong>Architecture:</strong>
<ol>
<li><strong>File Watcher:</strong> Monitors incoming telemetry CSV files (watchdog library)</li>
<li><strong>Baseline Establishment:</strong> First lap becomes reference for all comparisons</li>
<li><strong>Per-Lap Processing:</strong> Gradient analysis at each corner</li>
<li><strong>Rolling Consistency:</strong> Updates after 3+ laps using running statistics</li>
<li><strong>Alert System:</strong> Flags repeated mistakes or declining performance</li>
<li><strong>Flag Filtering:</strong> Automatically excludes yellow flag laps from analysis</li>
<li><strong>Sector Tracking:</strong> Real-time S1/S2/S3 performance vs reference</li>
</ol>

<strong>Demo Mode:</strong> Simulates race session by dropping lap files at configurable intervals<br>
<strong>Live Mode:</strong> Watches directory for incoming telemetry from data acquisition systems<br><br>

<strong>Use Cases:</strong>
- Practice session coaching (real-time feedback)
- Race engineering support (pit strategy)
- Driver training systems (immediate correction)
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader("Dataset Specifications")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **GR Cup Series Telemetry:**
    - 2 tracks: Barber, Indianapolis
    - File sizes: 1.5-3GB per track
    - Parameters: speed, throttle, brake (F/R), steering angle, GPS, accelerations
    - Format: Long-format CSV (telemetry_name/telemetry_value pairs)
    - Sampling rate: ~100Hz (varies by parameter)
    
    **Endurance Timing Data:**
    - Sector times (S1, S2, S3) per lap
    - Top speed tracking
    - Flag conditions (Green, Yellow, Finish)
    - Clean lap identification
    """)

with col2:
    st.markdown("""
    **Data Preprocessing:**
    - Pivot to wide format for efficient processing
    - Duplicate lap deduplication (keep latest timestamp)
    - Distance calculation fallbacks when unavailable
    - Corner extraction via GPS + steering analysis
    - Smart lap selection based on data quality
    - Clean lap filtering via flag conditions
    - Sector time validation and outlier detection
    """)

st.markdown("---")

st.subheader("Technical Implementation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Stack:**
    - Python 3.10+
    - Streamlit (dashboard framework)
    - pandas (data manipulation)
    - scipy (signal processing - Savitzky-Golay)
    - NumPy (numerical computation)
    
    **Key Algorithms:**
    - `scipy.signal.savgol_filter` for derivative smoothing
    - Gradient-based classification thresholds
    - Rolling statistics for consistency tracking
    """)

with col2:
    st.markdown("""
    **Performance:**
    - Single lap analysis: < 2s
    - Multi-lap (15 laps): < 5s
    - Live processing latency: < 1s per lap
    - Memory efficient: processes 3GB files in chunks
    
    **Scalability:**
    - Modular corner configurations per track
    - Extensible classification system
    - Parallel processing ready (future enhancement)
    """)

if 'telemetry_path' not in st.session_state:
    st.session_state.telemetry_path = None
if 'lap_times_path' not in st.session_state:
    st.session_state.lap_times_path = None
if 'track_name' not in st.session_state:
    st.session_state.track_name = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'vehicle1_id' not in st.session_state:
    st.session_state.vehicle1_id = None
if 'vehicle2_id' not in st.session_state:
    st.session_state.vehicle2_id = None
if 'lap1_num' not in st.session_state:
    st.session_state.lap1_num = None
if 'lap2_num' not in st.session_state:
    st.session_state.lap2_num = None

st.sidebar.header("Navigation")
st.sidebar.markdown("""
**Get Started:**
1. Select Data → Choose track and laps
2. Analysis Results → View classifications
3. Live Session → Real-time monitoring (demo/live)

**Documentation:**
- Single lap: Corner-by-corner behavioral analysis
- Multi-lap: Consistency tracking across stints
- Live: Real-time coaching and alerts
""")

st.sidebar.markdown("---")

st.sidebar.markdown("""
**Technical Contact:**
For dataset access, algorithm details, or collaboration inquiries, 
see project documentation.
""")

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
    
    st.success("All data cleared! Please refresh the page.")
    st.rerun()
