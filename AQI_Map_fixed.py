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

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.page-header {
    background: linear-gradient(135deg, #0c1445, #1a237e, #283593);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
}
.page-header h1 { font-size: 2rem; font-weight: 700; margin: 0 0 6px 0; }
.page-header p  { color: #90caf9; margin: 0; font-size: 0.95rem; }

.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    color: white;
}
.metric-card .label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.5rem; font-weight: 700; margin: 6px 0 4px; }
.metric-card .sub   { font-size: 0.78rem; color: #64748b; }

.legend-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    color: white;
}
.legend-box h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 14px; }
.legend-item {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 10px; font-size: 0.85rem;
}
.dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; }

.district-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-top: 12px;
}
.district-card h2 { font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; }
.aqi-big {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
    margin: 12px 0 4px;
}
.aqi-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
.driver-bar-wrap { margin-bottom: 10px; }
.driver-label { display:flex; justify-content:space-between; font-size:0.83rem; margin-bottom:4px; }
.driver-bar-bg { background:#0f172a; border-radius:999px; height:8px; overflow:hidden; }
.driver-bar-fill { height:8px; border-radius:999px; }
.info-item { background: #0f172a; border-radius: 10px; padding: 14px 16px; }
.info-item .ilabel { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.info-item .ivalue { font-size: 1.05rem; font-weight: 600; margin-top: 4px; }
.timeline-wrapper {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🌫️ AQI Analysis Dashboard</h1>
  <p>Air Quality Index and pollutant drivers across Maharashtra districts</p>
</div>
""", unsafe_allow_html=True)

# ── Data Load ───────────────────────────────────────────────────────────────
df_raw = pd.read_csv('Mharashtra_merged.csv')
df_raw['Date'] = pd.to_datetime(df_raw['Date'])

maharashtra_districts = {
    'Nandurbar': (21.8189, 74.6027), 'Dhule': (21.1816, 74.7787),
    'Jalgaon': (21.1842, 75.5614),  'Nashik': (19.9975, 73.7898),
    'Aurangabad': (19.8762, 75.3433),'Parbhani': (19.2683, 76.7597),
    'Hingoli': (19.7272, 77.1448),  'Washim': (20.1033, 76.8055),
    'Akola': (20.7123, 77.0042),    'Amravati': (20.9329, 77.7539),
    'Yavatmal': (20.4052, 78.1368), 'Wardha': (20.7465, 78.6038),
    'Nagpur': (21.1458, 79.0882),   'Bhandara': (21.1917, 79.6804),
    'Chandrapur': (19.2841, 79.2961),'Garhchiroli': (20.5496, 80.2782),
    'Buldhana': (20.5033, 75.2236), 'Latur': (18.4088, 76.3864),
    'Osmana bad': (17.8601, 76.7504),'Solapur': (17.6869, 75.9255),
    'Sangli': (16.8523, 74.5654),   'Satara': (17.6807, 73.9949),
    'Kolhapur': (16.7050, 73.7421), 'Ratnagiri': (16.9891, 73.3167),
    'Sindhudurg': (16.3988, 73.3237),'Raigarh': (18.7039, 73.1936),
    'Pune': (18.5204, 73.8567),     'Ahmednagar': (19.0964, 74.7458),
    'Bid': (18.9821, 75.5218),      'Jalna': (19.8450, 75.8853),
    'Thane': (19.2183, 72.9781),    'Mumbai Suburban': (19.1136, 72.8480),
    'Mumbai City': (19.0760, 72.8881),
}

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
        label_visibility="collapsed"
    )
st.markdown('</div>', unsafe_allow_html=True)

selected_period = available_months[selected_month_idx]
df_month = df_raw[df_raw['Date'].dt.to_period('M') == selected_period].copy()

# Aggregate by district (monthly mean)
df_agg = df_month.groupby('District').agg(
    HCHO=('HCHO', 'mean'),
    CO=('CO',   'mean'),
    NO2=('NO2', 'mean'),
    SO2=('SO2', 'mean'),
    O3=('O3',   'mean'),
    frp=('frp', 'mean'),
    u10=('u10', 'mean'),
    v10=('v10', 'mean'),
    t2m=('t2m', 'mean'),
    blh=('blh', 'mean'),
).reset_index()

df_agg['Lat'] = df_agg['District'].map(lambda x: maharashtra_districts.get(x.strip(), (None, None))[0])
df_agg['Lon'] = df_agg['District'].map(lambda x: maharashtra_districts.get(x.strip(), (None, None))[1])
df_agg = df_agg.dropna(subset=['Lat', 'Lon'])

# ── AQI Calculation ──────────────────────────────────────────────────────────
# Normalise each pollutant to 0-1 scale, then compute weighted AQI (0-500)
def norm(series):
    mn, mx = series.min(), series.max()
    return ((series - mn) / (mx - mn + 1e-12)).clip(0, 1)

df_agg['no2_n']  = norm(df_agg['NO2'])
df_agg['co_n']   = norm(df_agg['CO'])
df_agg['hcho_n'] = norm(df_agg['HCHO'])
df_agg['o3_n']   = norm(df_agg['O3'])

# AOD proxy = BLH inversely (high BLH = better dispersion = lower AOD)
df_agg['aod_n'] = 1 - norm(df_agg['blh'])

# Weather proxy = temperature deviation from comfortable 25°C
df_agg['wx_n'] = norm((df_agg['t2m'] - 298.15).abs())

# Weighted AQI (NO2 42%, AOD 31%, CO 17%, Weather 10%)
df_agg['AQI'] = (
    df_agg['no2_n'] * 0.42 +
    df_agg['aod_n'] * 0.31 +
    df_agg['co_n']  * 0.17 +
    df_agg['wx_n']  * 0.10
) * 500
df_agg['AQI'] = df_agg['AQI'].fillna(0).clip(0, 500).round(0).astype(int)

# Per-district driver percentages (contribution of each pollutant to AQI)
driver_cols = {'NO2': 'no2_n', 'AOD': 'aod_n', 'CO': 'co_n', 'Weather': 'wx_n'}
weights     = {'NO2': 0.42,   'AOD': 0.31,    'CO': 0.17,  'Weather': 0.10}
for name, col in driver_cols.items():
    df_agg[f'drv_{name}'] = df_agg[col] * weights[name]

def driver_pct(row):
    total = sum(row[f'drv_{k}'] for k in driver_cols) + 1e-12
    return {k: round(row[f'drv_{k}'] / total * 100, 1) for k in driver_cols}

# HCHO Index for heatmap
df_agg['HCHO_Index'] = (df_agg['HCHO'] * 1_000_000).clip(0, 500)
df_agg['cig_equiv']  = (df_agg['HCHO_Index'] / 23).round(2)

# ── Multi-Month Trend Data (for district line charts) ───────────────────────
# Same AQI methodology as above, but computed for every month so each
# district has a full historical AQI series to plot, not just the
# currently-selected month.
df_raw['Month'] = df_raw['Date'].dt.to_period('M')

df_trend = df_raw.groupby(['District', 'Month']).agg(
    HCHO=('HCHO', 'mean'),
    CO=('CO',   'mean'),
    NO2=('NO2', 'mean'),
    SO2=('SO2', 'mean'),
    O3=('O3',   'mean'),
    blh=('blh', 'mean'),
    t2m=('t2m', 'mean'),
).reset_index()
df_trend['District'] = df_trend['District'].str.strip()

def _norm_grp(s):
    mn, mx = s.min(), s.max()
    return ((s - mn) / (mx - mn + 1e-12)).clip(0, 1)

df_trend['no2_n'] = df_trend.groupby('Month')['NO2'].transform(_norm_grp)
df_trend['co_n']  = df_trend.groupby('Month')['CO'].transform(_norm_grp)
df_trend['aod_n'] = 1 - df_trend.groupby('Month')['blh'].transform(_norm_grp)
df_trend['wx_n']  = df_trend.groupby('Month')['t2m'].transform(lambda s: _norm_grp((s - 298.15).abs()))

df_trend['AQI'] = (
    df_trend['no2_n'] * 0.42 +
    df_trend['aod_n'] * 0.31 +
    df_trend['co_n']  * 0.17 +
    df_trend['wx_n']  * 0.10
) * 500
df_trend['AQI'] = df_trend['AQI'].fillna(0).clip(0, 500).round(0).astype(int)
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
    ("🔴 Worst AQI", str(df_agg['AQI'].max()), worst_aqi_row['District']),
    ("📊 Avg AQI",   str(df_agg['AQI'].mean().round(0).astype(int)), f"{len(df_agg)} districts"),
    ("🚬 Max Cig",   f"{df_agg['cig_equiv'].max()} /day", df_agg.loc[df_agg['cig_equiv'].idxmax(), 'District']),
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

def aqi_color(aqi):
    if aqi <= 50:   return "#22c55e"
    elif aqi <= 100: return "#84cc16"
    elif aqi <= 150: return "#eab308"
    elif aqi <= 200: return "#f97316"
    elif aqi <= 300: return "#ef4444"
    else:            return "#7c3aed"

def aqi_category(aqi):
    if aqi <= 50:   return "Good"
    elif aqi <= 100: return "Satisfactory"
    elif aqi <= 150: return "Moderate"
    elif aqi <= 200: return "Poor"
    elif aqi <= 300: return "Very Poor"
    else:            return "Severe"

with map_col:
    m = folium.Map(location=[19.1136, 78.8480], zoom_start=7, tiles='CartoDB dark_matter')

    heat_vals = df_agg['AQI'] if map_mode == "AQI Heatmap" else df_agg['cig_equiv'] * 23
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

        popup_html = f"""
        <div style="font-family:Inter,Arial;width:270px;padding:4px;">
          <h4 style="margin:0 0 6px;font-size:1rem;">{row['District']}</h4>
          <span style="background:{color};color:white;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:700;">AQI {aqi} · {cat}</span>
          <hr style="margin:8px 0;border-color:#e2e8f0;">
          <b>Major Drivers:</b><br>
          NO2 : {drv['NO2']}%<br>
          AOD : {drv['AOD']}%<br>
          CO  : {drv['CO']}%<br>
          Weather : {drv['Weather']}%<br>
          <hr style="margin:8px 0;border-color:#e2e8f0;">
          🚬 <b>{cig}</b> cigarettes/day equivalent
        </div>"""

        tooltip_txt = f"<b>{row['District']}</b> — {'🚬 '+str(cig)+' cigs/day' if map_mode=='🚬 Cigarette Equivalent' else 'AQI '+str(aqi)+' · '+cat}"

        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=6,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_txt,
            color=color, fill=True, fillColor=color,
            fillOpacity=0.6, weight=2, opacity=0.7
        ).add_to(m)

    st_folium(m, width="100%", height=650)

with legend_col:
    st.markdown("""
    <div class="legend-box">
      <h4>AQI Levels</h4>
      <div class="legend-item"><div class="dot" style="background:#22c55e;"></div><div><b>Good</b><br><small>0–50</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#84cc16;"></div><div><b>Satisfactory</b><br><small>51–100</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#eab308;"></div><div><b>Moderate</b><br><small>101–150</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#f97316;"></div><div><b>Poor</b><br><small>151–200</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#ef4444;"></div><div><b>Very Poor</b><br><small>201–300</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#7c3aed;"></div><div><b>Severe</b><br><small>300+</small></div></div>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>Driver Weights</h4>
      <p style="font-size:0.78rem;color:#94a3b8;line-height:1.7;margin:0;">
        NO₂ &nbsp; 42%<br>
        AOD &nbsp; 31%<br>
        CO &nbsp;&nbsp; 17%<br>
        Weather 10%
      </p>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>🚬 Cig Mode</h4>
      <p style="font-size:0.78rem;color:#94a3b8;line-height:1.5;">
        <code style="background:#0f172a;padding:2px 6px;border-radius:4px;font-size:0.75rem;">
        cigs = PM2.5 / 23
        </code><br>
        <small>(HCHO Index used as PM2.5 proxy)</small>
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── District Search Bar ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔍 District AQI Profile")
st.markdown("<p style='color:#64748b;margin-top:-12px;margin-bottom:16px;'>Search any district to see its complete air quality breakdown</p>", unsafe_allow_html=True)

district_names = sorted(df_agg['District'].str.strip().unique().tolist())
search_query = st.selectbox(
    "Search district",
    options=[""] + district_names,
    index=0,
    placeholder="Type a district name…",
    label_visibility="collapsed"
)

if search_query:
    row   = df_agg[df_agg['District'].str.strip() == search_query].iloc[0]
    aqi   = int(row['AQI'])
    color = aqi_color(aqi)
    cat   = aqi_category(aqi)
    cig   = row['cig_equiv']
    drv   = driver_pct(row)
    u, v  = row['u10'], row['v10']

    wind_dir = "N/A"
    if not (pd.isna(u) or pd.isna(v)):
        angle = np.degrees(np.arctan2(u, v)) % 360
        dirs = ['N','NE','E','SE','S','SW','W','NW']
        wind_dir = dirs[int((angle + 22.5) / 45) % 8]

    # Build driver bars HTML
    driver_colors = {'NO2': '#3b82f6', 'AOD': '#8b5cf6', 'CO': '#f97316', 'Weather': '#06b6d4'}
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

    temp_c = round(row['t2m'] - 273.15, 1) if not pd.isna(row['t2m']) else "N/A"
    blh    = round(row['blh'], 0) if not pd.isna(row['blh']) else "N/A"
    no2_v  = f"{row['NO2']:.2e}" if not pd.isna(row['NO2']) else "N/A"
    co_v   = f"{row['CO']:.4f}" if not pd.isna(row['CO']) else "N/A"

    st.markdown(f"""
<div class="district-card">
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
<div style="font-size:0.95rem;font-weight:600;margin-top:4px;">{selected_period.strftime('%B %Y')}</div>
</div>
</div>
<div>
<div class="aqi-label" style="margin-bottom:14px;">Major Drivers</div>
{bars_html}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px;">
<div class="info-item">
<div class="ilabel">NO₂</div>
<div class="ivalue" style="color:#3b82f6;">{no2_v}</div>
</div>
<div class="info-item">
<div class="ilabel">CO</div>
<div class="ivalue" style="color:#f97316;">{co_v}</div>
</div>
<div class="info-item">
<div class="ilabel">Temperature</div>
<div class="ivalue">{temp_c} °C</div>
</div>
<div class="info-item">
<div class="ilabel">Wind Direction</div>
<div class="ivalue">💨 {wind_dir}</div>
</div>
<div class="info-item">
<div class="ilabel">Mixing Layer Height</div>
<div class="ivalue">{blh} m</div>
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

    # ── AQI Trend Line Chart ─────────────────────────────────────────────────
    trend_d = df_trend[df_trend['District'] == search_query].sort_values('Month')

    if not trend_d.empty:
        st.markdown(f"<p style='color:#90caf9;font-weight:600;margin-top:24px;margin-bottom:6px;'>📈 {search_query} — AQI Trend Over Time</p>", unsafe_allow_html=True)

        sel_label = selected_period.strftime('%b %Y')
        # Outline the currently-selected month's bar so it stands out from the rest
        border_widths = [2.5 if lbl == sel_label else 0 for lbl in trend_d['MonthLabel']]
        border_colors = ['#f8fafc' if lbl == sel_label else 'rgba(0,0,0,0)' for lbl in trend_d['MonthLabel']]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=trend_d['MonthLabel'],
            y=trend_d['AQI'],
            marker=dict(
                color=trend_d['AQI'],
                colorscale=[[0, '#2563eb'], [0.5, '#eab308'], [1, '#ef4444']],
                cmin=0, cmax=300,
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