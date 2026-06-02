"""pages/02_interactive_map.py"""
import streamlit as st
import folium
from folium.plugins import MarkerCluster, MiniMap
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import q_map_data, q_monthly_trend

st.set_page_config(page_title="Interactive Map · NYS Recycling KPI", layout="wide")

METRIC_OPTIONS = {
    "Material Recovery Rate (MRR %)":  ("mrr",     "%",  True,  [60,95]),
    "Waste Diversion Rate (WDR %)":    ("wdr",     "%",  True,  [60,92]),
    "Contamination Rate (%)":          ("contam",  "%",  False, [1,12]),
    "Customer Satisfaction (CSS /5)":  ("css",     "/5", True,  [3.0,5.0]),
    "Equipment Downtime (%)":          ("downtime","%",  False, [2,12]),
    "Transportation Efficiency (%)":   ("te",      "%",  True,  [70,100]),
    "Employee Turnover Rate (%)":      ("etr",     "%",  False, [5,30]),
    "Energy Consumption (kWh/ton)":    ("energy","kWh/t",False, [20,65]),
}

TYPE_COLORS = {
    "Municipal": "#1e7a49",
    "Commercial":"#3a8ee0",
    "Electronic":"#e09d20",
    "Hazardous": "#d94a4a",
}

def score_color(s):
    if s>=85: return "#0d4d2c"
    if s>=75: return "#1e7a49"
    if s>=65: return "#a36b0b"
    return "#a82828"

