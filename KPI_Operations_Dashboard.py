"""
Recycle Center KPIs
Index / Home page
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data.sql_queries import q_latest_kpi, q_scorecard_summary, q_alerts

st.set_page_config(
    page_title="Recycle Center KPIs",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=52)
    st.markdown("### Recycle Center KPIs")
    st.caption("KPI Operations Dashboard")
    st.divider()
    st.markdown("""
    **Pages**
    - 📊 Executive Summary
    - 🗺️ Interactive Map
    - ⚙️ Operational KPIs
    - 🌿 Environmental KPIs
    - 💰 Financial KPIs
    - 👷 Workforce KPIs
    - 📋 KPI Scorecard
    - 🔔 Alerts
    - 📄 SQL Queries
    """)
    st.divider()
    st.caption("Data refreshed: Jan 2025")
    st.caption("Source: NYS DEC (simulated)")
    st.caption("© 2026 Zia Ahmed, Upatta Analytics")

# ── Hero ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d4d2c 0%, #1e7a49 60%, #3aaa6a 100%);
    border-radius: 16px; padding: 40px 44px; margin-bottom: 28px; color: white;">
  <div style="display:flex; align-items:center; gap:18px; margin-bottom:14px">
    <span style="font-size:48px; line-height:1">♻️</span>
    <div>
      <h1 style="margin:0; font-size:28px; font-weight:800; color:white; letter-spacing:-0.3px">
        Recycle Center KPIs
      </h1>
      <p style="margin:5px 0 0; opacity:0.85; font-size:14px">
        New York State Department of Environmental Conservation · Operations Analytics
      </p>
    </div>
  </div>
  <p style="opacity:0.9; font-size:14px; max-width:720px; margin:0; line-height:1.7">
    A comprehensive KPI tracking and reporting framework for <strong>20 recycling centers</strong>
    across New York State, powered by predefined SQL queries and live OpenStreetMap visualization.
    Monitor efficiency, sustainability, financial health, and workforce performance across
    5 regions and 4 center types.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background:#fff8e6; border:1.5px solid #e09d20; border-left:5px solid #e09d20;
    border-radius:10px; padding:14px 20px; margin-bottom:28px;
    display:flex; align-items:flex-start; gap:12px">
  <span style="font-size:22px; flex-shrink:0; line-height:1.4">⚠️</span>
  <div>
    <span style="font-weight:700; font-size:13px; color:#a36b0b">DEMONSTRATION PURPOSE ONLY</span><br>
    <span style="font-size:12px; color:#5a4010; line-height:1.75">
      All data, center locations, KPI values, financial figures, and alert conditions displayed
      in this dashboard are <strong>entirely simulated</strong> and do not represent any real
      recycling facility, government agency, or operational program. This application is intended
      solely as a <strong>technical demonstration</strong> of a Streamlit-based KPI monitoring framework.
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Live Metrics — State at a Glance ─────────────────────────────────────────────
df        = q_latest_kpi()
score     = q_scorecard_summary().iloc[0]
alerts_df = q_alerts()

crit_n = int(len(alerts_df[alerts_df["level"] == "critical"]))
warn_n = int(len(alerts_df[alerts_df["level"] == "warning"]))

st.markdown("### State at a Glance")
st.caption("Statewide averages for the latest reporting month across all 20 centers.")

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
c1.metric("Centers",     f"{len(df)}",                 "Statewide")
c2.metric("Avg MRR",     f"{score.avg_mrr:.1f}%",      "Target 86%",
          delta_color="normal" if score.avg_mrr >= 86 else "inverse")
c3.metric("Avg WDR",     f"{score.avg_wdr:.1f}%",      "Target 80%",
          delta_color="normal" if score.avg_wdr >= 80 else "inverse")
c4.metric("Avg CSS",     f"{score.avg_css:.2f}",       "Target 4.2",
          delta_color="normal" if score.avg_css >= 4.2 else "inverse")
c5.metric("Downtime",    f"{score.avg_downtime:.1f}%", "Target ≤ 5%",
          delta_color="inverse" if score.avg_downtime > 5 else "normal")
c6.metric("Contam.",     f"{score.avg_contam:.1f}%",   "Target ≤ 6%",
          delta_color="inverse" if score.avg_contam > 6 else "normal")
c7.metric("🔴 Critical", f"{crit_n}",                  "active alerts")
c8.metric("🟡 Warnings", f"{warn_n}",                  "active alerts")

st.divider()


st.markdown("### Recycle Center KPIs")
st.markdown(
    "Key Performance Indicators (KPIs) are commonly grouped into "
    "**Operational, Environmental, Financial, and Workforce** categories. "
    "These KPIs help managers monitor efficiency, sustainability, profitability, "
    "and employee performance. These KPIs provide a balanced framework for monitoring "
    "the performance of recycling centers and are particularly useful for dashboard "
    "applications, KPI reporting systems, and sustainability assessments involving "
    "multiple recycling facilities across regions."
)

st.markdown("<br>", unsafe_allow_html=True)

# ── 1. Operational KPIs ───────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border:1px solid #d0e6f7; border-left:6px solid #3a8ee0;
            border-radius:12px; padding:24px 28px 8px; margin-bottom:24px;
            background:white">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px">
    <span style="font-size:30px; line-height:1">⚙️</span>
    <div>
      <span style="font-size:18px; font-weight:800; color:#1a1a18">1. Operational KPIs</span>
      <br>
      <span style="font-size:12px; color:#555">
        Processing efficiency, equipment reliability, and transportation performance
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Operational KPIs measure how effectively a recycling center processes incoming "
    "materials and manages daily operations."
)
st.markdown("""
| KPI | Description | Formula / Measurement |
|-----|-------------|----------------------|
| **Throughput Volume** | Amount of recyclable material processed | Tons/day or tons/month |
| **Processing Rate** | Speed of material processing | Tons/hour |
| **Material Recovery Rate** | Percentage of recyclable material successfully recovered | (Recovered Material ÷ Total Input Material) × 100 |
| **Contamination Rate** | Percentage of non-recyclable material in incoming waste stream | (Contaminated Material ÷ Total Input Material) × 100 |
| **Equipment Utilization** | Percentage of available equipment operating time | (Operating Hours ÷ Available Hours) × 100 |
| **Equipment Downtime** | Time equipment is unavailable due to failures or maintenance | Hours/month |
| **Collection Efficiency** | Effectiveness of collection routes and operations | Collected Volume ÷ Planned Volume |
| **Processing Cost per Ton** | Cost to process one ton of material | Total Operating Cost ÷ Total Tons Processed |
""")
st.markdown("""
**Operational Goals**
- Increase throughput.
- Reduce contamination.
- Minimize equipment downtime.
- Improve processing efficiency.
""")

st.divider()

# ── 2. Environmental KPIs ─────────────────────────────────────────────────────────
st.markdown("""
<div style="border:1px solid #c8e6d6; border-left:6px solid #0f6e56;
            border-radius:12px; padding:24px 28px 8px; margin-bottom:24px;
            background:white">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px">
    <span style="font-size:30px; line-height:1">🌿</span>
    <div>
      <span style="font-size:18px; font-weight:800; color:#1a1a18">2. Environmental KPIs</span>
      <br>
      <span style="font-size:12px; color:#555">
        Waste diversion, contamination by material stream, and energy consumption
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Environmental KPIs evaluate the recycling center's contribution to sustainability "
    "and environmental protection."
)
st.markdown("""
| KPI | Description | Measurement |
|-----|-------------|-------------|
| **Diversion Rate** | Percentage of waste diverted from landfills | (Recycled Waste ÷ Total Waste Generated) × 100 |
| **Landfill Avoidance** | Amount of waste prevented from reaching landfills | Tons/year |
| **Greenhouse Gas (GHG) Reduction** | Estimated CO₂ emissions avoided through recycling | Tons CO₂e/year |
| **Energy Consumption** | Energy used during recycling operations | kWh/ton processed |
| **Water Consumption** | Water usage during operations | Gallons or m³/month |
| **Carbon Footprint** | Total emissions from facility operations | Tons CO₂e/year |
| **Recycled Material Recovery** | Quantity of recovered materials by type | Tons of paper, plastic, metal, glass |
| **Renewable Energy Usage** | Percentage of energy from renewable sources | (%) |
""")
st.markdown("""
**Environmental Goals**
- Reduce landfill waste.
- Lower carbon emissions.
- Improve resource recovery.
- Minimize energy and water consumption.
""")

