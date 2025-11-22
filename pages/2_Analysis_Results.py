import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from steering_track_comparator import compare_laps_by_track, extract_corner_data
from track_configs import TRACK_CONFIGS
from lap_time_loader import get_lap_data, get_sector_times

st.set_page_config(page_title="Analysis Results", page_icon="📊", layout="wide")

st.title("Analysis Results")

analysis_mode = st.session_state.get('analysis_mode', 'Single Lap Comparison')

if analysis_mode == 'Multi-Lap Consistency':
    if not all([
        st.session_state.get('track_name'),
        st.session_state.get('vehicle1_id'),
        st.session_state.get('multilap_files'),
        st.session_state.get('multilap_numbers')
    ]):
        st.warning("Please select data in the Select Data page")
        st.stop()
    
    if st.session_state.get('trigger_multilap_analysis') and not st.session_state.get('multilap_analysis_complete'):
        st.session_state.trigger_multilap_analysis = False
        
        st.subheader(f"Multi-Lap Consistency Analysis: Vehicle {st.session_state.vehicle1_id}")
        st.info(f"Analyzing {len(st.session_state.multilap_numbers)} laps (Laps {min(st.session_state.multilap_numbers)} - {max(st.session_state.multilap_numbers)})")
        
        with st.spinner("Analyzing consistency across laps..."):
            try:
                from multilap_consistency import analyze_multilap_consistency, generate_consistency_report
                
                track_config = TRACK_CONFIGS.get(st.session_state.track_name)
                
                lap_times_dict = st.session_state.get('lap_times_dict')
                
                consistency_results = analyze_multilap_consistency(
                    st.session_state.multilap_files,
                    st.session_state.multilap_numbers,
                    st.session_state.track_name,
                    track_config,
                    vehicle_id=st.session_state.vehicle1_id,
                    lap_times_dict=lap_times_dict
                )
                
                if consistency_results:
                    report = generate_consistency_report(
                        consistency_results,
                        st.session_state.vehicle1_id
                    )
                    
                    st.session_state.consistency_results = consistency_results
                    st.session_state.consistency_report = report
                    st.session_state.multilap_analysis_complete = True
                else:
                    st.error("Insufficient data for consistency analysis")
                    st.stop()
                    
            except ImportError as e:
                st.error(f"Multi-lap consistency module not found: {e}")
                st.error("Make sure multilap_consistency.py is in the project directory")
                st.stop()
            except Exception as e:
                st.error(f"Error in consistency analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.stop()
    
    if st.session_state.get('multilap_analysis_complete'):
        st.success("Multi-Lap Consistency Analysis Complete!")
        
        consistency_results = st.session_state.consistency_results
        
        st.markdown("---")
        
        if consistency_results.get('overall_consistency'):
            st.header("Overall Lap Time Consistency")
            
            oc = consistency_results['overall_consistency']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Consistency Score", f"{oc['consistency_score']:.1f}/100")
            with col2:
                st.metric("Average Lap Time", f"{oc['mean_time']:.3f}s")
            with col3:
                st.metric("Standard Deviation", f"{oc['std_dev']:.3f}s")
            with col4:
                cv_pct = oc['coefficient_of_variation']
                st.metric("Variation", f"{cv_pct:.2f}%")
            
            if oc['consistency_score'] >= 85:
                st.success("**Assessment:** EXCELLENT - Very consistent lap times")
            elif oc['consistency_score'] >= 70:
                st.info("**Assessment:** GOOD - Reasonably consistent performance")
            elif oc['consistency_score'] >= 50:
                st.warning("**Assessment:** MODERATE - Some lap-to-lap variation")
            else:
                st.error("**Assessment:** INCONSISTENT - High lap-to-lap variation")
        
        st.markdown("---")
        
        if consistency_results.get('sector_consistency'):
            st.header("Sector-Level Consistency")
            
            for sector_name, sector_data in consistency_results['sector_consistency'].items():
                with st.expander(sector_name, expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Consistency Score", f"{sector_data['consistency_score']:.1f}/100")
                    with col2:
                        st.metric("Average Time", f"{sector_data['mean_time']:.3f}s")
                    with col3:
                        st.metric("Std Dev", f"{sector_data['std_dev']:.3f}s")
                    
                    if sector_name in consistency_results.get('sector_trend_analysis', {}):
                        trend = consistency_results['sector_trend_analysis'][sector_name]
                        st.caption(f"Trend: {trend['trend'].upper()} ({trend['percentage_change']:+.2f}%)")
            
            st.markdown("---")
        
        if consistency_results.get('lap_times'):
            st.header("Lap Times")
            
            lap_time_data = []
            for lt in consistency_results['lap_times']:
                if lt['time']:
                    lap_time_data.append({
                        'Lap': lt['lap'],
                        'Time (s)': f"{lt['time']:.3f}"
                    })
            
            if lap_time_data:
                df = pd.DataFrame(lap_time_data)
                st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        if consistency_results.get('trend_analysis'):
            st.header("Performance Trend")
            
            ta = consistency_results['trend_analysis']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Trend", f"{ta['trend'].upper()}")
            with col2:
                st.metric("Early Stint Avg", f"{ta['early_avg']:.3f}s")
            with col3:
                st.metric("Late Stint Avg", f"{ta['late_avg']:.3f}s")
            
            change = ta['percentage_change']
            if ta['trend'] == 'improving':
                st.success(f"Performance improved by {change:.2f}% over the stint")
            elif ta['trend'] == 'deteriorating':
                st.warning(f"Performance declined by {change:.2f}% over the stint")
            else:
                st.info("Performance remained stable throughout the stint")
        
        st.markdown("---")
        
        if consistency_results.get('outlier_laps'):
            st.header("Outlier Laps")
            
            st.info("Laps that are significantly faster or slower than average (>2 standard deviations)")
            
            for outlier in consistency_results['outlier_laps']:
                if outlier['type'] == 'slower':
                    st.error(f"**Lap {outlier['lap']}:** {outlier['time']:.3f}s (SLOWER by {outlier['deviation']:.3f}s)")
                else:
                    st.success(f"**Lap {outlier['lap']}:** {outlier['time']:.3f}s (FASTER by {outlier['deviation']:.3f}s)")
        
        st.markdown("---")
        
        if consistency_results.get('corner_consistency'):
            st.header("Corner-by-Corner Consistency")
            
            corner_scores = []
            for corner_name, analysis in consistency_results['corner_consistency'].items():
                if analysis.get('overall_consistency_score'):
                    corner_scores.append({
                        'Corner': corner_name,
                        'Consistency Score': f"{analysis['overall_consistency_score']:.1f}/100",
                        'Score_Value': analysis['overall_consistency_score'],
                        'best_lap': analysis.get('best_lap'),
                        'worst_lap': analysis.get('worst_lap'),
                        'apex_dist_m': analysis.get('apex_dist_m')
                    })
            
            if corner_scores:
                corner_scores.sort(key=lambda x: x['Score_Value'])
                
                st.subheader("Most Inconsistent Corners (Need Attention)")
                
                for i, corner in enumerate(corner_scores[:5], 1):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.warning(f"{i}. **{corner['Corner']}**: {corner['Consistency Score']}")
                        if corner['best_lap'] and corner['worst_lap']:
                            st.caption(f"Best: Lap {corner['best_lap']['lap']} | Worst: Lap {corner['worst_lap']['lap']}")
                    
                    with col2:
                        if corner['best_lap'] and corner['worst_lap'] and corner['apex_dist_m']:
                            button_key = f"analyze_{corner['Corner'].replace(' ', '_').replace('/', '_')}"
                            if st.button("Diagnose", key=button_key):
                                st.session_state[f'drill_down_{button_key}'] = {
                                    'corner_name': corner['Corner'],
                                    'best_lap_file': corner['best_lap']['file'],
                                    'worst_lap_file': corner['worst_lap']['file'],
                                    'best_lap_num': corner['best_lap']['lap'],
                                    'worst_lap_num': corner['worst_lap']['lap'],
                                    'apex_dist_m': corner['apex_dist_m']
                                }
                
                for i, corner in enumerate(corner_scores[:5], 1):
                    button_key = f"analyze_{corner['Corner'].replace(' ', '_').replace('/', '_')}"
                    drill_down = st.session_state.get(f'drill_down_{button_key}')
                    
                    if drill_down:
                        st.markdown("---")
                        st.subheader(f"Diagnosis: {drill_down['corner_name']}")
                        
                        with st.spinner(f"Analyzing best vs worst lap at {drill_down['corner_name']}..."):
                            try:
                                from gradient_analysis import classify_driver_behavior_by_gradient
                                
                                tel_best = pd.read_csv(drill_down['best_lap_file'])
                                tel_worst = pd.read_csv(drill_down['worst_lap_file'])
                                
                                corner_data_best = extract_corner_data(tel_best, drill_down['apex_dist_m'])
                                corner_data_worst = extract_corner_data(tel_worst, drill_down['apex_dist_m'])
                                
                                if corner_data_best is not None and corner_data_worst is not None:
                                    lap_times_dict = st.session_state.get('lap_times_dict')
                                    lap_data_best = get_lap_data(lap_times_dict, st.session_state.vehicle1_id, drill_down['best_lap_num']) if lap_times_dict else None
                                    lap_data_worst = get_lap_data(lap_times_dict, st.session_state.vehicle1_id, drill_down['worst_lap_num']) if lap_times_dict else None
                                    
                                    top_speed_best = lap_data_best.get('top_speed') if lap_data_best else None
                                    top_speed_worst = lap_data_worst.get('top_speed') if lap_data_worst else None
                                    
                                    classification = classify_driver_behavior_by_gradient(
                                        corner_data_best,
                                        corner_data_worst,
                                        f"Lap {drill_down['best_lap_num']} (Best)",
                                        f"Lap {drill_down['worst_lap_num']} (Worst)",
                                        top_speed_a=top_speed_best,
                                        top_speed_b=top_speed_worst
                                    )
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Best Lap", drill_down['best_lap_num'])
                                    with col2:
                                        st.metric("Worst Lap", drill_down['worst_lap_num'])
                                    with col3:
                                        st.metric("Confidence", f"{classification['confidence']*100:.1f}%")
                                    
                                    st.info(f"**Classification:** {classification['type'].replace('_', ' ').title()}")
                                    st.markdown(f"**Explanation:** {classification['description']}")
                                    
                                    if classification.get('evidence'):
                                        st.markdown("**Evidence:**")
                                        for evidence in classification['evidence']:
                                            st.markdown(f"- {evidence}")
                                    
                                    if classification['type'] == 'driver_mistake':
                                        st.error(f"**Diagnosis:** Inconsistency caused by driver mistakes on some laps")
                                        st.markdown("**Action:** Focus on consistency at this corner - the clean line is there, just need to execute it every time")
                                    elif classification['type'] == 'different_line':
                                        st.warning(f"**Diagnosis:** Experimenting with different racing lines")
                                        st.markdown(f"**Action:** Pick one line and commit to it for better consistency")
                                    elif classification['type'] == 'driver_style':
                                        st.info(f"**Diagnosis:** Different driving styles between laps (aggressive vs smooth)")
                                        st.markdown("**Action:** Decide on optimal style for this corner and maintain it")
                                    else:
                                        st.success(f"**Diagnosis:** Setup or conditions affecting performance")
                                    
                                    if st.button(f"Close Analysis", key=f"close_{button_key}"):
                                        del st.session_state[f'drill_down_{button_key}']
                                        st.rerun()
                                else:
                                    st.error("Could not extract corner data for analysis")
                            except Exception as e:
                                st.error(f"Error in drill-down analysis: {e}")
                                import traceback
                                st.code(traceback.format_exc())
                
                st.markdown("---")
                
                st.subheader("Most Consistent Corners")
                best_corners = corner_scores[-5:]
                best_corners.reverse()
                for i, corner in enumerate(best_corners, 1):
                    st.success(f"{i}. **{corner['Corner']}**: {corner['Consistency Score']}")
                
                st.markdown("---")
                
                df_corners = pd.DataFrame([{
                    'Corner': c['Corner'],
                    'Consistency Score': c['Consistency Score']
                } for c in corner_scores])
                
                with st.expander("All Corner Consistency Scores"):
                    st.dataframe(df_corners, use_container_width=True)
        
        st.markdown("---")
        st.header("Full Consistency Report")
        
        with st.expander("Detailed Analysis Report", expanded=False):
            st.text(st.session_state.consistency_report)
    else:
        st.info("Select data and click 'Run Multi-Lap Analysis' in the Select Data page")

else:
    if not all([
        st.session_state.get('track_name'),
        st.session_state.get('vehicle1_id'),
        st.session_state.get('vehicle2_id'),
        st.session_state.get('lap1_num'),
        st.session_state.get('lap2_num'),
        st.session_state.get('lap1_file'),
        st.session_state.get('lap2_file')
    ]):
        st.warning("Please select data in the Select Data page")
        st.stop()

    if st.session_state.get('trigger_analysis') and not st.session_state.get('analysis_complete'):
        st.session_state.trigger_analysis = False
        
        with st.spinner("Loading telemetry data..."):
            try:
                tel1 = pd.read_csv(st.session_state.lap1_file)
                tel2 = pd.read_csv(st.session_state.lap2_file)
                
                race1 = st.session_state.get('race1', st.session_state.get('race', 'R1'))
                race2 = st.session_state.get('race2', st.session_state.get('race', 'R2'))
                
                st.success(f"Loaded Vehicle {st.session_state.vehicle1_id} ({race1}) Lap {st.session_state.lap1_num}: {len(tel1)} data points")
                st.success(f"Loaded Vehicle {st.session_state.vehicle2_id} ({race2}) Lap {st.session_state.lap2_num}: {len(tel2)} data points")
                
                lap_times_dict_r1 = st.session_state.get('lap_times_dict_r1')
                lap_times_dict_r2 = st.session_state.get('lap_times_dict_r2')
                
                lap_data_1 = None
                lap_data_2 = None
                if lap_times_dict_r1:
                    lap_data_1 = get_lap_data(lap_times_dict_r1, st.session_state.vehicle1_id, st.session_state.lap1_num)
                if lap_times_dict_r2:
                    lap_data_2 = get_lap_data(lap_times_dict_r2, st.session_state.vehicle2_id, st.session_state.lap2_num)
                
                st.session_state.lap_data_1 = lap_data_1
                st.session_state.lap_data_2 = lap_data_2
                
                distance_cols = ['lapdist_dls', 'trigger_lapdist_dls', 'Lap', 'distance']
                distance_available = False
                for col in distance_cols:
                    if col in tel1.columns and col in tel2.columns:
                        if tel1[col].notna().sum() > 10 and tel2[col].notna().sum() > 10:
                            distance_available = True
                            st.info(f"Distance data available: Using column '{col}'")
                            break
                
                st.session_state.distance_available = distance_available
                
                if not distance_available:
                    st.warning("Distance data unavailable - using aggregate lap-level analysis")
                
                st.session_state.tel1 = tel1
                st.session_state.tel2 = tel2
                
                from time_delta_calculator import calculate_lap_time
                
                lap_time_1 = None
                lap_time_2 = None
                
                if lap_data_1:
                    lap_time_1 = lap_data_1.get('lap_time')
                if lap_data_2:
                    lap_time_2 = lap_data_2.get('lap_time')
                
                if lap_time_1 is None:
                    lap_time_1 = calculate_lap_time(tel1)
                if lap_time_2 is None:
                    lap_time_2 = calculate_lap_time(tel2)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if lap_time_1 is not None:
                        st.metric("Vehicle 1 Lap Time", f"{lap_time_1:.3f}s")
                    else:
                        st.metric("Vehicle 1 Lap Time", "N/A")
                
                with col2:
                    if lap_time_2 is not None:
                        st.metric("Vehicle 2 Lap Time", f"{lap_time_2:.3f}s")
                    else:
                        st.metric("Vehicle 2 Lap Time", "N/A")
                
                with col3:
                    if lap_time_1 is not None and lap_time_2 is not None:
                        time_delta = lap_time_1 - lap_time_2
                        st.metric("Time Delta", f"{time_delta:+.3f}s", delta=f"{time_delta:+.3f}s", delta_color="inverse")
                    else:
                        st.metric("Time Delta", "N/A")
                
                with col4:
                    speed_delta = None
                    avg_speed_1 = None
                    avg_speed_2 = None
                    
                    if lap_data_1 and lap_data_1.get('kph'):
                        avg_speed_1 = lap_data_1['kph']
                    elif 'speed' in tel1.columns:
                        speed_data_1 = tel1['speed'].dropna()
                        if len(speed_data_1) > 0:
                            avg_speed_1 = speed_data_1.mean()
                    
                    if lap_data_2 and lap_data_2.get('kph'):
                        avg_speed_2 = lap_data_2['kph']
                    elif 'speed' in tel2.columns:
                        speed_data_2 = tel2['speed'].dropna()
                        if len(speed_data_2) > 0:
                            avg_speed_2 = speed_data_2.mean()
                    
                    if avg_speed_1 is not None and avg_speed_2 is not None:
                        speed_delta = avg_speed_1 - avg_speed_2
                        st.metric("Avg Speed Delta", f"{speed_delta:+.1f} km/h", delta=f"{speed_delta:+.1f} km/h", delta_color="normal")
                    else:
                        st.metric("Avg Speed Delta", "N/A")
                
                if lap_data_1 and lap_data_1.get('s1'):
                    st.markdown("---")
                    st.subheader("Sector Times")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Sector 1**")
                        st.metric("Vehicle 1", f"{lap_data_1['s1']:.3f}s")
                        if lap_data_2 and lap_data_2.get('s1'):
                            st.metric("Vehicle 2", f"{lap_data_2['s1']:.3f}s")
                            delta = lap_data_1['s1'] - lap_data_2['s1']
                            st.metric("Delta", f"{delta:+.3f}s", delta=f"{delta:+.3f}s", delta_color="inverse")
                    
                    with col2:
                        st.markdown("**Sector 2**")
                        st.metric("Vehicle 1", f"{lap_data_1['s2']:.3f}s")
                        if lap_data_2 and lap_data_2.get('s2'):
                            st.metric("Vehicle 2", f"{lap_data_2['s2']:.3f}s")
                            delta = lap_data_1['s2'] - lap_data_2['s2']
                            st.metric("Delta", f"{delta:+.3f}s", delta=f"{delta:+.3f}s", delta_color="inverse")
                    
                    with col3:
                        st.markdown("**Sector 3**")
                        st.metric("Vehicle 1", f"{lap_data_1['s3']:.3f}s")
                        if lap_data_2 and lap_data_2.get('s3'):
                            st.metric("Vehicle 2", f"{lap_data_2['s3']:.3f}s")
                            delta = lap_data_1['s3'] - lap_data_2['s3']
                            st.metric("Delta", f"{delta:+.3f}s", delta=f"{delta:+.3f}s", delta_color="inverse")
                
                if (lap_data_1 and lap_data_1.get('top_speed')) or (lap_data_2 and lap_data_2.get('top_speed')):
                    st.markdown("---")
                    st.subheader("Top Speed")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if lap_data_1 and lap_data_1.get('top_speed'):
                            st.metric("Vehicle 1", f"{lap_data_1['top_speed']:.1f} km/h")
                        else:
                            st.metric("Vehicle 1", "N/A")
                    
                    with col2:
                        if lap_data_2 and lap_data_2.get('top_speed'):
                            st.metric("Vehicle 2", f"{lap_data_2['top_speed']:.1f} km/h")
                        else:
                            st.metric("Vehicle 2", "N/A")
                    
                    with col3:
                        if lap_data_1 and lap_data_2 and lap_data_1.get('top_speed') and lap_data_2.get('top_speed'):
                            speed_delta = lap_data_1['top_speed'] - lap_data_2['top_speed']
                            st.metric("Delta", f"{speed_delta:+.1f} km/h", delta=f"{speed_delta:+.1f} km/h", delta_color="normal")
                        else:
                            st.metric("Delta", "N/A")
                
                if (lap_data_1 and lap_data_1.get('flag')) or (lap_data_2 and lap_data_2.get('flag')):
                    from lap_time_loader import get_flag_emoji
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if lap_data_1 and lap_data_1.get('flag'):
                            flag_emoji = get_flag_emoji(lap_data_1['flag'])
                            st.info(f"{flag_emoji} Vehicle 1: {lap_data_1['flag']}")
                    
                    with col2:
                        if lap_data_2 and lap_data_2.get('flag'):
                            flag_emoji = get_flag_emoji(lap_data_2['flag'])
                            st.info(f"{flag_emoji} Vehicle 2: {lap_data_2['flag']}")
                
                st.session_state.lap_time_1 = lap_time_1 if lap_time_1 is not None else 0.0
                st.session_state.lap_time_2 = lap_time_2 if lap_time_2 is not None else 0.0
            except Exception as e:
                st.error(f"Error loading data: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.stop()
        
        if st.session_state.get('distance_available'):
            with st.spinner("Running corner-by-corner analysis..."):
                try:
                    comparison_results = compare_laps_by_track(
                        st.session_state.tel1,
                        st.session_state.tel2,
                        st.session_state.track_name
                    )
                    
                    st.session_state.comparison_results = comparison_results
                    
                    if comparison_results['summary']['corners_analyzed'] == 0:
                        st.error("No corners could be analyzed!")
                        st.stop()
                        
                except Exception as e:
                    st.error(f"Error in comparison: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.stop()
        else:
            st.session_state.comparison_results = None
        
        if st.session_state.get('distance_available'):
            try:
                with st.spinner("Classifying behaviors with gradient analysis..."):
                    from gradient_analysis import classify_driver_behavior_by_gradient, generate_gradient_based_recommendations
                    
                    track_config = TRACK_CONFIGS[st.session_state.track_name]
                    if isinstance(track_config, dict) and 'corners' in track_config:
                        corners = track_config['corners']
                    else:
                        corners = track_config
                    
                    detailed_results = {
                        'report': '',
                        'summary': {
                            'total_time_delta': st.session_state.get('lap_time_1', 0.0) - st.session_state.get('lap_time_2', 0.0),
                            'corners_analyzed': 0
                        },
                        'corners': {}
                    }
                    
                    report_lines = []
                    report_lines.append("GRADIENT-BASED BEHAVIORAL ANALYSIS")
                    report_lines.append("=" * 80)
                    report_lines.append(f"Vehicle {st.session_state.vehicle1_id} (Reference) vs Vehicle {st.session_state.vehicle2_id} (Comparison)")
                    report_lines.append(f"Overall Lap Time Delta: {detailed_results['summary']['total_time_delta']:+.3f}s")
                    report_lines.append("")
                    
                    lap_data_1 = st.session_state.get('lap_data_1')
                    lap_data_2 = st.session_state.get('lap_data_2')
                    top_speed_1 = lap_data_1.get('top_speed') if lap_data_1 else None
                    top_speed_2 = lap_data_2.get('top_speed') if lap_data_2 else None
                    
                    for corner_def in corners:
                        corner_data_a = extract_corner_data(st.session_state.tel1, corner_def['apex_dist_m'])
                        corner_data_b = extract_corner_data(st.session_state.tel2, corner_def['apex_dist_m'])
                        
                        if corner_data_a is None or corner_data_b is None:
                            continue
                        
                        classification = classify_driver_behavior_by_gradient(
                            corner_data_a, 
                            corner_data_b,
                            st.session_state.vehicle1_id,
                            st.session_state.vehicle2_id,
                            top_speed_a=top_speed_1,
                            top_speed_b=top_speed_2
                        )
                        
                        context = {
                            'vehicle_a_id': st.session_state.vehicle1_id,
                            'vehicle_b_id': st.session_state.vehicle2_id
                        }
                        recommendations = generate_gradient_based_recommendations(classification, context)
                        
                        report_lines.append(f"{corner_def['name']} ({corner_def['type']})")
                        
                        if recommendations and recommendations[0].get('vehicle'):
                            vehicle_str = f"Vehicle {recommendations[0]['vehicle']}"
                        else:
                            vehicle_str = "Both vehicles"
                        report_lines.append(f"  Vehicle: {vehicle_str}")
                        report_lines.append(f"  Classification: {classification['type'].replace('_', ' ').title()}")
                        report_lines.append(f"  Confidence: {classification['confidence']*100:.1f}%")
                        report_lines.append(f"  {classification['description']}")
                        
                        if classification.get('evidence'):
                            report_lines.append(f"  Evidence:")
                            for evidence in classification['evidence']:
                                report_lines.append(f"    - {evidence}")
                        
                        if recommendations:
                            report_lines.append(f"  Recommendations:")
                            for rec in recommendations:
                                report_lines.append(f"    Vehicle {rec['vehicle']}: {rec['recommendation']}")
                        
                        report_lines.append("")
                        
                        priority_map = {'high': 'HIGH', 'medium': 'MEDIUM', 'low': 'LOW'}
                        priority = priority_map.get(recommendations[0]['priority'], 'LOW') if recommendations else 'LOW'
                        
                        detailed_results['corners'][corner_def['name']] = {
                            'classification': classification['type'],
                            'confidence': classification['confidence'] * 100,
                            'vehicle': recommendations[0]['vehicle'] if recommendations else None,
                            'recommendation': {
                                'action': recommendations[0]['recommendation'] if recommendations else 'Continue current approach',
                                'explanation': classification['description'],
                                'priority': priority
                            },
                            'evidence': classification.get('evidence', {})
                        }
                        
                        detailed_results['summary']['corners_analyzed'] += 1
                    
                    detailed_results['report'] = '\n'.join(report_lines)
                    
                    st.session_state.detailed_results = detailed_results
                    st.session_state.has_gradient_analysis = True
            except ImportError as e:
                st.warning(f"Gradient analysis modules not available: {e}")
                st.session_state.has_gradient_analysis = False
            except Exception as e:
                st.warning(f"Gradient analysis error: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.has_gradient_analysis = False
        else:
            try:
                with st.spinner("Running aggregate lap-level analysis..."):
                    from aggregate_analysis import analyze_lap_comparison_aggregate, generate_aggregate_report
                    
                    aggregate_results = analyze_lap_comparison_aggregate(
                        st.session_state.tel1,
                        st.session_state.tel2,
                        st.session_state.vehicle1_id,
                        st.session_state.vehicle2_id
                    )
                    
                    aggregate_report = generate_aggregate_report(aggregate_results)
                    
                    st.session_state.aggregate_results = aggregate_results
                    st.session_state.aggregate_report = aggregate_report
                    st.session_state.has_aggregate_analysis = True
                    st.session_state.has_gradient_analysis = False
            except ImportError as e:
                st.warning(f"Aggregate analysis modules not available: {e}")
                st.session_state.has_aggregate_analysis = False
            except Exception as e:
                st.warning(f"Aggregate analysis error: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.has_aggregate_analysis = False
        
        if st.session_state.get('distance_available'):
            try:
                with st.spinner("Generating visualizations..."):
                    import visualizations
                    import corner_visualizations
                    
                    viz_path = Path("visualizations")
                    viz_path.mkdir(exist_ok=True)
                    corner_path = viz_path / "corners"
                    corner_path.mkdir(exist_ok=True)
                    
                    for old_viz in corner_path.glob("*.png"):
                        old_viz.unlink()
                    
                    if st.session_state.get('has_gradient_analysis'):
                        visualizations.create_summary_visualizations(
                            st.session_state.comparison_results,
                            st.session_state.detailed_results,
                            str(viz_path)
                        )
                    
                    track_config = TRACK_CONFIGS[st.session_state.track_name]
                    if isinstance(track_config, dict) and 'corners' in track_config:
                        corners = track_config['corners']
                    else:
                        corners = track_config
                    
                    detailed_report = {
                        'track': st.session_state.track_name,
                        'corners': []
                    }
                    
                    for corner_def in corners:
                        corner_data_a = extract_corner_data(st.session_state.tel1, corner_def['apex_dist_m'])
                        corner_data_b = extract_corner_data(st.session_state.tel2, corner_def['apex_dist_m'])
                        
                        if corner_data_a is not None and corner_data_b is not None:
                            detailed_report['corners'].append({
                                'corner_name': corner_def['name'],
                                'data_a': corner_data_a,
                                'data_b': corner_data_b,
                                'time_delta': None
                            })
                    
                    lap_info_a = {
                        'vehicle_id': st.session_state.vehicle1_id,
                        'lap': st.session_state.lap1_num,
                        'time': st.session_state.lap_time_1
                    }
                    lap_info_b = {
                        'vehicle_id': st.session_state.vehicle2_id,
                        'lap': st.session_state.lap2_num,
                        'time': st.session_state.lap_time_2
                    }
                    
                    corner_visualizations.generate_corner_visualizations(
                        detailed_report,
                        lap_info_a,
                        lap_info_b,
                        str(corner_path)
                    )
                    
                    st.session_state.viz_path = viz_path
                    st.session_state.has_visualizations = True
            except ImportError as e:
                st.warning(f"Visualization modules not available: {e}")
                st.session_state.has_visualizations = False
            except Exception as e:
                st.warning(f"Visualization error: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.has_visualizations = False
        
        st.session_state.analysis_complete = True
    
    if st.session_state.get('analysis_complete'):
        st.success("Analysis Complete!")
        
        st.markdown("---")
        
        if st.session_state.get('has_aggregate_analysis') and st.session_state.get('aggregate_results'):
            st.header("Aggregate Lap-Level Analysis")
            
            st.info("Distance data unavailable - showing lap-level performance metrics")
            
            with st.expander("Full Aggregate Report", expanded=True):
                st.text(st.session_state.aggregate_report)
            
            aggregate = st.session_state.aggregate_results
            
            st.markdown("---")
            st.subheader("Performance Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### Vehicle {aggregate['vehicle_a']['id']}")
                if aggregate['vehicle_a']['smoothness']:
                    st.metric("Steering Smoothness", f"{aggregate['vehicle_a']['smoothness']['smoothness_score']:.1f}/100")
                if aggregate['vehicle_a']['brake']:
                    st.metric("Brake Consistency", f"{aggregate['vehicle_a']['brake']['consistency_score']:.1f}/100")
                if aggregate['vehicle_a']['throttle']:
                    st.metric("Throttle Confidence", f"{aggregate['vehicle_a']['throttle']['confidence_score']:.1f}/100")
                st.markdown(f"**Style:** {aggregate['vehicle_a']['style'].replace('_', ' ').title()}")
            
            with col2:
                st.markdown(f"### Vehicle {aggregate['vehicle_b']['id']}")
                if aggregate['vehicle_b']['smoothness']:
                    st.metric("Steering Smoothness", f"{aggregate['vehicle_b']['smoothness']['smoothness_score']:.1f}/100")
                if aggregate['vehicle_b']['brake']:
                    st.metric("Brake Consistency", f"{aggregate['vehicle_b']['brake']['consistency_score']:.1f}/100")
                if aggregate['vehicle_b']['throttle']:
                    st.metric("Throttle Confidence", f"{aggregate['vehicle_b']['throttle']['confidence_score']:.1f}/100")
                st.markdown(f"**Style:** {aggregate['vehicle_b']['style'].replace('_', ' ').title()}")
            
            st.markdown("---")
            st.subheader("Recommendations")
            
            for vehicle_key in ['vehicle_a', 'vehicle_b']:
                vehicle = aggregate[vehicle_key]
                st.markdown(f"### Vehicle {vehicle['id']}")
                
                for rec in vehicle['recommendations']:
                    with st.expander(f"{rec['category']} - {rec['priority']} Priority"):
                        st.markdown(f"**Issue:** {rec['issue']}")
                        st.markdown(f"**Recommendation:** {rec['recommendation']}")
                        st.markdown(f"**Evidence:** {rec['evidence']}")
            
        elif st.session_state.get('has_gradient_analysis') and st.session_state.get('detailed_results'):
            st.header("Detailed Report")
            
            with st.expander("Full Analysis Report", expanded=True):
                report_text = st.session_state.detailed_results['report']
                st.text(report_text)
        else:
            st.header("Basic Comparison Results")
            
            comparison = st.session_state.comparison_results
            
            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Corners", comparison['summary']['total_corners'])
            with col2:
                st.metric("Corners Analyzed", comparison['summary']['corners_analyzed'])
            with col3:
                st.metric("Corners with Speed", comparison['summary']['corners_with_speed'])
            
            st.subheader("Corner-by-Corner Comparison")
            
            corner_data = []
            for corner in comparison['corners']:
                if corner.get('data_available'):
                    corner_data.append({
                        'Corner': corner['name'],
                        'Type': corner['type'],
                        'Steering Delta': f"{corner.get('steering_delta', 0):.2f}" if 'steering_delta' in corner else 'N/A',
                        'Brake Delta': f"{corner.get('brake_delta', 0):.2f}" if 'brake_delta' in corner else 'N/A',
                        'Speed Delta': f"{corner.get('speed_delta', 0):.2f}" if 'speed_delta' in corner else 'N/A',
                    })
            
            if corner_data:
                df = pd.DataFrame(corner_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No corner data available for comparison")
        
        if st.session_state.get('has_gradient_analysis') and st.session_state.get('detailed_results'):
            st.markdown("---")
            st.header("Corner-by-Corner Summary")
            
            detailed_results = st.session_state.detailed_results
            
            summary_data = []
            for corner_name, analysis in detailed_results['corners'].items():
                summary_data.append({
                    'Corner': corner_name,
                    'Classification': analysis['classification'],
                    'Confidence (%)': f"{analysis['confidence']:.1f}",
                    'Priority': analysis['recommendation']['priority']
                })
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                
                def highlight_priority(row):
                    if row['Priority'] == 'HIGH':
                        return ['background-color: #ffcccc'] * len(row)
                    elif row['Priority'] == 'MEDIUM':
                        return ['background-color: #fff4cc'] * len(row)
                    else:
                        return ['background-color: #ccffcc'] * len(row)
                
                styled_df = df.style.apply(highlight_priority, axis=1)
                st.dataframe(styled_df, use_container_width=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Total Time Delta",
                    f"{detailed_results['summary']['total_time_delta']:.3f}s"
                )
            
            with col2:
                st.metric(
                    "Corners Analyzed",
                    detailed_results['summary']['corners_analyzed']
                )
            
            if st.session_state.get('has_visualizations'):
                st.markdown("---")
                st.info("Navigate to Corner Details to see per-corner visualizations")
    else:
        st.info("Select data and click 'Run Analysis' in the Select Data page")

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