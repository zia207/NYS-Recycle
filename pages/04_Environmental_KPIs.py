"""pages/04_environmental_kpis.py"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import (q_latest_kpi, q_monthly_by_region, q_monthly_by_type,
                               q_contamination_by_stream, q_contamination_by_stream_type,
                               q_scorecard_summary)

st.set_page_config(page_title="Environmental KPIs · NYS Recycling", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    stream_region = st.selectbox("Stream Region", ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"], key="sr")
    st.divider()
    with st.expander("📋 SQL: WDR & MRR"):
        st.code("""
SELECT
  c.region, k.report_month,
  ROUND(AVG(k.wdr),2) AS avg_wdr,
  ROUND(AVG(k.mrr),2) AS avg_mrr
FROM monthly_kpi k
JOIN centers c ON c.center_id=k.center_id
GROUP BY c.region, k.report_month
ORDER BY k.report_month;
        """, language="sql")
    with st.expander("📋 SQL: Contamination by Stream"):
        st.code("""
SELECT
  s.material, c.region,
  ROUND(AVG(s.contamination_pct),2) AS avg_contam
FROM material_streams s
JOIN centers c ON c.center_id=s.center_id
GROUP BY s.material, c.region
ORDER BY avg_contam DESC;
        """, language="sql")

df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]

st.markdown("## 🌿 Environmental KPIs")
st.caption("Waste diversion, contamination, and energy metrics across NYS recycling centers")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg WDR",        f"{score.avg_wdr:.1f}%",  "Target ≥ 80%")
c2.metric("Avg MRR",        f"{score.avg_mrr:.1f}%",  "Target ≥ 86%")
c3.metric("Contamination",  f"{score.avg_contam:.1f}%","Target ≤ 6%")
c4.metric("Energy (kWh/t)", f"{score.avg_energy:.1f}", "Target ≤ 30")

st.divider()
col1,col2 = st.columns(2)

with col1:
    st.markdown("#### Waste Diversion Rate (%) by Region — Monthly")
    wdr_r = q_monthly_by_region("wdr")
    fig = px.line(wdr_r, x="report_month", y="avg_val", color="region",
                  markers=True,
                  labels={"avg_val":"WDR (%)","report_month":"Month","region":"Region"},
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig.add_hline(y=80, line_dash="dash", line_color="#d94a4a", annotation_text="Target 80%")
    fig.update_layout(height=320, margin=dict(t=10,b=0), yaxis=dict(range=[60,95]),
                      xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Energy Consumption (kWh/ton) by Center Type")
    energy_t = q_monthly_by_type("energy")
    fig2 = px.line(energy_t, x="report_month", y="avg_val", color="center_type",
                   markers=True,
                   labels={"avg_val":"kWh/ton","report_month":"Month","center_type":"Type"},
                   color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                       "Electronic":"#e09d20","Hazardous":"#d94a4a"})
    fig2.add_hline(y=30, line_dash="dash", line_color="#d94a4a", annotation_text="Target 30 kWh/t")
    fig2.update_layout(height=320, margin=dict(t=10,b=0), xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col3,col4 = st.columns(2)

with col3:
    st.markdown("#### Contamination Rate by Material Stream & Region")
    contam = q_contamination_by_stream(stream_region)
    fig3 = px.bar(contam, x="avg_contam", y="material", color="region",
                  orientation="h", barmode="group",
                  labels={"avg_contam":"Avg Contamination (%)","material":"Material Stream"},
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.add_vline(x=6, line_dash="dash", line_color="#d94a4a", annotation_text="Target ≤6%")
    fig3.update_layout(height=320, margin=dict(t=10,b=0), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Contamination by Stream & Center Type")
    contam2 = q_contamination_by_stream_type()
    fig4 = px.bar(contam2, x="material", y="avg_contam", color="center_type",
                  barmode="group",
                  labels={"avg_contam":"Contamination (%)","material":"Stream","center_type":"Type"},
                  color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                                      "Electronic":"#e09d20","Hazardous":"#d94a4a"})
    fig4.add_hline(y=6, line_dash="dash", line_color="#d94a4a", annotation_text="Target ≤6%")
    fig4.update_layout(height=320, margin=dict(t=10,b=0), xaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)

# MRR scatter vs energy
st.divider()
st.markdown("#### MRR vs Energy Consumption — Center-Level Scatter")
st.caption("Bubble size = Composite Score · Color = Center Type")
scatter = df.copy()
scatter["composite_score"] = scatter["composite_score"].clip(50,100)
fig5 = px.scatter(
    scatter, x="energy", y="mrr", color="center_type",
    size="composite_score", hover_name="center_name",
    hover_data={"city":True,"wdr":True,"contam":True},
    color_discrete_map={"Municipal":"#1e7a49","Commercial":"#3a8ee0",
                        "Electronic":"#e09d20","Hazardous":"#d94a4a"},
    labels={"energy":"Energy (kWh/ton)","mrr":"MRR (%)","center_type":"Type"}
)
fig5.add_hline(y=86,  line_dash="dash", line_color="#d94a4a", annotation_text="MRR target")
fig5.add_vline(x=30,  line_dash="dash", line_color="#3a8ee0", annotation_text="Energy target")
fig5.update_layout(height=350, margin=dict(t=20,b=0))
st.plotly_chart(fig5, use_container_width=True)
