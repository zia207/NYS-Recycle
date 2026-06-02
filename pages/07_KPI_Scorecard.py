"""pages/07_kpi_scorecard.py"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import q_latest_kpi, q_scorecard_summary

st.set_page_config(page_title="KPI Scorecard · NYS Recycling", layout="wide")

TARGETS = {
    "mrr":      dict(label="Material Recovery Rate",     unit="%",    target=86,  higher=True,  category="Operational"),
    "ptb":      dict(label="Processing Time / Batch",    unit="h",    target=4.0, higher=False, category="Operational"),
    "downtime": dict(label="Equipment Downtime",         unit="%",    target=5.0, higher=False, category="Operational"),
    "wsi":      dict(label="Workplace Safety Incidents", unit="/100", target=1.0, higher=False, category="Workforce"),
    "wdr":      dict(label="Waste Diversion Rate",       unit="%",    target=80,  higher=True,  category="Environmental"),
    "css":      dict(label="Customer Satisfaction",      unit="/5",   target=4.2, higher=True,  category="Financial"),
    "te":       dict(label="Transportation Efficiency",  unit="%",    target=88,  higher=True,  category="Operational"),
    "etr":      dict(label="Employee Turnover Rate",     unit="%",    target=15,  higher=False, category="Workforce"),
    "contam":   dict(label="Contamination Rate",         unit="%",    target=6.0, higher=False, category="Environmental"),
    "energy":   dict(label="Energy Consumption",         unit="kWh/t",target=30,  higher=False, category="Environmental"),
}
CAT_COLORS = {"Operational":"#3a8ee0","Environmental":"#1e7a49","Workforce":"#e09d20","Financial":"#8b5cf6"}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    st.divider()
    view_mode   = st.radio("View Mode", ["Statewide Summary","Per-Center Comparison"])

df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]

st.markdown("## 📋 KPI Scorecard")
st.caption("Performance vs. targets across all 10 KPI dimensions · Current period")

if df.empty:
    st.warning("No centers match filters.")
    st.stop()

if view_mode == "Statewide Summary":
    # ── Progress bars for each KPI ────────────────────────────────────────────
    st.markdown("### Statewide Average vs. Target")
    cols = st.columns(2)
    for i, (key, cfg) in enumerate(TARGETS.items()):
        val = getattr(score, f"avg_{key}")
        t   = cfg["target"]
        if cfg["higher"]:
            pct = min(100, val/t*100)
        else:
            pct = min(100, t/max(val,0.01)*100)
        good = pct >= 90
        warn = pct >= 70
        bar_color = "#1e7a49" if good else "#e09d20" if warn else "#d94a4a"
        icon = "🟢" if good else "🟡" if warn else "🔴"
        direction = "↑ higher better" if cfg["higher"] else "↓ lower better"
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#f9faf8;border-radius:10px;padding:14px 16px;
                        margin-bottom:12px;border:1px solid #e4e4e0">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:12px;font-weight:600;color:#1a1a18">{icon} {cfg['label']}</span>
                <span style="font-size:10px;background:{CAT_COLORS[cfg['category']]}22;
                             color:{CAT_COLORS[cfg['category']]};padding:2px 7px;border-radius:10px;
                             font-weight:600">{cfg['category']}</span>
              </div>
              <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:8px">
                <span style="font-size:22px;font-weight:700;color:{bar_color}">{val:.2f}{cfg['unit']}</span>
                <span style="font-size:11px;color:#666">Target: {t}{cfg['unit']} · {direction}</span>
              </div>
              <div style="background:#e4e4e0;border-radius:4px;height:8px;overflow:hidden">
                <div style="background:{bar_color};width:{pct:.0f}%;height:100%;
                            border-radius:4px;transition:width 1s"></div>
              </div>
              <div style="font-size:10px;color:#999;margin-top:4px;text-align:right">{pct:.0f}% of target</div>
            </div>""", unsafe_allow_html=True)

    # ── Radar chart: statewide vs target ─────────────────────────────────────
    st.divider()
    st.markdown("### KPI Radar — Statewide Average vs. Target")

    def normalize(key, val):
        cfg = TARGETS[key]
        t   = cfg["target"]
        if cfg["higher"]:
            return min(100, val/t*100)
        else:
            return min(100, t/max(val,0.001)*100)

    radar_keys = list(TARGETS.keys())
    radar_labels = [TARGETS[k]["label"].replace(" ","<br>") for k in radar_keys]
    actual_vals  = [normalize(k, getattr(score, f"avg_{k}")) for k in radar_keys]
    target_vals  = [100] * len(radar_keys)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=actual_vals+[actual_vals[0]],
                                  theta=radar_labels+[radar_labels[0]],
                                  fill="toself", name="Statewide Avg",
                                  fillcolor="rgba(30,122,73,0.2)",
                                  line=dict(color="#1e7a49",width=2.5)))
    fig.add_trace(go.Scatterpolar(r=target_vals+[100],
                                  theta=radar_labels+[radar_labels[0]],
                                  fill="toself", name="Target",
                                  fillcolor="rgba(58,142,224,0.08)",
                                  line=dict(color="#3a8ee0",width=1.5,dash="dash")))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,110])),
                      height=500, margin=dict(t=40),
                      legend=dict(orientation="h",y=-0.1))
    st.plotly_chart(fig, use_container_width=True)