st.divider()

# ── 3. Financial KPIs ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="border:1px solid #e0d5f7; border-left:6px solid #8b5cf6;
            border-radius:12px; padding:24px 28px 8px; margin-bottom:24px;
            background:white">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px">
    <span style="font-size:30px; line-height:1">💰</span>
    <div>
      <span style="font-size:18px; font-weight:800; color:#1a1a18">3. Financial KPIs</span>
      <br>
      <span style="font-size:12px; color:#555">
        Revenue, operating costs, net margins, cost per ton, and profitability
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Financial KPIs assess profitability, cost management, and overall financial health."
)
st.markdown("""
| KPI | Description | Formula |
|-----|-------------|---------|
| **Total Revenue** | Revenue generated from selling recyclables and services | $/month |
| **Revenue per Ton** | Revenue earned per ton of processed material | Revenue ÷ Tons Processed |
| **Operating Cost** | Total facility operating expenses | $/month |
| **Cost per Ton Processed** | Average processing cost per ton | Operating Cost ÷ Tons Processed |
| **Profit Margin** | Percentage of revenue retained as profit | (Profit ÷ Revenue) × 100 |
| **Return on Investment (ROI)** | Return from recycling infrastructure investments | (Gain − Cost) ÷ Cost × 100 |
| **Material Sales Revenue** | Revenue from recovered materials | $/month |
| **Maintenance Cost Ratio** | Maintenance expenses relative to operating costs | Maintenance Cost ÷ Total Operating Cost |
| **Budget Variance** | Difference between planned and actual expenses | Actual − Budget |
""")
st.markdown("""
**Financial Goals**
- Increase revenue from recyclable materials.
- Reduce processing costs.
- Improve profitability.
- Optimize capital investments.
""")

