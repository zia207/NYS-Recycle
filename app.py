"""
NYS Recycling Center KPI Dashboard
Main entry point — home / introduction page
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data.sql_queries import q_latest_kpi, q_scorecard_summary, q_alerts

st.set_page_config(
    page_title="NYS Recycling Center KPI Dashboard",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    st.markdown("""
    **Navigation**
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
    st.caption("© 2025 NYS Recycling KPI Dashboard")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0d4d2c 0%,#1e7a49 60%,#3aaa6a 100%);
            border-radius:16px;padding:36px 40px;margin-bottom:24px;color:white">
  <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
    <span style="font-size:40px">♻️</span>
    <div>
      <h1 style="margin:0;font-size:26px;font-weight:700;color:white">
        NYS Recycling Center KPI Dashboard
      </h1>
      <p style="margin:4px 0 0;opacity:0.85;font-size:14px">
        New York State Department of Environmental Conservation · Operations Analytics
      </p>
    </div>
  </div>
  <p style="opacity:0.9;font-size:14px;max-width:700px;margin:0">
    A comprehensive KPI tracking and reporting framework for 20 recycling centers
    across NYS, powered by predefined SQL queries and live OpenStreetMap visualization.
    Monitor efficiency, sustainability, financial health, and workforce performance.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#fff8e6;border:1.5px solid #e09d20;border-left:5px solid #e09d20;
            border-radius:10px;padding:14px 20px;margin-bottom:20px;display:flex;
            align-items:flex-start;gap:12px">
  <span style="font-size:22px;flex-shrink:0">⚠️</span>
  <div>
    <span style="font-weight:700;font-size:13px;color:#a36b0b">DEMONSTRATION PURPOSE ONLY</span><br>
    <span style="font-size:12px;color:#5a4010;line-height:1.7">
      All data, center locations, KPI values, financial figures, and alert conditions
      displayed in this dashboard are <b>entirely simulated</b> and do not represent any
      real recycling facility, government agency, or operational program.
      This application is intended solely as a <b>technical demonstration</b> of a
      Streamlit-based KPI monitoring framework. It must not be used for operational
      decisions, regulatory reporting, policy analysis, or any other official purpose.
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── About this app ─────────────────────────────────────────────────────────────
with st.expander("📄 About This Application", expanded=True):
    st.markdown("""
    ### NYS Recycling Center KPI Dashboard — Summary

    This application is a **demonstration prototype** of a data-driven Key Performance
    Indicator (KPI) monitoring dashboard designed for a hypothetical network of recycling
    centers across New York State (NYS). It was built as a proof-of-concept to illustrate
    how operational, environmental, financial, and workforce performance data can be
    integrated into a single interactive platform using open-source Python tools.

    #### Purpose
    The dashboard demonstrates how a state environmental agency — such as the NYS
    Department of Environmental Conservation (DEC) — could track and visualize recycling
    center performance across multiple regions and facility types. Every chart, metric,
    alert, and map marker in this application is generated from **randomly simulated data**
    created at application startup. No real facility data has been used.

    #### What It Shows
    - **20 simulated recycling centers** spread across 5 NYS regions
      (NYC Metro, Western NY, Central NY, Capital Region, North Country)
    - **4 center types**: Municipal, Commercial, Electronic (E-Waste), and Hazardous
    - **10 KPI dimensions** covering operational efficiency, environmental impact,
      financial sustainability, and workforce health
    - **12 months** of monthly KPI records per center (240 rows total)
    - An **interactive OpenStreetMap** showing center locations with hover and
      click-through KPI popups
    - A **SQL query library** with 13 pre-defined analytical queries and a live
      custom query builder against the in-memory database

    #### Technology Stack
    | Component | Technology |
    |-----------|-----------|
    | Web framework | Streamlit ≥ 1.35 |
    | Data layer | SQLite (in-memory) via Python `sqlite3` |
    | Visualizations | Plotly Express & Graph Objects |
    | Interactive map | Folium + streamlit-folium (OpenStreetMap tiles) |
    | Data manipulation | Pandas, NumPy |

    #### Limitations & Disclaimer
    - All KPI values, financial figures, geographic placements, and alert conditions
      are **entirely fictitious** and regenerated fresh on every application start.
    - Center names, addresses, and coordinates are illustrative only and do not
      correspond to any licensed or operating recycling facility.
    - The SQL queries shown are designed for educational purposes against the simulated
      schema and are not validated against any production database system.
    - This application is **not affiliated with, endorsed by, or representative of**
      the NYS DEC, any municipal government, or any recycling industry organization.

    ---
    *Built as a Python / Streamlit data visualization demonstration · 2025*
    """)

