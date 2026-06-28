import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from folium.plugins import HeatMap
import plotly.graph_objects as go

st.set_page_config(
    page_title="HCHO Hotspots",
    page_icon="🗺️",
    layout="wide"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.page-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
}
.page-header h1 { font-size: 2rem; font-weight: 700; margin: 0 0 6px 0; }
.page-header p  { color: #94a3b8; margin: 0; font-size: 0.95rem; }

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
    height: 100%;
}
.legend-box h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 14px; }
.legend-item {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px; font-size: 0.88rem;
}
.dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; }

.cig-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #7c2d12, #dc2626);
    border-radius: 8px; padding: 6px 14px;
    color: white; font-size: 0.82rem; font-weight: 600;
    margin-top: 14px;
}

.district-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-top: 12px;
}
.district-card h2 { font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; }
.district-card .tag {
    display: inline-block; padding: 3px 12px;
    border-radius: 999px; font-size: 0.75rem; font-weight: 600;
    margin-bottom: 20px;
}
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.info-item { background: #0f172a; border-radius: 10px; padding: 14px 16px; }
.info-item .ilabel { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.info-item .ivalue { font-size: 1.05rem; font-weight: 600; margin-top: 4px; }
.cause-box {
    margin-top: 16px;
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
    padding: 14px 16px;
}
.cause-box .clabel { font-size: 0.75rem; color: #f87171; text-transform: uppercase; letter-spacing: 0.06em; }
.cause-box .cvalue { font-size: 1rem; font-weight: 600; margin-top: 4px; }

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
  <h1>🧪 HCHO Hotspot Monitor</h1>
  <p>Formaldehyde (HCHO) concentration across Maharashtra districts</p>
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
    st.markdown("<p style='color:#94a3b8;font-size:0.85rem;margin-top:8px;'>📅 Select Month</p>", unsafe_allow_html=True)
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
    CO=('CO', 'mean'),
    NO2=('NO2', 'mean'),
    frp=('frp', 'mean'),
    u10=('u10', 'mean'),
    v10=('v10', 'mean'),
).reset_index()

# Compare with previous month
prev_idx = max(0, selected_month_idx - 1)
prev_period = available_months[prev_idx]
df_prev = df_raw[df_raw['Date'].dt.to_period('M') == prev_period].groupby('District').agg(
    HCHO=('HCHO', 'mean'), frp=('frp', 'mean')
).reset_index().rename(columns={'HCHO': 'HCHO_prev', 'frp': 'frp_prev'})
df_agg = df_agg.merge(df_prev, on='District', how='left')

df_agg['Lat'] = df_agg['District'].map(lambda x: maharashtra_districts.get(x.strip(), (None, None))[0])
df_agg['Lon'] = df_agg['District'].map(lambda x: maharashtra_districts.get(x.strip(), (None, None))[1])
df_agg = df_agg.dropna(subset=['Lat', 'Lon'])

df_agg['HCHO_Index'] = (df_agg['HCHO'] * 1_000_000).clip(0, 500)
# Cigarette equivalent: use HCHO_Index as PM2.5 proxy (same units scale)
df_agg['cig_equiv'] = (df_agg['HCHO_Index'] / 23).round(2)

# HCHO % change vs previous month
df_agg['hcho_pct_change'] = ((df_agg['HCHO'] - df_agg['HCHO_prev']) / df_agg['HCHO_prev'].replace(0, np.nan) * 100).fillna(0).round(1)
df_agg['frp_pct_change']  = ((df_agg['frp']  - df_agg['frp_prev'])  / df_agg['frp_prev'].replace(0, np.nan)  * 100).fillna(0).round(1)

# ── Multi-Month Trend Data (for district line chart) ────────────────────────
# Same HCHO Index / cig-equivalent methodology as above, but computed for
# every month so each district has a full historical series to plot.
df_raw['Month'] = df_raw['Date'].dt.to_period('M')

df_trend = df_raw.groupby(['District', 'Month']).agg(
    HCHO=('HCHO', 'mean'),
    frp=('frp', 'mean'),
).reset_index()
df_trend['District'] = df_trend['District'].str.strip()

df_trend['HCHO_Index'] = (df_trend['HCHO'] * 1_000_000).clip(0, 500)
df_trend['cig_equiv'] = (df_trend['HCHO_Index'] / 23).round(2)
df_trend['MonthLabel'] = df_trend['Month'].apply(lambda m: m.strftime('%b %Y'))
df_trend = df_trend.sort_values('Month')

# ── Map Mode Toggle ──────────────────────────────────────────────────────────
map_mode = st.radio(
    "🗺️ Map Mode",
    ["HCHO Concentration", "🚬 Cigarette Equivalent"],
    horizontal=True
)

# ── Summary Metrics ──────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("🔴 Peak HCHO", f"{df_agg['HCHO'].max():.6f} ppm",
     df_agg.loc[df_agg['HCHO'].idxmax(), 'District']),
    ("📊 Avg HCHO", f"{df_agg['HCHO'].mean():.6f} ppm", f"{len(df_agg)} districts"),
    ("🚬 Max Cig Equiv", f"{df_agg['cig_equiv'].max()} cigs/day",
     df_agg.loc[df_agg['cig_equiv'].idxmax(), 'District']),
    ("📅 Period", selected_period.strftime('%B %Y'), f"{len(df_month)} data points"),
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
    m = folium.Map(location=[19.1136, 78.8480], zoom_start=7, tiles='CartoDB dark_matter')

    heat_data = [[float(row['Lat']), float(row['Lon']), float(row['HCHO_Index'])] for _, row in df_agg.iterrows()]
    HeatMap(
        heat_data, radius=60, blur=30, max_zoom=1,
        min_opacity=0.15, max_opacity=0.75,
        gradient={0.0:'blue', 0.25:'cyan', 0.4:'lime', 0.6:'yellow', 0.8:'orange', 1.0:'red'}
    ).add_to(m)

    for _, row in df_agg.iterrows():
        hcho_val = row['HCHO']
        cig = row['cig_equiv']
        district = row['District']

        if hcho_val <= 0.0002:
            status, color = "LOW", "#3b82f6"
        elif hcho_val <= 0.0003:
            status, color = "MODERATE", "#22c55e"
        elif hcho_val <= 0.0004:
            status, color = "HIGH", "#f97316"
        else:
            status, color = "VERY HIGH", "#ef4444"

        # Wind direction
        u, v = row['u10'], row['v10']
        wind_dir = ""
        if not (pd.isna(u) or pd.isna(v)):
            angle = np.degrees(np.arctan2(u, v)) % 360
            dirs = ['N','NE','E','SE','S','SW','W','NW']
            wind_dir = dirs[int((angle + 22.5) / 45) % 8]

        if map_mode == "🚬 Cigarette Equivalent":
            main_stat = f"🚬 {cig} cigarettes/day equivalent"
        else:
            main_stat = f"HCHO: {hcho_val:.8f} ppm"

        popup_html = f"""
        <div style="font-family:Inter,Arial;width:260px;padding:4px;">
          <h4 style="margin:0 0 8px;font-size:1rem;">{district}</h4>
          <span style="background:{color};color:white;padding:2px 8px;border-radius:999px;font-size:0.72rem;font-weight:600;">{status}</span>
          <hr style="margin:8px 0;border-color:#e2e8f0;">
          <b>{main_stat}</b><br>
          🔥 Fire Power: {f"{row['frp']:.2f}" if not pd.isna(row['frp']) else "N/A"}<br><br>
          💨 Wind: {wind_dir if wind_dir else 'N/A'}<br>
          🚬 Cig Equiv: <b>{cig}</b>/day<br>
          📈 HCHO vs prev month: {row['hcho_pct_change']:+.1f}%
        </div>"""

        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"<b>{district}</b> — {'🚬 '+str(cig)+' cigs/day' if map_mode=='🚬 Cigarette Equivalent' else 'HCHO: '+str(round(hcho_val,8))}",
            color=color, fill=True, fillColor=color,
            fillOpacity=0.5, weight=1.5, opacity=0.6
        ).add_to(m)

    st_folium(m, width="100%", height=650)