st.divider()

# ── 4. Workforce KPIs ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="border:1px solid #f0ddc0; border-left:6px solid #b45309;
            border-radius:12px; padding:24px 28px 8px; margin-bottom:24px;
            background:white">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px">
    <span style="font-size:30px; line-height:1">👷</span>
    <div>
      <span style="font-size:18px; font-weight:800; color:#1a1a18">4. Workforce KPIs</span>
      <br>
      <span style="font-size:12px; color:#555">
        Employee retention, safety incident rates, and workforce productivity
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Workforce KPIs measure employee productivity, safety, training, and engagement."
)
st.markdown("""
| KPI | Description | Formula / Measurement |
|-----|-------------|----------------------|
| **Employee Productivity** | Material processed per employee | Tons Processed ÷ Number of Employees |
| **Labor Utilization** | Percentage of available labor hours used productively | Productive Hours ÷ Available Hours × 100 |
| **Safety Incident Rate** | Number of workplace accidents | Incidents per 100 employees |
| **Lost Time Injury Frequency Rate (LTIFR)** | Injuries causing lost workdays | LTIs × 1,000,000 ÷ Hours Worked |
| **Employee Turnover Rate** | Percentage of employees leaving the organization | Departures ÷ Average Workforce × 100 |
| **Training Hours per Employee** | Average training received | Hours/employee/year |
| **Absenteeism Rate** | Percentage of missed workdays | Absent Days ÷ Total Workdays × 100 |
| **Employee Satisfaction Score** | Workforce engagement and satisfaction level | Survey score |
""")
st.markdown("""
**Workforce Goals**
- Improve employee productivity.
- Reduce workplace injuries.
- Increase training participation.
- Improve employee retention and satisfaction.
""")

