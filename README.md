# DriveSense AI

**Gradient-Based Behavioral Classification for Racing Telemetry**

DriveSense AI solves the attribution problem in motorsport telemetry analysis: distinguishing between driver mistakes, intentional technique variations, and different racing lines using first and second derivative analysis of driver inputs.

**Hackathon Category:** Driver Training/Insights  
**Platform:** Python 3.10+ / Local Deployment  
**Dataset:** Toyota GR Cup Series Telemetry (Barber Motorsports Park, Indianapolis Motor Speedway)

---

## Core Innovation

Traditional telemetry systems show **WHERE** time is lost. DriveSense AI reveals **WHY** by analyzing steering angle, brake pressure, and throttle input derivatives rather than speed traces.

**Key Technical Insight:**
- Driver mistakes produce high steering jerk (second derivative) due to sudden corrections
- Intentional technique variations show smooth gradient profiles despite different racing lines
- Classification thresholds: steering jerk > 2× baseline AND peak gradient > 1.5× reference = mistake (with confidence scoring)

**Signal Processing:**
- Savitzky-Golay filtering for noise reduction
- First and second derivative calculation
- Threshold-based classification with quantified confidence
- Real-time processing capability (<1s per lap)

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- 4GB RAM minimum
- Git

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/[your-username]/drivesense-ai.git
cd drivesense-ai
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify data directory structure:**
```
drivesense-ai/
├── processed_data/
│   ├── barber/
│   │   ├── metadata.json
│   │   ├── [lap files]
│   └── indianapolis/
│       ├── metadata.json
│       ├── [lap files]
```

4. **Launch the application:**
```bash
streamlit run Home.py
```

The application will open in your default browser at `http://localhost:8501`

---

## Usage Guide

### Analysis Modes

#### 1. **Single Lap Comparison**
Compare two laps with corner-by-corner gradient analysis:
- Navigate to **Select Data** page
- Choose analysis mode: "Single Lap Comparison"
- Select track, race, vehicles, and laps
- Click **Run Analysis**
- View detailed classification results in **Analysis Results**
- Explore per-corner visualizations in **Corner Details**

#### 2. **Multi-Lap Consistency**
Track consistency patterns across stints:
- Navigate to **Select Data** page
- Choose analysis mode: "Multi-Lap Consistency"
- Select track, race, vehicle, and lap range
- Click **Run Multi-Lap Analysis**
- View consistency scores, trends, and problematic corners

#### 3. **Live Session Demo**
Real-time lap-by-lap analysis with automatic file monitoring:
- Navigate to **Live Session Demo** page
- Configure session (track, race, vehicle, lap range)
- Click **Start Session**
- Laps process automatically via file watcher
- View real-time mistake detection and consistency tracking
- Click **Stop Session** for comprehensive summary

**Note:** Live session uses Python's `watchdog` library for automatic file monitoring. Each new lap file triggers immediate gradient analysis against the established baseline.

---

## Dataset Information

**Source:** Toyota GR Cup Series Telemetry  
**Tracks:** Barber Motorsports Park, Indianapolis Motor Speedway  
**File Format:** CSV with ~100Hz sampling rate  
**File Sizes:** 1.5-3GB per track (raw), processed to individual lap files

**Parameters Available:**
- `steering_angle`: Steering wheel angle (degrees)
- `pbrake_f`: Front brake pressure (bar)
- `pbrake_r`: Rear brake pressure (bar)
- `ath`: Throttle position (%)
- `speed`: Vehicle speed (km/h)
- `lapdist_dls`: Distance along lap (meters)
- GPS coordinates, 3-axis accelerations

**Preprocessing:**
Raw telemetry is preprocessed into individual lap files with distance validation and duplicate removal. Metadata tracks available laps per vehicle/race combination.

---

## Technical Architecture

### Core Modules

**`gradient_analysis.py`**
- Input derivative calculation via Savitzky-Golay filtering
- Behavioral classification (mistakes, line differences, brake technique)
- Confidence scoring and evidence generation
- Recommendation generation with priority levels

**`live_analysis.py`**
- Real-time session management
- Baseline establishment and comparison logic
- Consistency score calculation (coefficient of variation)
- Alert generation for repeated mistakes
- Session summary with comprehensive metrics

**`steering_track_comparator.py`**
- Corner data extraction (apex ± 100m windows)
- Track configuration management
- Per-corner telemetry analysis

**`time_delta_calculator.py`**
- Lap time calculation from telemetry timestamps
- Corner-level time delta calculation
- Distance-based time interpolation

**`track_configs.py`**
- Corner definitions with apex distances
- Track sector boundaries
- Corner type classification (slow/medium/fast)

**`visualizations.py` / `corner_visualizations.py`**
- Steering/brake/throttle overlay plots
- Per-corner telemetry visualization
- Classification summary charts

**`multilap_consistency.py`**
- Multi-lap consistency analysis
- Trend detection (improving/deteriorating/stable)
- Outlier lap identification
- Corner-by-corner consistency scoring

**`lap_file_watcher.py` / `race_simulator.py`**
- Automatic file monitoring via `watchdog`
- Lap file detection and processing
- Session simulation for demonstrations

### Classification Taxonomy