# ── State at a glance ──────────────────────────────────────────────────────────
df    = q_latest_kpi()
score = q_scorecard_summary().iloc[0]
alerts= q_alerts()

crit_n = len(alerts[alerts["level"]=="critical"])
warn_n = len(alerts[alerts["level"]=="warning"])

st.markdown("### State at a Glance — Latest Reporting Month")
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
c1.metric("Centers",    f"{len(df)}",                  "Statewide")
c2.metric("Avg MRR",    f"{score.avg_mrr:.1f}%",       "Target 86%")
c3.metric("Avg WDR",    f"{score.avg_wdr:.1f}%",       "Target 80%")
c4.metric("Avg CSS",    f"{score.avg_css:.2f}",        "Target 4.2")
c5.metric("Downtime",   f"{score.avg_downtime:.1f}%",  "Target ≤5%")
c6.metric("Contam.",    f"{score.avg_contam:.1f}%",    "Target ≤6%")
c7.metric("🔴 Critical",f"{crit_n}",                  "alerts")
c8.metric("🟡 Warnings",f"{warn_n}",                  "alerts")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE DASHBOARD SECTIONS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Dashboard Sections")
st.caption("Click **▶ Expand** on any section card to read a full description of its KPIs, "
           "charts, and how to use it.")

# ── Section definitions ────────────────────────────────────────────────────────
SECTIONS = [

    dict(
        icon="📊", title="Executive Summary", color="#1e7a49",
        tagline="Statewide one-page KPI overview with live metric cards and trend charts.",
        features=["7 live KPI cards", "MRR trend by type", "Tonnage bar chart",
                  "CSS rolling 12-month", "Top 10 centers table"],
        overview=(
            "The Executive Summary is the dashboard's landing KPI page. It aggregates "
            "performance data from all 20 recycling centers into a single view, "
            "giving managers an immediate pulse on the state of the network. "
            "Seven headline metric cards show the current statewide averages for MRR, "
            "WDR, CSS, downtime, contamination, transportation efficiency, and monthly "
            "revenue — each with a target delta indicator (green = on target, red = below). "
            "Five supporting charts break performance down over the 12-month period and "
            "across center types and regions."
        ),
        kpis=[
            ("♻️ Material Recovery Rate (MRR)",
             "Target ≥ 86%",
             "Percentage of incoming waste successfully recovered as usable material. "
             "The primary operational success metric. Values below 80% signal process "
             "inefficiency or high contamination and trigger NYS DEC review."),
            ("🌎 Waste Diversion Rate (WDR)",
             "Target ≥ 80%",
             "Share of received waste redirected away from landfill via recycling, "
             "composting, or energy recovery. Key metric for NYS Climate Act (CLCPA) "
             "compliance. Each ton diverted avoids ~0.5 metric tons CO₂-equivalent."),
            ("⭐ Customer Satisfaction Score (CSS)",
             "Target ≥ 4.2 / 5.0",
             "Rolling 90-day average survey score from drop-off customers, commercial "
             "haulers, and municipal program participants. A 0.3-point CSS decline "
             "correlates with a 4–8% drop in voluntary participation rates."),
            ("🔧 Equipment Downtime",
             "Target ≤ 5% of scheduled hours",
             "Unplanned downtime as a share of planned production time. Values above 7% "
             "trigger operational review. Every 1% increase costs ~$18–22K/month in "
             "lost capacity and overtime recovery."),
            ("⚠️ Contamination Rate",
             "Target ≤ 6% overall",
             "Percentage of each material stream containing non-target materials. "
             "Paper contamination above 8% causes market rejection. A 1% increase in "
             "plastic stream contamination reduces commodity value by $8–12/ton."),
        ],
        charts_desc=(
            "**MRR Trend by Center Type** — Line chart showing 12-month MRR evolution "
            "for Municipal, Commercial, Electronic, and Hazardous centers, revealing "
            "seasonal patterns and type-specific improvement trajectories.\n\n"
            "**Total Tonnage Processed** — Grouped bar chart of monthly processed vs. "
            "diverted tonnage statewide, illustrating the growing diversion gap.\n\n"
            "**Contamination by Region** — Color-gradient bar chart (green→red) enabling "
            "rapid regional comparison.\n\n"
            "**Downtime by Cause** — Donut chart breaking downtime into Scheduled "
            "Maintenance, Mechanical Failure, Power Outage, Operator Error, and Other.\n\n"
            "**CSS Rolling Trend** — 12-month area line chart with 4.2 target reference line."
        ),
    ),

    dict(
        icon="🗺️", title="Interactive Map", color="#1d9e75",
        tagline="Live OpenStreetMap with all 20 centers, color-coded KPI markers and drill-down popups.",
        features=["OSM tile basemap", "Color-coded by any KPI", "Full KPI popup on click",
                  "Hover tooltip", "Per-center 12-month trend"],
        overview=(
            "The Interactive Map page renders all 20 simulated NYS recycling centers "
            "as colored circle markers on a live OpenStreetMap basemap, using the "
            "Folium library via streamlit-folium. Marker fill color encodes the currently "
            "selected KPI metric on a continuous green→red gradient scale. Marker size "
            "encodes the composite performance score tier. The map supports full zoom, "
            "pan, and tile switching. A metric selector dropdown lets users instantly "
            "re-color all markers to show MRR, WDR, contamination, CSS, downtime, "
            "transport efficiency, turnover, or energy intensity."
        ),
        kpis=[
            ("📍 Composite KPI Score",
             "Weighted formula: MRR×30% + WDR×20% + Contamination×15% + CSS×20% + TE×15%",
             "A single 0–100 score synthesizing five KPI dimensions into one number "
             "for map-level ranking. Score ≥ 85 = Excellent (large dark marker), "
             "75–84 = Good, 65–74 = Fair, < 65 = Needs Attention (small red marker)."),
            ("🌈 Any KPI as map metric",
             "Switchable via the 'Map Metric' dropdown",
             "Users can re-color markers to display: MRR %, WDR %, Contamination %, "
             "CSS /5, Equipment Downtime %, Transportation Efficiency %, Employee "
             "Turnover %, or Energy kWh/ton — enabling spatial pattern detection."),
            ("🔍 Popup KPI snapshot",
             "All 12 KPI fields on click",
             "Clicking any marker opens a styled popup card showing center name, city, "
             "type, region, all 10 KPIs, revenue, and a 'View Full KPI Detail' button "
             "that loads the 12-month trend and radar comparison chart below the map."),
        ],
        charts_desc=(
            "**OSM Tile Map** — Full-resolution OpenStreetMap base layer covering all of "
            "New York State, from NYC to the Canadian border.\n\n"
            "**KPI Trend Chart** — Selecting a center loads a 12-month line chart for the "
            "chosen KPI, overlaid with the statewide average as a dashed reference.\n\n"
            "**Optional Mini-Map** — A collapsible inset overview map for spatial context.\n\n"
            "**Marker Cluster Toggle** — Groups overlapping markers in dense areas (NYC Metro) "
            "for cleaner navigation at low zoom levels."
        ),
    ),

    dict(
        icon="⚙️", title="Operational KPIs", color="#3a8ee0",
        tagline="Processing efficiency, equipment reliability, and transportation performance.",
        features=["PTB line + violin", "Downtime box plots", "TE trend with CI band",
                  "Center operational table", "Inline SQL panel"],
        overview=(
            "Operational KPIs measure the day-to-day throughput and reliability of each "
            "recycling center. Four key metrics are tracked: Processing Time per Batch (PTB), "
            "Equipment Downtime Rate, and Transportation Efficiency. This page provides "
            "both monthly trend views (how performance is changing) and distribution views "
            "(how centers compare within each type). The center-level table allows ranking "
            "and sorting across all operational metrics simultaneously."
        ),
        kpis=[
            ("⏱️ Processing Time per Batch (PTB)",
             "Target ≤ 4.0 h (Municipal/Commercial)",
             "Time from batch intake to sorted output. Shorter PTB = higher throughput. "
             "A center processing at 4 h vs 6 h has 33% more daily capacity. "
             "Targets vary: Electronic ≤ 5.5 h, Hazardous ≤ 7.0 h due to process complexity."),
            ("🔧 Equipment Downtime Rate",
             "Target ≤ 5% of scheduled hours",
             "Unplanned hours lost to failure as % of planned operation. Causes: Mechanical "
             "failure (28%), Scheduled maintenance (42%), Power outages (12%), Operator "
             "error (10%). Above 8% triggers mandatory DEC operational review."),
            ("🚛 Transportation Efficiency (TE)",
             "Target ≥ 88% load efficiency",
             "Average vehicle payload as % of rated capacity across all trips. Below 80% "
             "indicates route planning inefficiencies. Transportation is 18–25% of total "
             "operating costs; a 10% TE improvement saves $40–80K/year per center."),
        ],
        charts_desc=(
            "**PTB by Center Type** — 12-month multi-line chart comparing average "
            "processing time per batch across all four center types with target reference.\n\n"
            "**PTB Distribution (Violin)** — Violin chart showing the full distribution "
            "of PTB values per type, revealing outlier batches and variance.\n\n"
            "**TE Trend with Confidence Band** — Monthly TE trend with shaded min/max "
            "envelope showing the performance range across all centers.\n\n"
            "**Downtime Box Plots** — Box-and-whisker plot per center type with all "
            "monthly data points overlaid, showing median, IQR, and outliers.\n\n"
            "**Center Operational Table** — Color-gradient table sortable by PTB, "
            "downtime, TE, and tons processed."
        ),
    ),

    dict(
        icon="🌿", title="Environmental KPIs", color="#0f6e56",
        tagline="Waste diversion, contamination by material stream, and energy consumption.",
        features=["WDR by region (line)", "Energy kWh/ton by type", "Stream contamination bars",
                  "MRR vs Energy scatter", "Contamination by type heatmap"],
        overview=(
            "Environmental KPIs capture the ecological performance of recycling operations — "
            "how much waste is kept out of landfills, how clean the recovered material streams "
            "are, and how energy-efficiently the centers operate. The page enables both "
            "regional comparison (which areas are meeting diversion targets?) and stream-level "
            "diagnosis (which material types carry the highest contamination risk?)."
        ),
        kpis=[
            ("🌎 Waste Diversion Rate (WDR)",
             "Target ≥ 80% (NYS CLCPA alignment)",
             "Proportion of incoming waste redirected from landfill through recycling, "
             "composting, or energy recovery. Regional variation is significant: NYC Metro "
             "achieves 82–88% while North Country centers average 70–76% due to rural "
             "contamination challenges."),
            ("⚠️ Contamination Rate by Stream",
             "Target ≤ 6% overall; ≤ 3% for Paper/Metal",
             "Contamination tracked per material stream (Paper, Plastics, Glass, Metals, "
             "Electronics, Hazardous). Paper >8% causes end-market rejection. Plastics >10% "
             "fails MRF grade. A 1% plastic contamination increase reduces commodity "
             "value by $8–12/ton and raises reprocessing costs."),
            ("⚡ Energy Consumption per Ton",
             "Target ≤ 30 kWh/ton (Municipal/Commercial)",
             "Electrical energy to process one metric ton of material. Municipal MRFs "
             "with modern optical sorters achieve 24–30 kWh/ton. E-waste centers require "
             "38–50 kWh/ton; hazardous centers 50–60 kWh/ton. Reducing 5 kWh/ton across "
             "all centers saves ~$212,500/year at NYS commercial rates."),
        ],
        charts_desc=(
            "**WDR by Region** — 12-month multi-line chart per region with 80% target line, "
            "revealing which regions are improving vs. plateauing.\n\n"
            "**Energy by Center Type** — 12-month line chart comparing kWh/ton across "
            "all four types with 30 kWh/t target line.\n\n"
            "**Contamination by Stream & Region** — Grouped horizontal bar chart with "
            "stream as Y-axis and region as color groups, sortable by contamination level.\n\n"
            "**Contamination by Stream & Type** — Grouped bar chart showing which center "
            "types struggle most with each material stream.\n\n"
            "**MRR vs Energy Scatter** — Bubble chart per center where bubble size = "
            "composite score, revealing the efficiency frontier (high MRR, low energy)."
        ),
    ),

    dict(
        icon="💰", title="Financial KPIs", color="#8b5cf6",
        tagline="Revenue, operating costs, margins, cost per ton, and customer satisfaction.",
        features=["Revenue vs Opex dual-axis", "Net margin % trend", "Cost/ton by type",
                  "Revenue pie by region", "Center financial table"],
        overview=(
            "Financial KPIs track the economic sustainability of recycling operations. "
            "Revenue comes from three sources: tipping fees, commodity material sales, "
            "and government program grants. The page provides monthly aggregate trends, "
            "type-level cost benchmarking, and regional revenue distribution, enabling "
            "budget planners and program managers to spot deteriorating margins early "
            "and benchmark cost efficiency across facility types."
        ),
        kpis=[
            ("💵 Revenue & Net Operating Margin",
             "Margin % ≥ 20%; Revenue growth ≥ 3% YoY",
             "Revenue sources: tipping fees (55%), commodity sales (30%), grants (15%). "
             "Costs: labor (55%), maintenance (20%), transportation (18%), utilities (7%). "
             "Municipal centers often operate at 10–18% margins as they cross-subsidize "
             "residential service. Negative margins for 2+ quarters trigger subsidy review."),
            ("🏷️ Cost per Ton Processed",
             "≤ $55/ton (Municipal); ≤ $140/ton (Hazardous)",
             "Total operating expenditure divided by tons processed. The primary "
             "efficiency benchmark for cross-center comparison. Hazardous centers are "
             "2–3× more expensive than municipal due to regulatory compliance and "
             "specialized containment. A $5/ton improvement across all centers saves "
             "~$425K/year statewide."),
            ("⭐ Customer Satisfaction Score (CSS)",
             "Target ≥ 4.2 / 5.0",
             "Post-service survey covering drop-off experience (25%), staff helpfulness "
             "(20%), cleanliness (20%), wait time (20%), and information clarity (15%). "
             "Scores below 3.8 indicate service quality concerns increasing program "
             "abandonment risk. CSS is a leading indicator of tipping fee revenue."),
        ],
        charts_desc=(
            "**Revenue vs Opex** — Grouped bar chart with net margin overlaid on a "
            "secondary axis, showing the monthly revenue/cost gap over 12 months.\n\n"
            "**Net Margin %** — Area line chart with 20% target reference line, "
            "highlighting months where margins compress below target.\n\n"
            "**Cost per Ton by Type** — Horizontal bar chart with labeled values, "
            "clearly showing the 3× cost difference between Hazardous and Municipal.\n\n"
            "**Revenue by Region (Pie)** — Donut chart of latest-month revenue "
            "distribution across the five NYS regions.\n\n"
            "**Center Financial Table** — Color-gradient table sortable by margin %, "
            "revenue, opex, net margin, and tons processed."
        ),
    ),

    dict(
        icon="👷", title="Workforce KPIs", color="#a36b0b",
        tagline="Employee retention, safety incident rates, and workforce stability.",
        features=["ETR trend by region", "WSI safety incidents", "Box plot distributions",
                  "WSI vs ETR scatter", "Safety compliance table"],
        overview=(
            "Workforce KPIs measure the human capital health of recycling operations. "
            "These are leading indicators of operational quality: high turnover and "
            "elevated safety incidents predictably precede process degradation, MRR "
            "decline, and increased contamination. The page tracks both Employee Turnover "
            "Rate (ETR) and Workplace Safety Incidents (WSI) at regional and center level, "
            "with compliance classification against OSHA industry benchmarks."
        ),
        kpis=[
            ("🔄 Employee Turnover Rate (ETR)",
             "Target ≤ 15% annualized",
             "Voluntary and involuntary separations as % of average headcount. "
             "Industry average is 18–22% nationally. Experienced sorters take 3–4 months "
             "to reach full productivity — high turnover directly degrades MRR and "
             "contamination rates. Replacing one trained sorter costs $4,500–7,000. "
             "North Country centers face structural headwinds from thin labor markets."),
            ("🦺 Workplace Safety Incidents (WSI)",
             "Target ≤ 1.0 per 100 employees (OSHA benchmark)",
             "OSHA-recordable injuries and illnesses per 100 FTE employees. Main causes: "
             "sorting equipment lacerations, musculoskeletal strain, forklift incidents, "
             "chemical exposure (hazardous centers). Centers above 1.5 WSI/100 trigger "
             "mandatory DEC safety review; above 2.5 can result in permit conditions. "
             "Each recordable incident costs $35,000–85,000 in direct and indirect costs."),
        ],
        charts_desc=(
            "**ETR by Region** — 12-month multi-line chart with 15% target reference, "
            "revealing which regions are improving retention vs. experiencing turnover spikes.\n\n"
            "**WSI by Region** — 12-month multi-line chart with ≤1.0/100 OSHA target "
            "line, showing safety incident trends over the reporting year.\n\n"
            "**ETR Box Plots by Type** — Box-and-whisker chart per center type, showing "
            "turnover distribution with 15% target reference line.\n\n"
            "**WSI vs ETR Scatter** — Bubble scatter where bubble size = composite "
            "score, revealing the correlation between high turnover and safety incidents.\n\n"
            "**Workforce Compliance Table** — Color-gradient table with auto-assigned "
            "safety status (✅ Compliant / ⚠️ Watch / 🔴 Non-Compliant)."
        ),
    ),

    dict(
        icon="📋", title="KPI Scorecard", color="#0d4d2c",
        tagline="10-dimension progress bars, statewide radar, and per-center comparison heatmap.",
        features=["10 KPI progress bars", "Statewide vs target radar", "Per-center radar",
                  "KPI comparison heatmap", "Statewide vs Per-center toggle"],
        overview=(
            "The KPI Scorecard translates all 10 KPI dimensions into a unified "
            "performance-against-target view, enabling both high-level executive reporting "
            "and granular per-center comparison. Each KPI is normalized to a 0–100% "
            "scale where 100% = meeting the target exactly, and values above 100% indicate "
            "exceeding the target. Two view modes are available via a radio toggle: "
            "Statewide Summary (aggregate averages vs. targets) and Per-Center Comparison "
            "(side-by-side radar charts for up to 4 selected centers)."
        ),
        kpis=[
            ("📊 All 10 KPI Dimensions scored",
             "Normalized 0–100% scale per KPI",
             "MRR, WDR, PTB, Downtime, WSI, CSS, TE, ETR, Contamination, Energy — each "
             "converted to a directional percentage-of-target score. Lower-is-better KPIs "
             "(downtime, contamination, turnover, energy) are inverted so that 100% always "
             "means 'meeting target'. Color coding: 🟢 ≥90%, 🟡 70–89%, 🔴 <70%."),
            ("🕸️ Radar Chart",
             "Statewide Avg vs Target / Per-Center Comparison",
             "Spider/radar chart with 10 axes, one per KPI dimension. The statewide "
             "polygon is filled in green; the target polygon in blue dashed lines. "
             "Per-center mode overlays up to 4 center polygons for direct comparison, "
             "making performance gaps immediately visible."),
            ("🌡️ KPI Heatmap",
             "Available in Per-Center mode",
             "Color grid (red→green) with centers as rows and KPI dimensions as columns. "
             "Enables pattern detection across many centers simultaneously — for example, "
             "identifying centers that are strong on environmental KPIs but weak on "
             "workforce metrics."),
        ],
        charts_desc=(
            "**Progress Bars** — 10 HTML-rendered progress bars in a 2-column grid, "
            "each showing value, unit, target, direction, and % of target achieved. "
            "Color transitions green→amber→red as performance drops.\n\n"
            "**Statewide Radar** — Scatterpolar chart comparing the statewide average "
            "polygon to the target (all-100%) polygon across all 10 dimensions.\n\n"
            "**Per-Center Radar** — Overlay of up to 4 user-selected center polygons "
            "plus a dotted target ring for benchmarking.\n\n"
            "**Heatmap** — Plotly imshow heatmap on a RdYlGn scale, zmin=50, zmax=110."
        ),
    ),

    dict(
        icon="🔔", title="Alerts & Escalation", color="#d94a4a",
        tagline="Automated threshold monitoring with critical/warning/ok classification and escalation protocol.",
        features=["Alert severity cards", "Threshold definition table", "Escalation protocol",
                  "Live KPI breach check", "Filter by severity level"],
        overview=(
            "The Alerts page provides an automated threshold monitoring system that "
            "evaluates each center's latest KPI values against 8 pre-defined breach "
            "rules and classifies results as Critical, Warning, or OK. Alerts are "
            "displayed as color-coded cards with center name, KPI affected, breach "
            "message, actual value, threshold value, and date. A Live KPI Threshold Check "
            "section re-evaluates all centers in real time and surfaces every active breach "
            "in a sortable table with composite score context."
        ),
        kpis=[
            ("🔴 Critical Alerts",
             "Hard regulatory or operational safety breach — respond within 24 hours",
             "Triggered when: MRR < 78%, Contamination > 8%, Downtime > 7%, "
             "Safety incidents > 1.5/100, or Turnover > 20%. Generates automatic "
             "notification to Regional DEC Solid Waste Manager. A corrective action "
             "plan (CAP) is required within 72 hours of the alert date."),
            ("🟡 Warning Alerts",
             "KPI approaching limit or sustained below target ≥ 2 months — respond within 5 days",
             "Triggered when: MRR < 83%, WDR < 77%, Contamination > 7%, Downtime > 6%, "
             "CSS < 4.0, TE < 82%. Two consecutive warning months for the same KPI "
             "automatically escalate to Critical. Generates weekly digest to facility "
             "operations managers."),
            ("🟢 OK Notifications",
             "All monitored KPIs meeting or exceeding targets — monthly review",
             "Centers meeting all 8 monitored thresholds receive an OK classification. "
             "These are compiled into the monthly performance scorecard distributed to "
             "the NYS DEC Commissioner's office. Used for recognition programs and "
             "best-practice identification."),
        ],
        charts_desc=(
            "**Alert Summary Badges** — Three large count cards (Critical / Warning / OK) "
            "at the top of the page for immediate situational awareness.\n\n"
            "**Alert Detail Cards** — Styled bordered cards per alert with severity color, "
            "center name, KPI badge, breach message, value, threshold, and date.\n\n"
            "**Escalation Protocol Table** — Expandable section defining thresholds, "
            "response timelines, and escalation actions for all 8 monitored KPIs.\n\n"
            "**Live Threshold Check** — Real-time evaluation of all centers against all "
            "8 rules, displayed as a sortable color-gradient table with composite scores."
        ),
    ),

    dict(
        icon="📄", title="SQL Query Library", color="#555551",
        tagline="13 pre-defined KPI queries + a full custom SQL builder with chart output and CSV/JSON export.",
        features=["13 named queries", "8 starter templates", "Auto-chart builder",
                  "CSV + JSON download", "Schema browser", "Execution timing"],
        overview=(
            "The SQL Queries page gives analysts direct access to the underlying "
            "SQLite database through two interfaces: a pre-defined library of 13 "
            "named queries covering every KPI dimension, and a full custom query "
            "builder with 8 starter templates, an interactive chart generator, and "
            "result export to CSV and JSON. All queries run live against the in-memory "
            "database and return results in seconds. A schema browser shows table "
            "structures, column types, row counts, and numeric summaries."
        ),
        kpis=[
            ("📚 Pre-defined Query Library",
             "13 queries across 7 categories",
             "Categories: Operational (MRR, PTB, Downtime), Environmental (WDR, "
             "Contamination, Energy), Financial (Revenue, CSS), Workforce (ETR, WSI), "
             "Geo/Map (Composite Score), Scorecard (Full 10-KPI report), "
             "Alerts (Threshold violation UNION). Each query includes a quick "
             "auto-chart and CSV + JSON download."),
            ("⌨️ Custom Query Builder",
             "Full SELECT support against 4 tables",
             "Write any SELECT statement against: `centers`, `monthly_kpi`, "
             "`material_streams`, `alerts`. 8 pre-loaded starter templates include: "
             "top-5 centers by MRR, contamination outliers, region revenue trend, "
             "side-by-side center comparison, all-targets-met filter, "
             "month-over-month change, material stream summary, and type averages."),
            ("📊 Auto-chart Generator",
             "Bar / Line / Scatter / Pie / Histogram",
             "After running any query, the auto-chart option builds a configurable "
             "Plotly chart from the result set. Users select chart type, X axis column, "
             "Y axis column, and optional color grouping. Execution timing is shown "
             "in milliseconds. Results can be downloaded as CSV or JSON."),
        ],
        charts_desc=(
            "**Pre-defined Query Cards** — Collapsible expanders per query showing the "
            "full SQL, a Run button, result table, auto-chart, and download buttons.\n\n"
            "**Custom SQL Editor** — Multi-line text area with template loader dropdown "
            "and 'Load ↓' button, row limit slider (10–500), auto-chart toggle, and "
            "column type display option.\n\n"
            "**Schema Browser** — Side-by-side table preview (20 rows) and column "
            "definition table (name, type, not-null, PK), plus an expandable "
            "numeric summary (describe()) for each table."
        ),
    ),
]