st.divider()

# ── References ────────────────────────────────────────────────────────────────────
st.markdown("### References")
st.markdown("""
1. [United States Environmental Protection Agency (2025)](https://www.epa.gov/circulareconomy/national-recycling-goal-recycling-rate-measurement).
   *National Recycling Goal: Recycling Rate Measurement*. Retrieved from EPA website.

2. [Busch Systems Waste Diversion KPIs](https://www.buschsystems.com/waste-diversion-kpis/) (2025).
   *Measuring Waste Diversion Success: KPIs Every Sustainability Leader Should Track*.

3. [Willis Recycling Metrics Guide](https://www.willisrecycling.com/recycling-program-metrics-how-to-track/) (2026).
   *Recycling Program Metrics: Key KPIs and How to Track Them*.
""")

st.divider()

# ── KPI Framework & About (collapsed) ─────────────────────────────────────────────
with st.expander("📋 KPI Framework Reference", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**10 Core KPI Dimensions**")
        st.markdown("""
| # | KPI | Category | Target |
|---|-----|----------|--------|
| 1 | Material Recovery Rate | Operational | ≥ 86% |
| 2 | Processing Time / Batch | Operational | ≤ 4.0 h |
| 3 | Equipment Downtime | Operational | ≤ 5% |
| 4 | Workplace Safety Incidents | Workforce | ≤ 1.0/100 |
| 5 | Waste Diversion Rate | Environmental | ≥ 80% |
| 6 | Customer Satisfaction Score | Financial | ≥ 4.2/5 |
| 7 | Transportation Efficiency | Operational | ≥ 88% |
| 8 | Employee Turnover Rate | Workforce | ≤ 15% |
| 9 | Contamination Rate | Environmental | ≤ 6% |
| 10 | Energy Consumption | Environmental | ≤ 30 kWh/t |
""")
    with col_b:
        st.markdown("**Data Infrastructure**")
        st.markdown("""
- **Database**: SQLite (in-memory) populated from simulated NYS DEC data
- **20 Centers** across 5 regions: NYC Metro, Western NY, Central NY, Capital Region, North Country
- **4 Center Types**: Municipal, Commercial, Electronic (E-Waste), Hazardous
- **12 months** of monthly KPI records per center (240 rows)
- **Material streams**: Paper, Plastics, Glass, Metals, Electronics, Hazardous

**Technology Stack**

| Component | Technology |
|-----------|-----------|
| Web framework | Streamlit ≥ 1.35 |
| Visualizations | Plotly Express & Graph Objects |
| Interactive map | Folium + streamlit-folium |
| Data layer | SQLite (in-memory) via `sqlite3` |
| Data manipulation | Pandas, NumPy |
""")
        st.info("👈 Select any page from the sidebar to begin.", icon="ℹ️")

with st.expander("📄 About This Application", expanded=False):
    st.markdown("""
### Recycle Center KPIs — Summary

This application is a **demonstration prototype** of a data-driven Key Performance Indicator (KPI)
monitoring dashboard designed for a hypothetical network of recycling centers across New York State.
It was built as a proof-of-concept to illustrate how operational, environmental, financial, and
workforce performance data can be integrated into a single interactive platform using open-source
Python tools.

#### Purpose
The dashboard demonstrates how a state environmental agency — such as the NYS Department of
Environmental Conservation (DEC) — could track and visualize recycling center performance across
multiple regions and facility types. Every chart, metric, alert, and map marker in this application
is generated from **randomly simulated data** created at application startup.

#### Limitations & Disclaimer
- All KPI values, financial figures, geographic placements, and alert conditions are
  **entirely fictitious** and regenerated fresh on every application start.
- Center names, addresses, and coordinates are illustrative only and do not correspond to
  any licensed or operating recycling facility.
- This application is **not affiliated with, endorsed by, or representative of** the NYS DEC,
  any municipal government, or any recycling industry organization.

---
*Built as a Python / Streamlit data visualization demonstration · © 2026 Zia Ahmed, Upatta Analytics*
""")
