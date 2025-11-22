# DriveSense AI

Gradient-based behavioral classification system for motorsport telemetry analysis. Distinguishes between driver mistakes, racing line differences, and technique variations by analyzing derivatives of steering, brake, and throttle inputs rather than traditional speed-based metrics.

## Core Innovation

Traditional telemetry analysis identifies **WHERE** time is lost through speed traces and time deltas. DriveSense AI explains **WHY** time is lost by classifying the behavioral cause of performance differences.

### Technical Foundation

Analyzes first and second derivatives of driver inputs (`steering_angle`, `pbrake_f`, `ath`) to classify behavioral patterns:

- **Driver Mistakes**: High steering jerk (d²θ/ds²) from sudden corrections, asymmetric patterns
- **Racing Line Differences**: Different gradient profiles with consistent variance (controlled execution)
- **Brake/Throttle Technique**: Pressure gradient analysis (dp/ds, dath/ds) reveals modulation differences

Uses Savitzky-Golay filtering (window=5, polyorder=2) for derivative smoothing and ratio-based confidence scoring.

## Features

### Single Lap Comparison
Corner-by-corner analysis of two laps with:
- Gradient-based behavioral classification per corner
- Confidence scoring with evidence-based recommendations
- Sector time deltas and top speed comparison
- Corner telemetry overlays (steering, brake, throttle)

### Multi-Lap Consistency
Stint-level performance analysis with:
- Lap time consistency scoring (coefficient of variation)
- Corner-by-corner consistency metrics
- Performance trend detection (improving/stable/declining)
- Outlier lap identification (>2σ threshold)
- Sector-level consistency tracking

### Live Session Monitoring
Real-time analysis pipeline with:
- File watcher for incoming telemetry (watchdog library)
- Per-lap gradient analysis vs. baseline
- Rolling consistency metrics (updates after 3+ laps)
- Alert system for repeated mistakes or declining performance
- Flag condition filtering (excludes yellow flag laps)
- Demo mode for session replay

## Installation

### Requirements
- Python 3.10+
- 8GB+ RAM (processes large telemetry files)

### Setup
```bash
git clone https://github.com/yourusername/drivesense-ai.git
cd drivesense-ai
pip install -r requirements.txt
```

### Dependencies
```
streamlit==1.28.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
scipy>=1.9.0
watchdog>=3.0.0
```

## Data Requirements

### Telemetry Format
Long-format CSV with columns:
- `lapdist_dls` or `trigger_lapdist_dls`: Distance along lap (meters)
- `steering_angle`: Steering input (degrees)
- `pbrake_f`: Front brake pressure (bar)
- `ath`: Throttle position (%)
- `speed`: Vehicle speed (km/h)
- `timestamp`: Sample timestamp

Sampling rate: ~100Hz (varies by parameter)

### Endurance Timing Format
Semicolon-delimited CSV with columns:
- `NUMBER`: Vehicle number
- `LAP_NUMBER`: Lap number
- `LAP_TIME`: Lap time (mm:ss.sss)
- `TOP_SPEED`: Top speed (km/h)
- `S1_SECONDS`, `S2_SECONDS`, `S3_SECONDS`: Sector times
- `FLAG_AT_FL`: Flag condition (GF, FCY, FF, SC, RED)

### Preprocessing
Telemetry files must be preprocessed into per-lap CSVs:
```bash
python preprocess_data.py --track barber --input raw_telemetry.csv --output processed_data/
```

Expected directory structure:
```
processed_data/
├── barber/
│   ├── metadata.json
│   ├── lap_001.csv
│   ├── lap_002.csv
│   └── AnalysisEnduranceWithSections_Race_1.CSV
└── indianapolis/
    ├── metadata.json
    └── ...
```

## Usage

### Launch Dashboard
```bash
streamlit run Home.py
```

Access at `http://localhost:8501`

### Single Lap Analysis
1. Navigate to **Select Data**
2. Choose track, vehicles, and laps
3. Click **Run Analysis**
4. View results in **Analysis Results**
5. Examine per-corner telemetry in **Corner Details**

### Multi-Lap Consistency
1. Navigate to **Select Data**
2. Select **Multi-Lap Consistency** mode
3. Choose vehicle and lap range
4. Click **Run Multi-Lap Analysis**
5. Review consistency scores and trend analysis

### Live Session Demo
1. Navigate to **Live Session Demo**
2. Configure track, vehicle, lap range, interval
3. Click **Start Session**
4. Monitor real-time analysis as laps arrive
5. View final summary report after session completion

## Classification Taxonomy

### Driver Mistakes
**Detection**: Steering jerk >2× baseline, peak gradient >1.5× reference, asymmetric correction patterns

**Evidence**: d²θ/ds² ratio, peak steering input comparison, top speed correlation

**Confidence**: Ratio-based (spikiness_a / (spikiness_b + 1)) / 10, capped at 0.95

**Use Cases**: Real-time coaching, lap invalidation, driver development tracking

