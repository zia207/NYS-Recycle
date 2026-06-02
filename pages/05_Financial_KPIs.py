"""pages/05_financial_kpis.py"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import (q_latest_kpi, q_financial_monthly,
                               q_cost_per_ton_by_type, q_scorecard_summary)
from data.db_engine import run_query

st.set_page_config(page_title="Financial KPIs · NYS Recycling", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type", ["All","Municipal","Commercial","Electronic","Hazardous"])
    region      = st.selectbox("Region",      ["All","NYC Metro","Western NY","Central NY","Capital Region","North Country"])
    st.divider()
    with st.expander("📋 SQL: Revenue & Margin"):
        st.code("""
SELECT
  k.report_month,
  ROUND(SUM(k.revenue),0)  AS total_revenue,
  ROUND(SUM(k.opex),0)     AS total_opex,
  ROUND(SUM(k.revenue-k.opex),0) AS net_margin,
  ROUND(AVG((k.revenue-k.opex)*100.0/k.revenue),1)
      AS avg_margin_pct
FROM monthly_kpi k
JOIN centers c ON c.center_id=k.center_id
GROUP BY k.report_month
ORDER BY k.report_month;
        """, language="sql")
    with st.expander("📋 SQL: Cost per Ton"):
        st.code("""
SELECT
  c.center_type,
  ROUND(AVG(k.opex/k.tons_processed),2)
      AS avg_cost_per_ton
FROM monthly_kpi k
JOIN centers c ON c.center_id=k.center_id
GROUP BY c.center_type
ORDER BY avg_cost_per_ton DESC;
        """, language="sql")

df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]
fin   = q_financial_monthly(center_type, region)

st.markdown("## 💰 Financial KPIs")
st.caption("Revenue, operating costs, margins, and cost efficiency across NYS recycling centers")

if fin.empty:
    st.warning("No financial data for selected filters.")
    st.stop()

last = fin.iloc[-1]
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Revenue ($K)",    f"${last.total_revenue:,.0f}K",  "+4.2% MoM")
c2.metric("Opex ($K)",       f"${last.total_opex:,.0f}K",     "+2.1% MoM")
c3.metric("Net Margin ($K)", f"${last.net_margin:,.0f}K")
c4.metric("Margin %",        f"{last.avg_margin_pct:.1f}%",   "Target ≥ 20%")
c5.metric("Cost/Ton ($)",    f"${last.cost_per_ton:.2f}")

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Revenue vs Opex ($K/month)")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Revenue",    x=fin["report_month"], y=fin["total_revenue"],
                         marker_color="#1e7a49", opacity=0.85))
    fig.add_trace(go.Bar(name="Opex",       x=fin["report_month"], y=fin["total_opex"],
                         marker_color="#d94a4a", opacity=0.75))
    fig.add_trace(go.Scatter(name="Net Margin", x=fin["report_month"], y=fin["net_margin"],
                             mode="lines+markers", yaxis="y2",
                             line=dict(color="#3a8ee0", width=2.5), marker=dict(size=6)))
    fig.update_layout(
        height=320, margin=dict(t=10,b=0), barmode="group",
        yaxis=dict(title="$K"), xaxis_title="",
        yaxis2=dict(title="Net Margin ($K)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.3)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Net Margin % over Time")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=fin["report_month"], y=fin["avg_margin_pct"],
                              mode="lines+markers", fill="tozeroy",
                              fillcolor="rgba(30,122,73,0.1)",
                              line=dict(color="#1e7a49", width=2.5), marker=dict(size=7)))
    fig2.add_hline(y=20, line_dash="dash", line_color="#d94a4a", annotation_text="Target 20%")
    fig2.update_layout(height=320, margin=dict(t=10,b=0),
                       yaxis_title="Margin %", xaxis_title="",
                       yaxis=dict(range=[0,40]))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Cost per Ton ($) by Center Type")
    cpt = q_cost_per_ton_by_type()
    colors = {"Municipal":"#1e7a49","Commercial":"#3a8ee0","Electronic":"#e09d20","Hazardous":"#d94a4a"}
    fig3 = px.bar(cpt, x="center_type", y="avg_cost_per_ton",
                  color="center_type",
                  color_discrete_map=colors,
                  labels={"avg_cost_per_ton":"Avg Cost/Ton ($)","center_type":"Type"},
                  text="avg_cost_per_ton")
    fig3.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
    fig3.update_layout(height=300, margin=dict(t=10,b=0), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Revenue Distribution by Region (latest month)")
    rev_reg = run_query("""
        SELECT c.region, ROUND(SUM(k.revenue),0) AS total_rev
        FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
        WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi)
        GROUP BY c.region
    """)
    fig4 = px.pie(rev_reg, names="region", values="total_rev", hole=0.45,
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig4.update_layout(height=300, margin=dict(t=10,b=0))
    st.plotly_chart(fig4, use_container_width=True)

# Center financial table
st.divider()
st.markdown("#### Center Financial Snapshot")
tbl = df[["center_name","center_type","region","revenue","opex","net_margin","margin_pct","tons_processed"]].copy()
tbl.columns = ["Center","Type","Region","Revenue ($K)","Opex ($K)","Net Margin ($K)","Margin %","Tons"]
tbl = tbl.sort_values("Margin %", ascending=False).reset_index(drop=True)
tbl.index += 1
st.dataframe(
    tbl.style
       .background_gradient(subset=["Margin %"],     cmap="Greens",   vmin=0, vmax=35)
       .background_gradient(subset=["Net Margin ($K)"],cmap="Greens", vmin=0, vmax=1000)
       .format({"Revenue ($K)":"{:,.0f}","Opex ($K)":"{:,.0f}",
                "Net Margin ($K)":"{:,.0f}","Margin %":"{:.1f}","Tons":"{:.0f}"}),
    use_container_width=True, height=400
)