with legend_col:
    st.markdown("""
    <div class="legend-box">
      <h4>HCHO Levels</h4>
      <div class="legend-item"><div class="dot" style="background:#3b82f6;"></div><div><b>Low</b><br><small>≤ 0.0002 ppm</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#22c55e;"></div><div><b>Moderate</b><br><small>0.0002–0.0003 ppm</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#f97316;"></div><div><b>High</b><br><small>0.0003–0.0004 ppm</small></div></div>
      <div class="legend-item"><div class="dot" style="background:#ef4444;"></div><div><b>Very High</b><br><small>> 0.0004 ppm</small></div></div>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>🌡️ Heatmap</h4>
      <div style="height:120px;width:100%;border-radius:8px;background:linear-gradient(to top,#2563eb,#06b6d4,#22c55e,#eab308,#f97316,#ef4444);margin-bottom:6px;"></div>
      <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#94a3b8;">
        <span>Low</span><span>High</span>
      </div>
      <hr style="border-color:#334155;margin:14px 0;">
      <h4>🚬 Cig Mode</h4>
      <p style="font-size:0.78rem;color:#94a3b8;line-height:1.5;">
        Estimates cigarettes smoked equivalent based on HCHO Index:<br>
        <code style="background:#0f172a;padding:2px 6px;border-radius:4px;font-size:0.75rem;">
        cigs = HCHO_Index / 23
        </code>
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── District Search Bar ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔍 District Deep-Dive")
st.markdown("<p style='color:#64748b;margin-top:-12px;margin-bottom:16px;'>Search any district to see its complete HCHO profile</p>", unsafe_allow_html=True)

district_names = sorted(df_agg['District'].str.strip().unique().tolist())
search_query = st.selectbox(
    "Search district",
    options=[""] + district_names,
    index=0,
    placeholder="Type a district name…",
    label_visibility="collapsed"
)

if search_query:
    row = df_agg[df_agg['District'].str.strip() == search_query].iloc[0]
    hcho_val   = row['HCHO']
    hcho_idx   = row['HCHO_Index']
    cig        = row['cig_equiv']
    frp_val    = row['frp']
    hcho_chg   = row['hcho_pct_change']
    frp_chg    = row['frp_pct_change']
    u, v       = row['u10'], row['v10']

    if hcho_val <= 0.0002:
        status, tag_color, bg = "LOW", "#3b82f6", "rgba(59,130,246,0.15)"
    elif hcho_val <= 0.0003:
        status, tag_color, bg = "MODERATE", "#22c55e", "rgba(34,197,94,0.15)"
    elif hcho_val <= 0.0004:
        status, tag_color, bg = "HIGH", "#f97316", "rgba(249,115,22,0.15)"
    else:
        status, tag_color, bg = "VERY HIGH", "#ef4444", "rgba(239,68,68,0.15)"

    wind_dir = "N/A"
    if not (pd.isna(u) or pd.isna(v)):
        angle = np.degrees(np.arctan2(u, v)) % 360
        dirs = ['N','NE','E','SE','S','SW','W','NW']
        wind_dir = dirs[int((angle + 22.5) / 45) % 8]

    # Likely cause heuristic
    if not pd.isna(frp_val) and frp_val > 5:
        likely_cause = "🌾 Crop residue / agricultural burning"
    elif hcho_val > 0.0004:
        likely_cause = "🏭 Industrial emissions / vehicular pollution"
    elif hcho_val > 0.0003:
        likely_cause = "🌿 Biogenic emissions + secondary formation"
    else:
        likely_cause = "🌫️ Background atmospheric HCHO"

    hcho_chg_str = f"+{hcho_chg}%" if hcho_chg >= 0 else f"{hcho_chg}%"
    frp_chg_str  = f"+{frp_chg}%"  if frp_chg  >= 0 else f"{frp_chg}%"
    hcho_arrow   = "↑" if hcho_chg >= 0 else "↓"
    frp_arrow    = "↑" if frp_chg  >= 0 else "↓"

    frp_display = f"{frp_val:.2f}" if not pd.isna(frp_val) else "N/A"

    st.markdown(f"""
<div class="district-card">
<h2>{search_query}</h2>
<span class="tag" style="background:{bg};color:{tag_color};border:1px solid {tag_color}40;">● {status}</span>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px;">
<div class="info-item">
<div class="ilabel">Region / State</div>
<div class="ivalue">Maharashtra</div>
</div>
<div class="info-item">
<div class="ilabel">Period</div>
<div class="ivalue">{selected_period.strftime('%B %Y')}</div>
</div>
<div class="info-item">
<div class="ilabel">HCHO Status</div>
<div class="ivalue" style="color:{tag_color};">{status}</div>
</div>
<div class="info-item">
<div class="ilabel">Observed · HCHO Change</div>
<div class="ivalue" style="color:{'#ef4444' if hcho_chg>=0 else '#22c55e'};">HCHO {hcho_arrow} {hcho_chg_str} vs prev month</div>
</div>
<div class="info-item">
<div class="ilabel">Fire Radiative Power</div>
<div class="ivalue" style="color:{'#ef4444' if (not pd.isna(frp_val) and frp_val>5) else '#94a3b8'};">{frp_display} MW &nbsp; <small style="color:{'#ef4444' if frp_chg>=0 else '#22c55e'}">{frp_arrow} {frp_chg_str}</small></div>
</div>
<div class="info-item">
<div class="ilabel">Wind Direction</div>
<div class="ivalue">💨 {wind_dir}</div>
</div>
<div class="info-item">
<div class="ilabel">HCHO Concentration</div>
<div class="ivalue">{hcho_val:.8f} ppm</div>
</div>
<div class="info-item">
<div class="ilabel">HCHO Index (scaled)</div>
<div class="ivalue">{hcho_idx:.2f}</div>
</div>
<div class="info-item" style="background:linear-gradient(135deg,#7c2d12,#1e293b);border:1px solid #dc2626;">
<div class="ilabel" style="color:#fca5a5;">🚬 Cigarette Equivalent</div>
<div class="ivalue" style="color:#fef2f2;">{cig} cigarettes / day</div>
</div>
</div>
<div class="cause-box">
<div class="clabel">⚠️ Likely Cause</div>
<div class="cvalue">{likely_cause}</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ── HCHO Trend Line Chart ────────────────────────────────────────────────
    trend_d = df_trend[df_trend['District'] == search_query].sort_values('Month')

    if not trend_d.empty:
        st.markdown(f"<p style='color:#90caf9;font-weight:600;margin-top:24px;margin-bottom:6px;'>📈 {search_query} — HCHO Index Trend Over Time</p>", unsafe_allow_html=True)

        sel_label = selected_period.strftime('%b %Y')

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=trend_d['MonthLabel'],
            y=trend_d['HCHO_Index'],
            mode='lines+markers',
            line=dict(width=3, color='#3b82f6', shape='spline'),
            marker=dict(
                size=8,
                color=trend_d['HCHO_Index'],
                colorscale=[[0, '#2563eb'], [0.5, '#eab308'], [1, '#ef4444']],
                cmin=0, cmax=500,
                line=dict(width=1, color='#0f172a')
            ),
            fill='tozeroy',
            fillcolor='rgba(59,130,246,0.10)',
            hovertemplate='<b>%{x}</b><br>HCHO Index: %{y:.2f}<extra></extra>',
            showlegend=False
        ))

        # Ring-highlight the currently selected month, if present in the series
        sel_match = trend_d[trend_d['MonthLabel'] == sel_label]
        if not sel_match.empty:
            fig.add_trace(go.Scatter(
                x=[sel_label],
                y=[sel_match['HCHO_Index'].iloc[0]],
                mode='markers',
                marker=dict(size=16, color='rgba(0,0,0,0)', line=dict(color='#f8fafc', width=2)),
                hoverinfo='skip',
                showlegend=False
            ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='#0f172a',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif', color='#94a3b8', size=12),
            xaxis=dict(showgrid=False, color='#64748b', linecolor='#334155'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#64748b', title='HCHO Index', rangemode='tozero'),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})