1. **Driver Mistakes** (High Priority)
   - Detection: Steering jerk > 2× baseline + peak gradient > 1.5× reference
   - Evidence: Steering correction magnitude, rate-of-change comparison
   - Recommendation: Focus on consistency, replicate reference lap approach

2. **Racing Line Differences** (Medium Priority)
   - Detection: Different peak gradients with similar variance
   - Evidence: Gradient profile comparison, controlled inputs
   - Recommendation: Evaluate line efficiency, consider reverting if slower

3. **Brake Technique Variations** (Medium Priority)
   - Detection: Brake pressure gradient differences > 10 bar/m
   - Evidence: Application sharpness comparison
   - Recommendation: Smoother brake release for better tire grip

4. **Driver Style Variations** (Low Priority)
   - Detection: Smooth vs. aggressive input patterns
   - Evidence: Input modulation frequency
   - Recommendation: Optimize style for specific corner types

---

## System Requirements

**Minimum:**
- Python 3.10+
- 4GB RAM
- 2GB disk space (with sample data)
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Recommended:**
- Python 3.11+
- 8GB RAM
- 5GB disk space (for additional tracks)
- Multi-core processor for faster analysis

---

## Key Dependencies

- `streamlit==1.28.0` - Web application framework
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.23.0` - Numerical computation
- `scipy>=1.9.0` - Signal processing (Savitzky-Golay filtering)
- `matplotlib>=3.6.0` - Visualization
- `watchdog>=3.0.0` - File system monitoring (live session)

See `requirements.txt` for complete dependency list.

---

## Project Structure
```
drivesense-ai/
├── Home.py                          # Main entry point
├── pages/
│   ├── 0_Live_Session_Demo.py       # Live analysis with file watcher
│   ├── 1_Select_Data.py             # Data selection interface
│   ├── 2_Analysis_Results.py        # Results display
│   └── 3_Corner_Details.py          # Per-corner visualization
├── gradient_analysis.py             # Core classification engine
├── live_analysis.py                 # Session management
├── steering_track_comparator.py     # Corner extraction
├── time_delta_calculator.py         # Lap time calculation
├── track_configs.py                 # Track definitions
├── visualizations.py                # Chart generation
├── corner_visualizations.py         # Corner detail plots
├── multilap_consistency.py          # Consistency analysis
├── lap_file_watcher.py              # File monitoring
├── race_simulator.py                # Demo session simulation
├── aggregate_analysis.py            # Lap-level metrics
├── endurance_data_loader.py         # Endurance data integration
├── lap_time_loader.py               # Lap time management
├── processed_data/                  # Preprocessed telemetry
│   ├── barber/
│   └── indianapolis/
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Video Demonstration

[Link to 3-minute demo video showing live session analysis with automatic file watcher]

The video demonstrates:
- Real-time lap processing with automatic file monitoring
- Mistake detection with confidence scoring (Turn 3: 87% confidence)
- Line difference classification (Turn 7: intentional variation)
- Consistency tracking activation after 3+ laps
- Session summary with comprehensive metrics

---

## Use Cases

**Practice Session Coaching:**
Real-time feedback on mistakes and consistency trends for immediate driver improvement.

**Race Engineering Support:**
Live analysis during sessions to inform pit strategy and setup decisions.

**Driver Development:**
Multi-lap consistency tracking to measure skill progression and identify training focus areas.

**Post-Session Debrief:**
Detailed corner-by-corner analysis with specific, evidence-based recommendations.

**Setup Validation:**
Compare lap performance before/after setup changes with behavioral attribution.

---

## Open Source Components

This project uses the following open-source libraries:
- **Streamlit** (Apache 2.0): Web application framework
- **pandas** (BSD 3-Clause): Data manipulation
- **NumPy** (BSD 3-Clause): Numerical computation
- **SciPy** (BSD 3-Clause): Signal processing
- **Matplotlib** (PSF): Visualization
- **watchdog** (Apache 2.0): File system monitoring

All components are used in compliance with their respective licenses.

---

## Technical Validation

**Classification Accuracy:**
- Manual validation against expert driver analysis
- Confidence thresholds tuned to minimize false positives
- Evidence-based recommendations with quantified metrics

**Performance:**
- Single lap analysis: <2 seconds
- Multi-lap (15 laps): <5 seconds  
- Live processing latency: <1 second per lap
- Memory efficient: processes 3GB files in chunks

**Scalability:**
- Modular corner configurations per track
- Extensible classification system
- Parallel processing ready (future enhancement)

---

## Future Enhancements

- **Additional Tracks:** Extend to full GR Cup Series calendar
- **Machine Learning:** Train classifiers on labeled mistake dataset
- **Predictive Analysis:** Forecast consistency degradation
- **Multi-Vehicle Comparison:** Fleet-wide performance benchmarking
- **API Integration:** Direct data acquisition system connection


**Note:** This application is designed for local deployment to support automatic file monitoring capabilities. The live session feature uses Python's `watchdog` library to monitor incoming telemetry files, enabling real-time analysis for pit-side deployment scenarios.

- Requires high-quality distance data for gradient analysis
- Corner apex distances must be manually configured per track
- Sampling rate variations can affect derivative calculations
- Limited to tracks with defined corner configurations
- Best suited for circuit racing
- Classification thresholds may need tuning for different vehicle classes