def interp_color(val, lo, hi, higher_better=True):
    """Interpolate between red→green (or green→red)."""
    t = max(0.0, min(1.0, (val-lo)/(hi-lo)))
    if not higher_better:
        t = 1 - t
    r = int(215 * (1-t) + 30 * t)
    g = int(68  * (1-t) + 122 * t)
    b = int(68  * (1-t) + 73  * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def make_circle_icon(color, border_color, label):
    return folium.DivIcon(
        html=f"""
          <div style="
            width:28px;height:28px;border-radius:50%;
            background:{color};border:2.5px solid {border_color};
            display:flex;align-items:center;justify-content:center;
            font-size:9px;font-weight:700;color:white;
            font-family:sans-serif;box-shadow:0 2px 6px rgba(0,0,0,.35);
            text-shadow:0 1px 2px rgba(0,0,0,.6);cursor:pointer;
          ">{label}</div>""",
        icon_size=(28,28), icon_anchor=(14,14)
    )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    st.divider()
    metric_label= st.selectbox("Map Metric", list(METRIC_OPTIONS.keys()))
    use_cluster = st.checkbox("Cluster markers", value=False)
    show_mini   = st.checkbox("Show mini-map",   value=True)

metric_key, metric_unit, higher_better, (vlo, vhi) = METRIC_OPTIONS[metric_label]

# ── Load data ──────────────────────────────────────────────────────────────────
df = q_map_data(metric_key, center_type, region)

st.markdown("## 🗺️ Interactive NYS Recycling Center Map")
st.caption(f"OpenStreetMap · {len(df)} centers shown · Metric: **{metric_label}** · Click a marker for full KPI popup")

if df.empty:
    st.warning("No centers match filters.")
    st.stop()

# ── Build Folium map ───────────────────────────────────────────────────────────
m = folium.Map(
    location=[42.9, -75.6],
    zoom_start=7,
    tiles="OpenStreetMap",
    control_scale=True
)

# Optional minimap
if show_mini:
    MiniMap(toggle_display=True, tile_layer="OpenStreetMap").add_to(m)

# Optional cluster
layer = MarkerCluster(name="Centers") if use_cluster else m

for _, row in df.iterrows():
    val   = row["metric_value"]
    score = row["composite_score"]
    col   = interp_color(val, vlo, vhi, higher_better)
    bc    = score_color(score)
    lbl   = row["center_id"].replace("C0","").replace("C","")

    score_txt = ("🟢 Excellent" if score>=85 else "🔵 Good" if score>=75
                 else "🟡 Fair" if score>=65 else "🔴 Needs Attention")

    popup_html = f"""
    <div style="font-family:Arial,sans-serif;min-width:230px;font-size:12px;line-height:1.7">
      <b style="font-size:13px">{row['center_name']}</b><br>
      <span style="font-size:11px;color:#555">{row['city']} · {row['region']}</span><br>
      <span style="background:{bc}22;color:{bc};padding:2px 7px;border-radius:10px;
                   font-size:10px;font-weight:bold">{score_txt} · Score {score}</span>
      <hr style="margin:6px 0;border-color:#eee">
      <table style="width:100%;border-collapse:collapse">
        <tr><td style="color:#777">Type</td>   <td align="right"><b>{row['center_type']}</b></td></tr>
        <tr><td style="color:#777">MRR</td>    <td align="right"><b>{row['mrr']:.1f}%</b></td></tr>
        <tr><td style="color:#777">WDR</td>    <td align="right"><b>{row['wdr']:.1f}%</b></td></tr>
        <tr><td style="color:#777">CSS</td>    <td align="right"><b>{row['css']:.2f}/5</b></td></tr>
        <tr><td style="color:#777">Contam.</td><td align="right"><b>{row['contam']:.1f}%</b></td></tr>
        <tr><td style="color:#777">Downtime</td><td align="right"><b>{row['downtime']:.1f}%</b></td></tr>
        <tr><td style="color:#777">Trans. Eff.</td><td align="right"><b>{row['te']:.1f}%</b></td></tr>
        <tr><td style="color:#777">Turnover</td><td align="right"><b>{row['etr']:.1f}%</b></td></tr>
        <tr><td style="color:#777">Energy</td><td align="right"><b>{row['energy']:.1f} kWh/t</b></td></tr>
        <tr><td style="color:#777">Revenue</td><td align="right"><b>${row['revenue']:,.0f}K</b></td></tr>
        <tr style="background:#f5fdf8"><td><b>📍 {metric_label.split('(')[0].strip()}</b></td>
            <td align="right"><b style="color:{col}">{val:.2f}{metric_unit}</b></td></tr>
      </table>
    </div>"""

    tooltip_txt = f"{row['center_name']} · {metric_label.split('(')[0].strip()}: {val:.1f}{metric_unit}"

    marker = folium.Marker(
        location=[row["latitude"], row["longitude"]],
        icon=make_circle_icon(col, bc, lbl),
        tooltip=folium.Tooltip(tooltip_txt, sticky=True),
        popup=folium.Popup(popup_html, max_width=280),
    )
    if use_cluster:
        marker.add_to(layer)
    else:
        marker.add_to(m)

if use_cluster:
    layer.add_to(m)

# Legend
legend_html = f"""
<div style="position:fixed;bottom:30px;left:30px;z-index:1000;background:white;
            border-radius:10px;padding:12px 16px;box-shadow:0 2px 12px rgba(0,0,0,.2);
            font-family:Arial,sans-serif;font-size:11px;min-width:160px">
  <b style="font-size:12px;color:#0d4d2c">Performance Tier</b><br><br>
  <span style="color:#0d4d2c">⬤</span> Excellent (≥ 85)<br>
  <span style="color:#1e7a49">⬤</span> Good (75–84)<br>
  <span style="color:#a36b0b">⬤</span> Fair (65–74)<br>
  <span style="color:#a82828">⬤</span> Needs Attention (< 65)<br>
  <hr style="margin:8px 0;border-color:#eee">
  <b>Marker fill:</b> {metric_label.split('(')[0].strip()}<br>
  <span style="color:#1e7a49">■</span> High
  <span style="color:#d94a4a">■</span> Low
</div>"""
m.get_root().html.add_child(folium.Element(legend_html))

# Type layer control
for ctype, color in TYPE_COLORS.items():
    folium.LayerControl().add_to(m)

map_data = st_folium(m, width="100%", height=520, returned_objects=["last_object_clicked_popup"])

# ── Selected center detail ─────────────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Center KPI Trends")
st.caption("Select any center on the map above, or choose from dropdown")

selected = st.selectbox(
    "Select center for trend analysis",
    options=df["center_id"].tolist(),
    format_func=lambda x: df.loc[df["center_id"]==x,"center_name"].values[0]
)

if selected:
    row = df[df["center_id"]==selected].iloc[0]
    score = row["composite_score"]
    score_txt = ("🟢 Excellent" if score>=85 else "🔵 Good" if score>=75
                 else "🟡 Fair" if score>=65 else "🔴 Needs Attention")

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric("MRR",         f"{row['mrr']:.1f}%")
    m2.metric("WDR",         f"{row['wdr']:.1f}%")
    m3.metric("CSS",         f"{row['css']:.2f}/5")
    m4.metric("Downtime",    f"{row['downtime']:.1f}%")
    m5.metric("Contamination",f"{row['contam']:.1f}%")
    m6.metric("Score",       f"{score} · {score_txt}")

    trend_df = q_monthly_trend(center_id=selected)
    kpi_choices = {
        "MRR (%)":"mrr","WDR (%)":"wdr","CSS /5":"css",
        "Downtime (%)":"downtime","Contamination (%)":"contam",
        "Trans. Eff. (%)":"te","Turnover (%)":"etr","Energy (kWh/t)":"energy"
    }
    kpi_sel = st.selectbox("KPI to trend", list(kpi_choices.keys()), key="trend_kpi")
    kpi_col = kpi_choices[kpi_sel]

    # reload with correct column
    from data.sql_queries import run_query as _rq
    trend2 = _rq(f"""
        SELECT report_month, ROUND({kpi_col},2) AS val
        FROM monthly_kpi WHERE center_id=? ORDER BY report_month
    """, (selected,))

    # State average
    state_avg = _rq(f"""
        SELECT report_month, ROUND(AVG({kpi_col}),2) AS avg_val
        FROM monthly_kpi GROUP BY report_month ORDER BY report_month
    """)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend2["report_month"], y=trend2["val"],
                             mode="lines+markers", name=row["center_name"],
                             line=dict(color="#1e7a49",width=2.5), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=state_avg["report_month"], y=state_avg["avg_val"],
                             mode="lines", name="State Average",
                             line=dict(color="#3a8ee0",dash="dash",width=1.5)))
    fig.update_layout(height=300, margin=dict(t=20,b=0),
                      xaxis_title="Month", yaxis_title=kpi_sel,
                      legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)