### Racing Line Differences
**Detection**: Different peak gradients (>5°/m delta), similar variance (<2°/m delta), smooth profiles

**Evidence**: Gradient consistency check (σ(dθ/ds)), profile matching, geometric deviation

**Confidence**: abs(max_grad_a - max_grad_b) / 20, capped at 0.85

**Use Cases**: A/B testing lines, track evolution analysis, setup-induced changes

### Brake/Throttle Technique
**Detection**: Pressure gradient differences (>10 bar/m delta)

**Evidence**: dp/ds comparison, modulation frequency, application smoothness

**Confidence**: abs(max_brake_grad_a - max_brake_grad_b) / 50, capped at 0.80

**Use Cases**: Brake bias optimization, throttle confidence assessment, tire management

## Technical Implementation

### Core Algorithms
- `scipy.signal.savgol_filter`: Derivative smoothing (window=5, polyorder=2)
- Gradient-based classification with threshold detection
- Rolling statistics for consistency tracking
- Coefficient of variation (CV = σ/μ × 100) for consistency scoring

### Performance
- Single lap analysis: <2s
- Multi-lap (15 laps): <5s
- Live processing latency: <1s per lap
- Memory efficient: processes 3GB files in chunks

### Architecture
```
Home.py                      # Main dashboard entry
pages/
├── 0_Live_Session_Demo.py   # Real-time analysis interface
├── 1_Select_Data.py         # Data selection and configuration
├── 2_Analysis_Results.py    # Results visualization
└── 3_Corner_Details.py      # Per-corner telemetry overlays

Core Modules:
├── gradient_analysis.py          # Behavioral classification engine
├── aggregate_analysis.py         # Lap-level metrics (no distance data)
├── multilap_consistency.py       # Stint-level analysis
├── live_analysis.py              # Real-time analyzer
├── lap_time_loader.py            # Timing data integration
├── endurance_data_loader.py      # Sector times, flags, top speed
├── steering_track_comparator.py  # Corner extraction
├── time_delta_calculator.py      # Lap time calculation
├── track_configs.py              # Track corner definitions
├── visualizations.py             # Summary charts
├── corner_visualizations.py      # Per-corner overlays
├── lap_file_watcher.py           # File monitoring (watchdog)
└── race_simulator.py             # Demo session simulator
```

## Supported Tracks

### Active Tracks (Distance Data Available)
- **Barber Motorsports Park**: 10 corners, 3 sectors
- **Indianapolis Motor Speedway**: 14 corners, 3 sectors

Track configurations in `track_configs.py` include corner apex distances, types (slow/medium/fast), and sector boundaries. Additional track configurations (COTA, Road America, Sebring, Sonoma, VIR) are included and can be activated when corresponding telemetry data is available.

## Output Examples

### Gradient Analysis Report
```
GRADIENT-BASED BEHAVIORAL ANALYSIS
================================================================================
Vehicle 321 (Reference) vs Vehicle 322 (Comparison)
Overall Lap Time Delta: +0.247s

Turn 1 (medium)
  Vehicle: Vehicle 322
  Classification: Driver Mistake
  Confidence: 87.3%
  Vehicle 322 made a sudden steering correction, likely due to missed braking 
  point or compromised corner entry
  Evidence:
    - Steering correction: 12.45 rate-of-change vs 4.23 on reference (2x higher)
    - Peak steering input: 8.67°/m vs 4.12°/m (1.5x higher)
    - Indicates: Late braking or missed turn-in point requiring correction
  Recommendations:
    Vehicle 322: Focus on smoother initial turn-in to avoid mid-corner 
    corrections. Practice consistency in entry speed and brake point.
```

### Consistency Report
```
MULTI-LAP CONSISTENCY ANALYSIS
================================================================================
Vehicle: 321
Laps Analyzed: 15 (Laps 3 - 17)

OVERALL LAP TIME CONSISTENCY
--------------------------------------------------------------------------------
  Average Lap Time: 88.423s
  Standard Deviation: 0.187s
  Consistency Score: 89.4/100

  Assessment: EXCELLENT - Very consistent lap times

PERFORMANCE TREND
--------------------------------------------------------------------------------
  Trend: IMPROVING
  Early Stint Average: 88.621s
  Late Stint Average: 88.234s
  Change: -0.44%

CORNER-BY-CORNER CONSISTENCY
--------------------------------------------------------------------------------
  Most Inconsistent Corners (need attention):
    Turn 3: 62.4/100
    Turn 7: 68.1/100
    Turn 10: 71.3/100

  Most Consistent Corners:
    Turn 5: 94.2/100
    Turn 8: 91.7/100
    Turn 2: 90.1/100
```

## Dataset Specifications

### GR Cup Series Telemetry
- 2 tracks with complete data: Barber, Indianapolis
- File sizes: 1.5-3GB per track
- Parameters: speed, throttle, brake (F/R), steering angle, GPS, accelerations
- Format: Long-format CSV (telemetry_name/telemetry_value pairs)
- Sampling rate: ~100Hz (varies by parameter)

