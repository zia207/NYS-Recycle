"""pages/03_operational_kpis.py"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import q_latest_kpi, q_monthly_by_type, q_scorecard_summary
from data.db_engine   import run_query

st.set_page_config(page_title="Operational KPIs · NYS Recycling", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    st.divider()
    with st.expander("📋 SQL: PTB Query"):
        st.code("""
SELECT
  c.center_name, c.center_type,
  ROUND(AVG(k.ptb),2) AS avg_ptb_hours,
  ROUND(STDDEV(k.ptb),2) AS std_ptb,
  COUNT(*) AS months
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_name, c.center_type
ORDER BY avg_ptb_hours;
        """, language="sql")
    with st.expander("📋 SQL: Downtime Query"):
        st.code("""
SELECT
  c.center_type,
  ROUND(AVG(k.downtime),2) AS avg_downtime_pct,
  ROUND(MIN(k.downtime),2) AS min_downtime,
  ROUND(MAX(k.downtime),2) AS max_downtime
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_type
ORDER BY avg_downtime_pct DESC;
        """, language="sql")

df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]

st.markdown("## ⚙️ Operational KPIs")
st.caption("Processing efficiency, equipment reliability, and transportation performance")

# KPI row
c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg PTB (h)",         f"{score.avg_ptb:.2f}h",   "Target ≤ 4.0h")
c2.metric("Transport Efficiency",f"{score.avg_te:.1f}%",    "Target ≥ 88%")
c3.metric("Equipment Downtime",  f"{score.avg_downtime:.1f}%","Target ≤ 5%")
c4.metric("Centers Tracked",     str(len(df)))

st.divider()
col1, col2 = st.columns(2)

# PTB by type over time
with col1:
    st.markdown("#### Processing Time per Batch (h) — by Center Type")
    ptb_t = q_monthly_by_type("ptb")
    fig = px.line(ptb_t, x="report_month", y="avg_val", color="center_type",
                  labels={"avg_val":"Avg PTB (h)","report_month":"Month","center_type":"Type"},
                  color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                      "Electronic":"#e09d20","Hazardous":"#d94a4a"},
                  markers=True)
    fig.add_hline(y=4.0, line_dash="dash", line_color="#d94a4a", annotation_text="Target 4.0h")
    fig.update_layout(height=320, margin=dict(t=10,b=0), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# Transport efficiency trend
with col2:
    st.markdown("#### Transportation Efficiency (%) — Monthly Statewide")
    te_t = run_query("""
        SELECT report_month, ROUND(AVG(te),2) AS avg_te, ROUND(MIN(te),2) AS min_te,
               ROUND(MAX(te),2) AS max_te
        FROM monthly_kpi GROUP BY report_month ORDER BY report_month
    """)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=te_t["report_month"], y=te_t["max_te"],
                              fill=None, mode="lines", line_color="rgba(30,122,73,0.2)", showlegend=False))
    fig2.add_trace(go.Scatter(x=te_t["report_month"], y=te_t["min_te"],
                              fill="tonexty", fillcolor="rgba(30,122,73,0.1)",
                              mode="lines", line_color="rgba(30,122,73,0.2)", showlegend=False))
    fig2.add_trace(go.Scatter(x=te_t["report_month"], y=te_t["avg_te"],
                              mode="lines+markers", name="Avg TE",
                              line=dict(color="#1e7a49",width=2.5), marker=dict(size=6)))
    fig2.add_hline(y=88, line_dash="dash", line_color="#d94a4a", annotation_text="Target 88%")
    fig2.update_layout(height=320, margin=dict(t=10,b=0), yaxis=dict(range=[70,100]),
                       xaxis_title="", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col3, col4 = st.columns(2)

# Downtime box by center type
with col3:
    st.markdown("#### Equipment Downtime (%) — Distribution by Type")
    down_all = run_query("""
        SELECT c.center_type, k.downtime
        FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
    """)
    fig3 = px.box(down_all, x="center_type", y="downtime",
                  color="center_type", points="all",
                  color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                      "Electronic":"#e09d20","Hazardous":"#d94a4a"},
                  labels={"downtime":"Downtime (%)","center_type":"Type"})
    fig3.add_hline(y=5, line_dash="dash", line_color="#d94a4a", annotation_text="Target 5%")
    fig3.update_layout(height=300, margin=dict(t=10,b=0), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# PTB distribution
with col4:
    st.markdown("#### PTB (h) — Distribution by Type")
    ptb_all = run_query("""
        SELECT c.center_type, k.ptb
        FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
    """)
    fig4 = px.violin(ptb_all, x="center_type", y="ptb",
                     color="center_type", box=True,
                     color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                         "Electronic":"#e09d20","Hazardous":"#d94a4a"},
                     labels={"ptb":"PTB (h)","center_type":"Type"})
    fig4.add_hline(y=4.0, line_dash="dash", line_color="#d94a4a", annotation_text="Target 4.0h")
    fig4.update_layout(height=300, margin=dict(t=10,b=0), showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

# Center-level operational table
st.divider()
st.markdown("#### Center Operational Report")
tbl = df[["center_name","center_type","region","ptb","downtime","te","tons_processed"]].copy()
tbl.columns = ["Center","Type","Region","PTB (h)","Downtime %","Trans. Eff. %","Tons Processed"]
tbl = tbl.sort_values("Downtime %").reset_index(drop=True)
tbl.index += 1
st.dataframe(
    tbl.style
       .background_gradient(subset=["Downtime %"],  cmap="RdYlGn_r", vmin=2, vmax=12)
       .background_gradient(subset=["PTB (h)"],      cmap="RdYlGn_r", vmin=2, vmax=8)
       .background_gradient(subset=["Trans. Eff. %"],cmap="Greens",   vmin=70, vmax=100)
       .format({"PTB (h)":"{:.2f}","Downtime %":"{:.1f}","Trans. Eff. %":"{:.1f}","Tons Processed":"{:.0f}"}),
    use_container_width=True, height=400
)
