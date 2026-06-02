"""pages/06_workforce_kpis.py"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import (q_latest_kpi, q_workforce_monthly_by_region,
                               q_scorecard_summary)

st.set_page_config(page_title="Workforce KPIs · NYS Recycling", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    st.divider()
    with st.expander("📋 SQL: Turnover Rate"):
        st.code("""
SELECT
  c.region, k.report_month,
  ROUND(AVG(k.etr),2) AS avg_turnover_pct
FROM monthly_kpi k
JOIN centers c ON c.center_id=k.center_id
GROUP BY c.region, k.report_month
ORDER BY k.report_month;
        """, language="sql")
    with st.expander("📋 SQL: Safety Incidents"):
        st.code("""
SELECT
  c.center_name, c.region,
  ROUND(AVG(k.wsi),2) AS avg_wsi_per_100,
  CASE WHEN AVG(k.wsi)<=1.0 THEN 'Compliant'
       WHEN AVG(k.wsi)<=1.5 THEN 'Watch'
       ELSE 'Non-Compliant' END AS safety_status
FROM monthly_kpi k
JOIN centers c ON c.center_id=k.center_id
GROUP BY c.center_name, c.region
ORDER BY avg_wsi_per_100 DESC;
        """, language="sql")

df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]

st.markdown("## 👷 Workforce KPIs")
st.caption("Employee turnover, safety incidents, and satisfaction across NYS recycling centers")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Turnover Rate", f"{score.avg_etr:.1f}%",   "Target ≤ 15%")
c2.metric("Safety Incidents",  f"{score.avg_wsi:.2f}/100","Target ≤ 1.0")
compliant = len(df[df["wsi"]<=1.0]) if not df.empty else 0
c3.metric("Centers Compliant (Safety)", f"{compliant}/{len(df)}")
c4.metric("Avg CSS",           f"{score.avg_css:.2f}/5",  "Target ≥ 4.2")

st.divider()
col1, col2 = st.columns(2)

wf = q_workforce_monthly_by_region()

with col1:
    st.markdown("#### Employee Turnover Rate (%) by Region")
    fig = px.line(wf, x="report_month", y="avg_etr", color="region",
                  markers=True,
                  labels={"avg_etr":"Turnover (%)","report_month":"Month"},
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig.add_hline(y=15, line_dash="dash", line_color="#d94a4a", annotation_text="Target 15%")
    fig.update_layout(height=320, margin=dict(t=10,b=0), xaxis_title="",
                      yaxis=dict(range=[5,30]))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Safety Incidents per 100 Employees by Region")
    fig2 = px.line(wf, x="report_month", y="avg_wsi", color="region",
                   markers=True,
                   labels={"avg_wsi":"Incidents/100","report_month":"Month"},
                   color_discrete_sequence=px.colors.qualitative.Safe)
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#d94a4a", annotation_text="Target ≤1.0")
    fig2.update_layout(height=320, margin=dict(t=10,b=0), xaxis_title="",
                       yaxis=dict(range=[0,3]))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Turnover Rate Distribution by Center Type")
    from data.db_engine import run_query
    etr_all = run_query("""
        SELECT c.center_type, k.etr FROM monthly_kpi k
        JOIN centers c ON c.center_id=k.center_id
    """)
    fig3 = px.box(etr_all, x="center_type", y="etr", color="center_type",
                  points="all",
                  color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                      "Electronic":"#e09d20","Hazardous":"#d94a4a"},
                  labels={"etr":"Turnover (%)","center_type":"Type"})
    fig3.add_hline(y=15, line_dash="dash", line_color="#d94a4a", annotation_text="Target 15%")
    fig3.update_layout(height=300, margin=dict(t=10,b=0), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### WSI vs Turnover — Scatter by Center")
    fig4 = px.scatter(df, x="etr", y="wsi", color="center_type",
                      size="composite_score", hover_name="center_name",
                      color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                          "Electronic":"#e09d20","Hazardous":"#d94a4a"},
                      labels={"etr":"Turnover (%)","wsi":"WSI/100","center_type":"Type"})
    fig4.add_hline(y=1.0,  line_dash="dash", line_color="#d94a4a")
    fig4.add_vline(x=15.0, line_dash="dash", line_color="#d94a4a")
    fig4.update_layout(height=300, margin=dict(t=10,b=0))
    st.plotly_chart(fig4, use_container_width=True)

# Workforce table
st.divider()
st.markdown("#### Center Workforce Report")
tbl = df[["center_name","center_type","region","etr","wsi","css"]].copy()
tbl.columns = ["Center","Type","Region","Turnover %","WSI/100","CSS"]
tbl["Safety Status"] = tbl["WSI/100"].apply(
    lambda x: "✅ Compliant" if x<=1.0 else "⚠️ Watch" if x<=1.5 else "🔴 Non-Compliant")
tbl = tbl.sort_values("Turnover %").reset_index(drop=True)
tbl.index += 1
st.dataframe(
    tbl.style
       .background_gradient(subset=["Turnover %"],cmap="RdYlGn_r",vmin=5,vmax=30)
       .background_gradient(subset=["WSI/100"],   cmap="RdYlGn_r",vmin=0,vmax=3)
       .background_gradient(subset=["CSS"],        cmap="Greens",  vmin=3.0,vmax=5.0)
       .format({"Turnover %":"{:.1f}","WSI/100":"{:.2f}","CSS":"{:.2f}"}),
    use_container_width=True, height=420
)