### Endurance Timing Data
- Sector times (S1, S2, S3) per lap
- Top speed tracking
- Flag conditions (Green, Yellow, Finish, Safety Car, Red)
- Clean lap identification via flag filtering

### Data Preprocessing
- Pivot to wide format for efficient processing
- Duplicate lap deduplication (keep latest timestamp)
- Distance calculation fallbacks when unavailable
- Corner extraction via GPS + steering analysis
- Smart lap selection based on data quality
- Clean lap filtering via flag conditions
- Sector time validation and outlier detection

## Configuration

### Track Configuration
Edit `track_configs.py` to add new tracks:

```python
'track_name': {
    'name': 'Track Display Name',
    'sectors': [
        {'name': 'Sector 1', 'end_distance': 1200},
        {'name': 'Sector 2', 'end_distance': 2400},
        {'name': 'Sector 3', 'end_distance': 3600}
    ],
    'corners': [
        {'name': 'Turn 1', 'apex_dist_m': 400, 'type': 'medium', 'sector': 1},
    ]
}
```

### Analysis Thresholds
Modify classification thresholds in `gradient_analysis.py`:

```python
# Driver mistake detection
spikiness_threshold = 2.0
gradient_threshold = 1.5

# Racing line detection
gradient_delta_threshold = 5
variance_threshold = 2

# Brake technique detection
brake_gradient_threshold = 10
```

## Project Structure

```
drivesense-ai/
├── Home.py
├── pages/
│   ├── 0_Live_Session_Demo.py
│   ├── 1_Select_Data.py
│   ├── 2_Analysis_Results.py
│   └── 3_Corner_Details.py
├── aggregate_analysis.py
├── corner_visualizations.py
├── endurance_data_loader.py
├── gradient_analysis.py
├── lap_file_watcher.py
├── lap_time_loader.py
├── live_analysis.py
├── multilap_consistency.py
├── race_simulator.py
├── steering_track_comparator.py
├── time_delta_calculator.py
├── track_configs.py
├── visualizations.py
├── requirements.txt
└── processed_data/
    ├── barber/
    │   ├── metadata.json
    │   ├── lap_001.csv
    │   └── AnalysisEnduranceWithSections_Race_1.CSV
    └── indianapolis/
        └── ...
```

## Methodology

### Gradient Calculation
```python
steering_smooth = savgol_filter(steering, window_length=5, polyorder=2)
steering_derivative = np.gradient(steering_smooth)
steering_jerk = np.gradient(steering_derivative)
```

### Classification Logic
```python
if jerk_a > jerk_b * 2 and peak_grad_a > peak_grad_b * 1.5:
    classification = 'driver_mistake'
    confidence = min((jerk_a / (jerk_b + 1)) / 10, 0.95)

elif abs(peak_grad_a - peak_grad_b) > 5 and abs(std_grad_a - std_grad_b) < 2:
    classification = 'different_line'
    confidence = min(abs(peak_grad_a - peak_grad_b) / 20, 0.85)

elif abs(brake_grad_a - brake_grad_b) > 10:
    classification = 'brake_technique'
    confidence = min(abs(brake_grad_a - brake_grad_b) / 50, 0.80)
```

### Consistency Scoring
```python
CV = (std_dev / mean) * 100
consistency_score = 100 / (1 + CV / 50)

early_avg = mean(laps[:n//3])
late_avg = mean(laps[-n//3:])

if late_avg < early_avg * 0.995:
    trend = 'improving'
elif late_avg > early_avg * 1.005:
    trend = 'deteriorating'
else:
    trend = 'stable'
```

## Development

### Adding New Tracks
1. Add track configuration to `track_configs.py`
2. Determine corner apex distances from track map or telemetry analysis
3. Define sector boundaries
4. Classify corner types based on typical speeds
5. Preprocess telemetry data into per-lap CSVs

### Extending Classification
Add new behavioral patterns in `gradient_analysis.py`:

```python
def classify_driver_behavior_by_gradient(corner_data_a, corner_data_b, ...):
    
    elif your_condition:
        classification = {
            'type': 'your_pattern',
            'description': 'Explanation',
            'confidence': calculate_confidence(),
            'evidence': ['Evidence point 1', 'Evidence point 2']
        }
    
    return classification
```

## Limitations

- Requires high-quality distance data for gradient analysis
- Corner apex distances must be manually configured per track
- Sampling rate variations can affect derivative calculations
- Limited to tracks with defined corner configurations
- Best suited for circuit racing
- Classification thresholds may need tuning for different vehicle classes

## Future Enhancements

- Automatic corner detection via GPS + steering pattern analysis
- Machine learning classification model trained on expert-labeled data
- Real-time streaming telemetry integration
- Tire temperature/pressure correlation with consistency scores
- Weather condition impact on performance deltas
- Driver fatigue detection via consistency degradation patterns
- Multi-vehicle race strategy optimization
- Predictive lap time modeling based on driving style

## License

MIT License

## Contact

For dataset access, algorithm details, or collaboration inquiries, open an issue on GitHub.