# ── Render interactive section cards ──────────────────────────────────────────
# Session state: track which section is expanded
if "expanded_section" not in st.session_state:
    st.session_state.expanded_section = None

# Top 3-column grid of summary cards + expand buttons
cols_top = st.columns(3)
for i, sec in enumerate(SECTIONS):
    with cols_top[i % 3]:
        # Card header (static HTML)
        st.markdown(f"""
<div style="background:white;border:1px solid #e4e4e0;
            border-top:4px solid {sec['color']};
            border-radius:12px;padding:16px 18px 10px;margin-bottom:4px">
  <div style="font-size:22px;margin-bottom:6px">{sec['icon']}</div>
  <div style="font-weight:700;font-size:14px;color:#1a1a18;margin-bottom:5px">{sec['title']}</div>
  <div style="font-size:12px;color:#555;line-height:1.55;margin-bottom:10px">{sec['tagline']}</div>
  <div style="font-size:10px;color:{sec['color']};line-height:1.8">
    {'&nbsp;&nbsp;·&nbsp;&nbsp;'.join(f'<b>{f}</b>' for f in sec['features'])}
  </div>
</div>""", unsafe_allow_html=True)

        # Expand / collapse toggle button
        key = f"btn_{sec['title'].replace(' ','_')}"
        is_open = st.session_state.expanded_section == sec["title"]
        btn_label = "▼ Collapse" if is_open else "▶ Expand details"
        btn_type  = "secondary"
        if st.button(btn_label, key=key, use_container_width=True, type=btn_type):
            st.session_state.expanded_section = (
                None if is_open else sec["title"])
            st.rerun()