else:
    # ── Per-center radar comparison ───────────────────────────────────────────
    st.markdown("### Per-Center KPI Comparison")
    centers = df[["center_id","center_name"]].set_index("center_id")["center_name"].to_dict()
    sel = st.multiselect("Select up to 4 centers",
                         options=list(centers.keys()),
                         default=list(centers.keys())[:3],
                         format_func=lambda x: centers[x])
    if not sel:
        st.info("Select at least one center above.")
    else:
        fig2 = go.Figure()
        palette = ["#1e7a49","#3a8ee0","#e09d20","#d94a4a"]
        for idx, cid in enumerate(sel[:4]):
            row = df[df["center_id"]==cid].iloc[0]
            norm = [normalize(k, row[k]) for k in radar_keys]
            color = palette[idx]
            fig2.add_trace(go.Scatterpolar(
                r=norm+[norm[0]],
                theta=radar_labels+[radar_labels[0]],
                fill="toself", name=centers[cid],
                fillcolor=color.replace("#","rgba(")+"66)" if False else f"rgba(0,0,0,0)",
                line=dict(color=color, width=2.5)
            ))
        fig2.add_trace(go.Scatterpolar(r=[100]*len(radar_keys)+[100],
                                       theta=radar_labels+[radar_labels[0]],
                                       name="Target", fill="toself",
                                       fillcolor="rgba(0,0,0,0)",
                                       line=dict(color="#aaa",width=1,dash="dot")))
        fig2.update_layout(polar=dict(radialaxis=dict(range=[0,115])),
                           height=520, margin=dict(t=40),
                           legend=dict(orientation="h",y=-0.12))
        st.plotly_chart(fig2, use_container_width=True)

        # Heatmap of selected centers
        st.markdown("#### KPI Heatmap — Selected Centers")
        heat_data = []
        for cid in sel[:4]:
            row = df[df["center_id"]==cid].iloc[0]
            heat_data.append({
                "Center": centers[cid],
                **{TARGETS[k]["label"]: round(normalize(k, row[k]),1) for k in radar_keys}
            })
        heat_df = pd.DataFrame(heat_data).set_index("Center")
        fig3 = px.imshow(heat_df, color_continuous_scale="RdYlGn",
                         zmin=50, zmax=110,
                         labels=dict(color="% of target"),
                         aspect="auto")
        fig3.update_layout(height=200, margin=dict(t=10,b=0))
        st.plotly_chart(fig3, use_container_width=True)
