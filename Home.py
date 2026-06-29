import streamlit as st

st.set_page_config(
    page_title="Home | Project Overview",
    page_icon="🛰️",
    layout="wide")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.page-header {
    background: linear-gradient(135deg, #0c1445, #1a237e, #134e4a);
    border-radius: 10px;
    padding: 20px 20px;
    margin-bottom: 22px;
    color: white;}
.page-header h1 { font-size: 2.1rem; font-weight: 700; margin: 0 0 6px 0; }
.page-header .subtitle { color: #90caf9; margin: 0 0 16px 0; font-size: 1rem; }

.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 32px 0 14px 0;}

.objective-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 22px 24px;
    color: white;
    height: 100%;}
.objective-card .obj-tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 10px;}
.objective-card h3 { font-size: 1.15rem; font-weight: 700; margin: 0 0 8px 0; }
.objective-card p { font-size: 0.88rem; color: #94a3b8; line-height: 1.55; margin: 0; }

.pipeline-row { display: flex; align-items: stretch; gap: 6px; }
.pipeline-step {
    flex: 1;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 14px;
    text-align: center;
    color: white;}
.pipeline-step .step-icon { font-size: 1.6rem; margin-bottom: 6px; }
.pipeline-step .step-title { font-size: 0.82rem; font-weight: 700; margin-bottom: 4px; }
.pipeline-step .step-sub { font-size: 0.72rem; color: #64748b; line-height: 1.4; }
.pipeline-arrow { display: flex; align-items: center; color: #475569; font-size: 1.2rem; }

.source-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 18px;
    color: white;
    height: 100%;}
.source-card .src-icon { font-size: 1.4rem; margin-bottom: 6px; }
.source-card .src-title { font-size: 0.92rem; font-weight: 700; margin-bottom: 4px; }
.source-card .src-sub { font-size: 0.78rem; color: #94a3b8; line-height: 1.5; }

</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-header">
  <h1>🛰️ Surface AQI &amp; HCHO Hotspot Monitor</h1>
  <p class="subtitle">Satellite-based air quality intelligence over Maharashtra, India</p>
</div>
""", unsafe_allow_html=True)

# Information
st.markdown("""
Air pollution is one of India's most pressing public health challenges, and ground-based monitoring
covers only a small fraction of the country's landmass — leaving most of the population without
localized air quality information. This project closes that gap using freely available satellite
observations, turning raw remote-sensing data into spatially continuous, district-level air quality
intelligence that anyone can read at a glance.""")


# Objectives
st.markdown('<div class="section-title">🎯 Project Objectives</div>', unsafe_allow_html=True)

o1, o2 = st.columns(2)
with o1:
    st.markdown("""
    <div class="objective-card">
      <span class="obj-tag" style="background:rgba(59,130,246,0.15);color:#60a5fa;">Objective 1</span>
      <h3>🌫️ Surface AQI Estimation</h3>
      <p>
        Combine multi-pollutant retrievals from Sentinel-5P TROPOMI (NO₂, CO, SO₂, O₃), aerosol optical
        depth, and ERA5 reanalysis meteorology to model ground-level Air Quality Index — validated
        against CPCB station data — across every district, every month.
      </p>
    </div>
    """, unsafe_allow_html=True)
with o2:
    st.markdown("""
    <div class="objective-card">
      <span class="obj-tag" style="background:rgba(239,68,68,0.15);color:#f87171;">Objective 2</span>
      <h3>🔥 HCHO Hotspot Identification</h3>
      <p>
        Map spatio-temporal formaldehyde (HCHO) concentrations — a proxy for VOC emissions and biomass
        burning — to flag pollution source regions and crop-residue burning seasons before they peak.
      </p>
    </div>
    """, unsafe_allow_html=True)

# Pipeline 
st.markdown('<div class="section-title">⚙️ How It Works</div>', unsafe_allow_html=True)

steps = [
    ("📥", "Data Sources", "CPCB · TROPOMI · ERA5 · MODIS/FIRMS"),
    ("🧹", "Processing", "Clean → QA filter → regrid → collocate"),
    ("🧠", "Models", "Random Forest AQI · Z-score/K-Means hotspots"),
    ("✅", "Validation", "RMSE · R² · MAE vs. CPCB ground truth"),
    ("📊", "Visualization", "Interactive maps, trends & this dashboard"),]
pipe_cols = st.columns([3,1,3,1,3,1,3,1,3])
for i, (icon, title, sub) in enumerate(steps):
    with pipe_cols[i*2]:
        st.markdown(f"""
        <div class="pipeline-step">
          <div class="step-icon">{icon}</div>
          <div class="step-title">{title}</div>
          <div class="step-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)
    if i < len(steps) - 1:
        with pipe_cols[i*2 + 1]:
            st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)

# Data Sources
st.markdown('<div class="section-title">🛰️ Data Sources</div>', unsafe_allow_html=True)

sources = [
    ("🏭", "CPCB Ground Stations", "PM2.5, PM10, NO₂, SO₂, CO, O₃ — hourly/daily, station-level"),
    ("🛰️", "Sentinel-5P TROPOMI", "NO₂, SO₂, CO, O₃, HCHO columns — ~3.5 km daily"),
    ("🌬️", "ERA5 Reanalysis", "Wind, temperature, humidity, boundary layer height"),
    ("🔥", "MODIS / VIIRS (FIRMS)", "Active fire detections & Fire Radiative Power"),
    ("☀️", "INSAT-3D AOD", "Aerosol Optical Depth, supplements PM2.5 estimation"),]
src_cols = st.columns(5)
for col, (icon, title, sub) in zip(src_cols, sources):
    with col:
        st.markdown(f"""
        <div class="source-card">
          <div class="src-icon">{icon}</div>
          <div class="src-title">{title}</div>
          <div class="src-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# Navigate the Dashboard 
st.markdown('<div class="section-title">🧭 Explore the Dashboard</div>', unsafe_allow_html=True)

nav_cols = st.columns(2)
nav_items = [
    ("🌫️ AQI Analysis", "District-level AQI, pollutant drivers & trends", "pages/AQI_Map_fixed.py"),
    ("🧪 HCHO Hotspots", "Formaldehyde concentration & fire correlation", "pages/HCHO_Hotspots.py"),]
for col, (label, desc, target) in zip(nav_cols, nav_items):
    with col:
        try:
            st.page_link(target, label=label, use_container_width=True)
        except Exception:
            st.markdown(f"**{label}**")
        st.caption(desc)