# ── Full-width detail panel for the expanded section ─────────────────────────
expanded = next(
    (s for s in SECTIONS if s["title"] == st.session_state.expanded_section),
    None)

if expanded:
    st.markdown(f"""
<div style="background:#f9faf8;border:1.5px solid {expanded['color']};
            border-radius:14px;padding:22px 28px;margin:8px 0 20px">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <span style="font-size:32px">{expanded['icon']}</span>
    <div>
      <div style="font-size:18px;font-weight:700;color:#1a1a18">{expanded['title']}</div>
      <div style="font-size:12px;color:#666;margin-top:2px">{expanded['tagline']}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    det_col1, det_col2 = st.columns([3, 2])

    with det_col1:
        st.markdown("#### 📖 Overview")
        st.markdown(
            f'<div style="font-size:13px;color:#333;line-height:1.75;'
            f'background:white;border-radius:8px;padding:14px 16px;'
            f'border:1px solid #e4e4e0">{expanded["overview"]}</div>',
            unsafe_allow_html=True)

        st.markdown("#### 📊 Charts & Visualizations")
        for line in expanded["charts_desc"].strip().split("\n\n"):
            if line.startswith("**"):
                bold_end = line.index("**", 2)
                title_txt = line[2:bold_end]
                rest_txt  = line[bold_end+2:].lstrip(" —")
                st.markdown(
                    f'<div style="background:white;border-left:3px solid {expanded["color"]};'
                    f'border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:8px;'
                    f'border:1px solid #e4e4e0;border-left:3px solid {expanded["color"]}">'
                    f'<span style="font-weight:600;font-size:12px;color:#1a1a18">{title_txt}</span>'
                    f'<br><span style="font-size:12px;color:#555;line-height:1.6">{rest_txt}</span>'
                    f'</div>',
                    unsafe_allow_html=True)

    with det_col2:
        st.markdown("#### 🎯 KPI Details")
        for kpi_name, kpi_target, kpi_desc in expanded["kpis"]:
            st.markdown(
                f'<div style="background:white;border:1px solid #e4e4e0;'
                f'border-left:4px solid {expanded["color"]};'
                f'border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:10px">'
                f'<div style="font-weight:600;font-size:12px;color:#1a1a18;margin-bottom:3px">'
                f'{kpi_name}</div>'
                f'<div style="font-size:10px;font-weight:600;color:{expanded["color"]};'
                f'background:{expanded["color"]}18;padding:2px 8px;border-radius:10px;'
                f'display:inline-block;margin-bottom:6px">{kpi_target}</div>'
                f'<div style="font-size:11px;color:#444;line-height:1.65">{kpi_desc}</div>'
                f'</div>',
                unsafe_allow_html=True)

    # Feature chips row
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:4px">'
        + "".join(
            f'<span style="background:{expanded["color"]}18;color:{expanded["color"]};'
            f'padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">{f}</span>'
            for f in expanded["features"])
        + "</div>",
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

st.divider()

# ── Framework summary (mirrors OALTC structure) ────────────────────────────────
st.markdown("### KPI Framework")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    **10 Core KPI Dimensions**

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
    st.markdown("""
    **Data Infrastructure**

    - **Database**: SQLite (in-memory) populated from simulated NYS DEC data
    - **20 Centers**: Across 5 regions — NYC Metro, Western NY, Central NY, Capital Region, North Country
    - **4 Center Types**: Municipal, Commercial, Electronic (E-Waste), Hazardous
    - **12 months** of monthly KPI records per center
    - **Material streams**: Paper, Plastics, Glass, Metals, Electronics, Hazardous

    **Tech Stack**
    - Streamlit · Plotly · Folium · SQLite · Pandas
    - OpenStreetMap tiles via Leaflet (streamlit-folium)
    - SQL KPI calculation pipeline
    """)
    st.info("👈 Use the sidebar to navigate to any dashboard section.")
