"""pages/08_alerts.py"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import q_alerts, q_latest_kpi

st.set_page_config(page_title="Alerts · NYS Recycling", layout="wide")

LEVEL_CFG = {
    "critical": dict(icon="🔴", color="#d94a4a", bg="#fdf0f0", label="CRITICAL", border="#d94a4a"),
    "warning":  dict(icon="🟡", color="#a36b0b", bg="#fef8ee", label="WARNING",  border="#e09d20"),
    "ok":       dict(icon="🟢", color="#1e7a49", bg="#f0faf4", label="OK",       border="#3aaa6a"),
}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    level_filter = st.multiselect("Filter by Level",
                                  ["critical","warning","ok"],
                                  default=["critical","warning","ok"])
    st.divider()
    st.markdown("**Thresholds**")
    st.caption("🔴 Critical: hard breach\n🟡 Warning: approaching limit\n🟢 OK: meeting targets")

alerts = q_alerts()
if level_filter:
    alerts = alerts[alerts["level"].isin(level_filter)]

# Summary badges
st.markdown("## 🔔 Alerts & Escalation System")
st.caption("Automated threshold monitoring across all 20 NYS recycling centers")

c1,c2,c3 = st.columns(3)
for level, cfg in LEVEL_CFG.items():
    n = len(alerts[alerts["level"]==level]) if not alerts.empty else 0
    col = {"critical":c1,"warning":c2,"ok":c3}[level]
    col.markdown(f"""
    <div style="background:{cfg['bg']};border:2px solid {cfg['border']};
                border-radius:12px;padding:16px 20px;text-align:center">
      <div style="font-size:28px;font-weight:700;color:{cfg['color']}">{n}</div>
      <div style="font-size:12px;font-weight:600;color:{cfg['color']}">{cfg['icon']} {cfg['label']}</div>
    </div>""", unsafe_allow_html=True)

st.divider()

if alerts.empty:
    st.info("No alerts match the selected filters.")
else:
    for _, row in alerts.iterrows():
        cfg = LEVEL_CFG.get(row["level"], LEVEL_CFG["ok"])
        st.markdown(f"""
        <div style="background:{cfg['bg']};border:1px solid #e4e4e0;
                    border-left:4px solid {cfg['border']};
                    border-radius:10px;padding:14px 18px;margin-bottom:10px">
          <div style="display:flex;align-items:flex-start;gap:12px">
            <span style="font-size:18px;flex-shrink:0">{cfg['icon']}</span>
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                <b style="font-size:13px;color:#1a1a18">{row['center_name']}</b>
                <span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;
                             background:{cfg['color']}22;color:{cfg['color']}">{cfg['label']}</span>
                <span style="font-size:10px;font-weight:600;color:#3a8ee0;padding:2px 7px;
                             background:#eaf2fc;border-radius:10px">{row['kpi']}</span>
              </div>
              <div style="font-size:12px;color:#333;margin-bottom:6px">{row['message']}</div>
              <div style="display:flex;gap:20px;font-size:11px;color:#666">
                <span>Value: <b style="color:#1a1a18">{row['value']}</b></span>
                <span>Threshold: <b style="color:#1a1a18">{row['threshold']}</b></span>
                <span>Date: <b style="color:#1a1a18">{row['created_at']}</b></span>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# Live threshold check against latest data
st.divider()
st.markdown("### 🔍 Live KPI Threshold Check (Latest Month)")
st.caption("Auto-generated alerts based on current KPI values vs. targets")

df = q_latest_kpi()
RULES = [
    ("mrr",     86,   False, "MRR below 86% state target"),
    ("wdr",     80,   False, "WDR below 80% target"),
    ("contam",  8.0,  True,  "Contamination > 8% critical threshold"),
    ("downtime",7.0,  True,  "Equipment downtime > 7%"),
    ("wsi",     1.5,  True,  "Safety incidents > 1.5/100"),
    ("etr",     20.0, True,  "Turnover rate > 20%"),
    ("css",     3.8,  False, "CSS below 3.8 (service risk)"),
    ("te",      80.0, False, "Transport efficiency below 80%"),
]

live_alerts = []
for _, row in df.iterrows():
    for col, thresh, over, msg in RULES:
        val = row[col]
        breach = (val > thresh) if over else (val < thresh)
        if breach:
            live_alerts.append({
                "Center": row["center_name"],
                "Type": row["center_type"],
                "KPI": col.upper(),
                "Value": round(val, 2),
                "Threshold": thresh,
                "Issue": msg,
                "Score": row["composite_score"]
            })

if live_alerts:
    la_df = pd.DataFrame(live_alerts).sort_values("Score")
    st.dataframe(la_df.style
        .applymap(lambda v: "background-color:#fdf0f0;color:#a82828" if isinstance(v,str) and "Issue" in str(la_df.columns) else "",
                  subset=["Issue"])
        .background_gradient(subset=["Score"], cmap="RdYlGn", vmin=60, vmax=100),
        use_container_width=True, height=400)
else:
    st.success("✅ All centers currently meeting KPI thresholds.")
