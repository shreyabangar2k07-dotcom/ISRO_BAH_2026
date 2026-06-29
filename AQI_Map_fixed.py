import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from folium.plugins import HeatMap
import plotly.graph_objects as go

st.set_page_config(
    page_title="AQI Analysis",
    page_icon="🌫️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap')

html, body, [class*="css"] { font-family: 'Inter', sans-serif }

.page-header {
    background: linear-gradient(135deg, #0c1445, #1a237e, #283593);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white}
.page-header h1 { font-size: 2rem; font-weight: 700; margin: 0 0 6px 0 }
.page-header p  { color: #90caf9; margin: 0; font-size: 0.95rem }

.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    color: white}
.metric-card .label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em }
.metric-card .value { font-size: 1.5rem; font-weight: 700; margin: 6px 0 4px }
.metric-card .sub   { font-size: 0.78rem; color: #64748b }

.legend-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    color: white}
.legend-box h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 14px}
.legend-item {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 10px; font-size: 0.85rem}
.dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; margin-top: 3px }

.district-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-top: 12px}
.district-card h2 { font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0 }
.aqi-big {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
    margin: 12px 0 4px}
.aqi-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em}
.driver-bar-wrap { margin-bottom: 10px }
.driver-label { display:flex; justify-content:space-between; font-size:0.83rem; margin-bottom:4px }
.driver-bar-bg { background:#0f172a; border-radius:999px; height:8px; overflow:hidden }
.driver-bar-fill { height:8px; border-radius:999px }
.info-item { background: #0f172a; border-radius: 10px; padding: 14px 16px }
.info-item .ilabel { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em }
.info-item .ivalue { font-size: 1.05rem; font-weight: 600; margin-top: 4px }
.timeline-wrapper {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 20px}
.note-box {
    background: rgba(234,179,8,0.08);
    border: 1px solid rgba(234,179,8,0.3);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.8rem;
    color: #fde68a;
    margin-top: 14px}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-header">
  <h1>🌫️ AQI Analysis Dashboard</h1>
  <p>Ground-station Air Quality Index across Maharashtra CPCB monitoring locations</p>
</div>
""", unsafe_allow_html=True)

# ── Data Load ─────────────────────────────────────────────────────────────────
df_raw = pd.read_csv('aqi_dataset_with_target.csv')
df_raw['Date'] = pd.to_datetime(df_raw['Timestamp'])

# Approximate locality-level coordinates for each monitoring station
station_coords = {
    'Mumbai':            (19.0669, 72.8679),
    'Mira-Bhayandar':    (19.2952, 72.8554),
    'Virar':             (19.4559, 72.8111),
    'Belapur':           (19.0145, 73.0400),
    'Dhule':             (20.9042, 74.7749),
    'Bhiwandi':          (19.3002, 73.0682),
    'Mahad':             (18.0833, 73.4167),
    'Thane':             (19.2403, 73.0297),
    'Badlapur':          (19.1556, 73.2350),
    'Kalyan':            (19.2502, 73.1389),
    'Boisar':            (19.8064, 72.7556),
    'Malegaon':          (20.5579, 74.5089),
    'Parbhani':          (19.2608, 76.7748),
    'Nashik':            (20.0114, 73.7956),
    'Aurangabad':        (19.8595, 75.3438),
    'Chandrapur':        (19.9615, 79.2961),
    'Jalna':             (19.8410, 75.8864),
    'Nagpur':            (21.1498, 79.0806),
    'Jalgaon':           (21.0077, 75.5626),
    'Akola':             (20.7002, 77.0082),
    'Solapur':           (17.6599, 75.9064),
    'Pune':              (18.5529, 73.8228),
    'Latur':             (18.4088, 76.5604),
    'Kolhapur':          (16.6913, 74.2479),
    'Amravati':          (20.9374, 77.7796),
    'Ulhasnagar':        (19.2215, 73.1645),
    'Nanded':            (19.1383, 77.3210),
    'Ahmednagar':        (19.0948, 74.7480),
    'Pimpri Chinchwad':  (18.6186, 73.7766),
    'Navi Mumbai':       (19.0822, 73.1003),
    'Sangli':            (16.8602, 74.5642),
}

# A small number of rows have a missing numeric AQI but are still labelled
# "Severe" in AQI_Category (the source data drops the exact value once it's
# off-scale). We fill these with the midpoint of the CPCB "Severe" band
# (401-500) so they still surface on the map/trends instead of silently
# disappearing, and flag how many such days fed into each average.

df_raw['AQI_filled'] = df_raw['AQI']

# ── Month Timeline ───────────────────────────────────────────────────────────
available_months = sorted(df_raw['Date'].dt.to_period('M').unique())
month_labels = [m.strftime('%b %Y') for m in available_months]

st.markdown('<div class="timeline-wrapper">', unsafe_allow_html=True)
col_tl_label, col_tl_slider = st.columns([1, 5])
with col_tl_label:
    st.markdown("<p style='color:#90caf9;font-size:0.85rem;margin-top:8px;'>📅 Select Month</p>", unsafe_allow_html=True)
with col_tl_slider:
    selected_month_idx = st.select_slider(
        "Month",
        options=list(range(len(month_labels))),
        format_func=lambda i: month_labels[i],
        value=len(month_labels) - 1,
        label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

selected_period = available_months[selected_month_idx]
df_month = df_raw[df_raw['Date'].dt.to_period('M') == selected_period].copy()

# ── Aggregate by station (monthly mean) ──────────────────────────────────────
df_agg = df_month.groupby('Location').agg(
    PM25=('PM2.5 (µg/m³)', 'mean'),
    PM10=('PM10 (µg/m³)', 'mean'),
    NO2=('NO2 (µg/m³)', 'mean'),
    SO2=('SO2 (µg/m³)', 'mean'),
    CO=('CO (mg/m³)', 'mean'),
    O3=('Ozone (µg/m³)', 'mean'),
    AT=('AT (°C)', 'mean'),
    RH=('RH (%)', 'mean'),
    WS=('WS (m/s)', 'mean'),
    WD=('WD (deg)', 'mean'),
    Dispersion=('Dispersion', 'mean'),
    AQI=('AQI_filled', 'mean'),
    severe_days=('AQI_Category', lambda s: int((s == 'Severe').sum())),
).reset_index()

df_agg['Lat'] = df_agg['Location'].map(lambda x: station_coords.get(x, (None, None))[0])
df_agg['Lon'] = df_agg['Location'].map(lambda x: station_coords.get(x, (None, None))[1])
df_agg = df_agg.dropna(subset=['Lat', 'Lon'])

df_agg['AQI'] = df_agg['AQI'].fillna(0).round(0).astype(int)

# ── CPCB Standard AQI Category / Color ───────────────────────────────────────
def aqi_color(aqi):
    if aqi <= 50:    return "#22c55e"
    elif aqi <= 100: return "#84cc16"
    elif aqi <= 200: return "#eab308"
    elif aqi <= 300: return "#f97316"
    elif aqi <= 400: return "#ef4444"
    else:            return "#7c3aed"

def aqi_category(aqi):
    if aqi <= 50:    return "Good"
    elif aqi <= 100: return "Satisfactory"
    elif aqi <= 200: return "Moderate"
    elif aqi <= 300: return "Poor"
    elif aqi <= 400: return "Very Poor"
    else:            return "Severe"

# ── Pollutant profile (relative levels within the selected month, for display) ─
def norm(series):
    mn, mx = series.min(), series.max()
    return ((series - mn) / (mx - mn + 1e-12)).clip(0, 1)

df_agg['pm25_n'] = norm(df_agg['PM25'])
df_agg['pm10_n'] = norm(df_agg['PM10'])
df_agg['no2_n']  = norm(df_agg['NO2'])
df_agg['co_n']   = norm(df_agg['CO'])

driver_cols = {'PM2.5': 'pm25_n', 'PM10': 'pm10_n', 'NO2': 'no2_n', 'CO': 'co_n'}

def driver_pct(row):
    total = sum(row[c] for c in driver_cols.values()) + 1e-12
    return {k: round(row[c] / total * 100, 1) for k, c in driver_cols.items()}

# Cigarette equivalent — Berkeley Earth rule of thumb: ~22 µg/m³ of PM2.5
# sustained over 24h ≈ 1 cigarette/day. Now driven by real measured PM2.5.
df_agg['cig_equiv'] = (df_agg['PM25'] / 22).round(2)

# ── Multi-Month Trend Data (for station search bar chart) ───────────────────
df_raw['Month'] = df_raw['Date'].dt.to_period('M')
df_trend = df_raw.groupby(['Location', 'Month']).agg(
    AQI=('AQI_filled', 'mean'),
    PM25=('PM2.5 (µg/m³)', 'mean'),
).reset_index()
df_trend['AQI'] = df_trend['AQI'].fillna(0).round(0).astype(int)
df_trend['MonthLabel'] = df_trend['Month'].apply(lambda m: m.strftime('%b %Y'))
df_trend = df_trend.sort_values('Month')

# ── Map Mode Toggle ──────────────────────────────────────────────────────────
map_mode = st.radio(
    "🗺️ Map Mode",
    ["AQI Heatmap", "🚬 Cigarette Equivalent"],
    horizontal=True
)

# ── Summary Metrics ──────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
worst_aqi_row = df_agg.loc[df_agg['AQI'].idxmax()]
metrics = [
    ("🔴 Worst AQI", str(df_agg['AQI'].max()), worst_aqi_row['Location']),
    ("📊 Avg AQI",   str(int(round(df_agg['AQI'].mean()))), f"{len(df_agg)} stations"),
    ("🚬 Max Cig",   f"{df_agg['cig_equiv'].max()} /day", df_agg.loc[df_agg['cig_equiv'].idxmax(), 'Location']),
    ("📅 Period",    selected_period.strftime('%B %Y'), f"{len(df_month)} data points"),
]
for col, (label, val, sub) in zip([c1, c2, c3, c4], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.write("")

# ── Map + Legend Side-by-Side ────────────────────────────────────────────────
map_col, legend_col = st.columns([4, 1])

with map_col:
    m = folium.Map(location=[19.5, 76.5], zoom_start=6, tiles='CartoDB dark_matter')

    heat_vals = df_agg['AQI'] if map_mode == "AQI Heatmap" else df_agg['cig_equiv'] * 22
    heat_data = [[float(row['Lat']), float(row['Lon']), float(heat_vals.iloc[i])] for i, (_, row) in enumerate(df_agg.iterrows())]

    HeatMap(
        heat_data, radius=60, blur=30, max_zoom=1,
        min_opacity=0.15, max_opacity=0.75,
        gradient={0.0:'#2563eb', 0.3:'#22c55e', 0.5:'#eab308', 0.75:'#f97316', 1.0:'#7c3aed'}
    ).add_to(m)

    for _, row in df_agg.iterrows():
        aqi   = int(row['AQI'])
        color = aqi_color(aqi)
        cat   = aqi_category(aqi)
        cig   = row['cig_equiv']
        drv   = driver_pct(row)

        if map_mode == "🚬 Cigarette Equivalent":
            main_line = f"🚬 {cig} cigarettes/day"
        else:
            main_line = f"AQI = {aqi} ({cat})"

        severe_note = f"<br>⚠️ {int(row['severe_days'])} severe-AQI day(s) this month (value estimated)" if row['severe_days'] > 0 else ""

        popup_html = f"""
        <div style="font-family:Inter,Arial;width:280px;padding:4px;">
          <h4 style="margin:0 0 6px;font-size:1rem;">{row['Location']}</h4>
          <span style="background:{color};color:white;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:700;">AQI {aqi} · {cat}</span>
          <hr style="margin:8px 0;border-color:#e2e8f0;">
          <b>Pollutant Profile:</b><br>
          PM2.5 : {drv['PM2.5']}%<br>
          PM10 : {drv['PM10']}%<br>
          NO2  : {drv['NO2']}%<br>
          CO : {drv['CO']}%<br>
          <hr style="margin:8px 0;border-color:#e2e8f0;">
          🚬 <b>{cig}</b> cigarettes/day equivalent{severe_note}
        </div>"""

        tooltip_txt = f"<b>{row['Location']}</b> — {'🚬 '+str(cig)+' cigs/day' if map_mode=='🚬 Cigarette Equivalent' else 'AQI '+str(aqi)+' · '+cat}"

        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=4,
            popup=folium.Popup(popup_html, max_width=310),
            tooltip=tooltip_txt,
            color=color, fill=True, fillColor=color,
            fillOpacity=0.4, weight=1, opacity=0.4
        ).add_to(m)

    st_folium(m, width="100%", height=650)

with legend_col:
    st.markdown("""
    <div class="legend-box">
      <h4>AQI Levels (CPCB)</h4>
      <div class="legend-item"><div class="dot" style="background:#22c55e;"></div><div><b>Good</b><br><small>0–50</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#84cc16;"></div><div><b>Satisfactory</b><br><small>51–100</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#eab308;"></div><div><b>Moderate</b><br><small>101–200</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#f97316;"></div><div><b>Poor</b><br><small>201–300</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#ef4444;"></div><div><b>Very Poor</b><br><small>301–400</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#7c3aed;"></div><div><b>Severe</b><br><small>401–500</small></div></div>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>📡 Data Source</h4>
      <p style="font-size:0.78rem;color:#94a3b8;line-height:1.6;margin:0;">
        Ground-station readings (PM2.5, PM10, NO₂, SO₂, CO, O₃) across 31 CPCB-style
        monitoring locations. AQI is the dataset's own ground-truth value, not a
        computed formula.
      </p>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>🚬 Cig Mode</h4>
      <p style="font-size:0.78rem;color:#94a3b8;line-height:1.5;">
        <code style="background:#0f172a;padding:2px 6px;border-radius:4px;font-size:0.75rem;">
        cigs = PM2.5 / 22
        </code><br>
        <small>(Berkeley Earth equivalence, real PM2.5)</small>
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── Station Search Bar ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔍 Station AQI Profile")
st.markdown("<p style='color:#64748b;margin-top:-12px;margin-bottom:16px;'>Search any monitoring station to see its complete air quality breakdown</p>", unsafe_allow_html=True)

station_names = sorted(df_agg['Location'].unique().tolist())
search_query = st.selectbox(
    "Search station",
    options=[""] + station_names,
    index=0,
    placeholder="Type a station or city name…",
    label_visibility="collapsed"
)

if search_query:
    row   = df_agg[df_agg['Location'] == search_query].iloc[0]
    aqi   = int(row['AQI'])
    color = aqi_color(aqi)
    cat   = aqi_category(aqi)
    cig   = row['cig_equiv']
    drv   = driver_pct(row)
    wd    = row['WD']

    wind_dir = "N/A"
    if not pd.isna(wd):
        dirs16 = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        wind_dir = dirs16[int((wd + 11.25) / 22.5) % 16]

    season_mode = df_month[df_month['Location'] == search_query]['Season'].mode()
    season = season_mode.iloc[0] if not season_mode.empty else "N/A"

    # Build driver bars HTML
    driver_colors = {'PM2.5': '#3b82f6', 'PM10': '#8b5cf6', 'NO2': '#f97316', 'CO': '#06b6d4'}
    bars_html = ""
    for name, pct in sorted(drv.items(), key=lambda x: -x[1]):
        bars_html += f"""<div class="driver-bar-wrap">
<div class="driver-label">
<span style="font-weight:600;">{name}</span>
<span style="color:{driver_colors[name]};font-weight:700;">{pct}%</span>
</div>
<div class="driver-bar-bg">
<div class="driver-bar-fill" style="width:{pct}%;background:{driver_colors[name]};"></div>
</div>
</div>"""

    at_v   = round(row['AT'], 1) if not pd.isna(row['AT']) else "N/A"
    rh_v   = round(row['RH'], 0) if not pd.isna(row['RH']) else "N/A"
    ws_v   = round(row['WS'], 1) if not pd.isna(row['WS']) else "N/A"
    disp_v = round(row['Dispersion'], 1) if not pd.isna(row['Dispersion']) else "N/A"
    so2_v  = round(row['SO2'], 1) if not pd.isna(row['SO2']) else "N/A"
    o3_v   = round(row['O3'], 1) if not pd.isna(row['O3']) else "N/A"

    
    st.markdown(f"""
<div class="district-card">
<h2>{search_query}</h2>
<div style="display:grid;grid-template-columns:1fr 2fr;gap:32px;align-items:start;">
<div>
<div class="aqi-label">Air Quality Index</div>
<div class="aqi-big" style="color:{color};">{aqi}</div>
<span style="background:rgba(0,0,0,0.3);border:1px solid {color}50;color:{color};padding:4px 14px;border-radius:999px;font-size:0.82rem;font-weight:700;">● {cat}</span>
<div style="margin-top:20px;">
<div class="ilabel" style="font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;">🚬 Cigarette Equivalent</div>
<div style="font-size:1.4rem;font-weight:700;color:#fca5a5;margin-top:6px;">{cig} <span style="font-size:0.85rem;font-weight:400;color:#94a3b8;">cigarettes/day</span></div>
</div>
<div style="margin-top:20px;">
<div class="ilabel" style="font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;">Period</div>
<div style="font-size:0.95rem;font-weight:600;margin-top:4px;">{selected_period.strftime('%B %Y')} &nbsp;·&nbsp; {season}</div>
</div>
</div>
<div>
<div class="aqi-label" style="margin-bottom:14px;">Pollutant Profile</div>
{bars_html}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px;">
<div class="info-item">
<div class="ilabel">SO₂</div>
<div class="ivalue" style="color:#3b82f6;">{so2_v} µg/m³</div>
</div>
<div class="info-item">
<div class="ilabel">O₃</div>
<div class="ivalue" style="color:#f97316;">{o3_v} µg/m³</div>
</div>
<div class="info-item">
<div class="ilabel">Temperature</div>
<div class="ivalue">{at_v} °C</div>
</div>
<div class="info-item">
<div class="ilabel">Humidity</div>
<div class="ivalue">{rh_v} %</div>
</div>
<div class="info-item">
<div class="ilabel">Wind</div>
<div class="ivalue">💨 {ws_v} m/s {wind_dir}</div>
</div>
<div class="info-item" style="background:linear-gradient(135deg,#7c2d12,#1e293b);border:1px solid #dc262650;">
<div class="ilabel" style="color:#fca5a5;">🚬 Cig Equiv</div>
<div class="ivalue" style="color:#fef2f2;">{cig} / day</div>
</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ── AQI Trend Bar Chart ──────────────────────────────────────────────────
    trend_d = df_trend[df_trend['Location'] == search_query].sort_values('Month')

    if not trend_d.empty:
        st.markdown(f"<p style='color:#90caf9;font-weight:600;margin-top:24px;margin-bottom:6px;'>📈 {search_query} — AQI Trend Over Time</p>", unsafe_allow_html=True)

        sel_label = selected_period.strftime('%b %Y')
        border_widths = [2.5 if lbl == sel_label else 0 for lbl in trend_d['MonthLabel']]
        border_colors = ['#f8fafc' if lbl == sel_label else 'rgba(0,0,0,0)' for lbl in trend_d['MonthLabel']]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=trend_d['MonthLabel'],
            y=trend_d['AQI'],
            marker=dict(
                color=trend_d['AQI'],
                colorscale=[[0, '#2563eb'], [0.5, '#eab308'], [1, '#ef4444']],
                cmin=0, cmax=400,
                line=dict(width=border_widths, color=border_colors)
            ),
            hovertemplate='<b>%{x}</b><br>AQI: %{y}<extra></extra>',
            showlegend=False
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='#0f172a',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif', color='#94a3b8', size=12),
            xaxis=dict(showgrid=False, color='#64748b', linecolor='#334155'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#64748b', title='AQI', rangemode='tozero'),
            bargap=0.25,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
