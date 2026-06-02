"""pages/01_Executive_Summary.py — Enhanced with full KPI descriptions, scorecard & alerts."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_queries import (
    q_latest_kpi, q_monthly_statewide, q_monthly_by_type,
    q_financial_monthly, q_scorecard_summary, q_alerts
)

st.set_page_config(page_title="Executive Summary · NYS Recycling KPI", layout="wide")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    center_type = st.selectbox("Center Type",
        ["All", "Municipal", "Commercial", "Electronic", "Hazardous"])
    region = st.selectbox("Region",
        ["All", "NYC Metro", "Western NY", "Central NY", "Capital Region", "North Country"])
    st.divider()
    st.caption("Data refreshed: Jan 2025")
    st.caption("Source: NYS DEC (simulated)")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("## 📊 Executive Summary")
st.caption("Statewide KPI snapshot · All 20 NYS recycling centers · Latest reporting month")

# ── Load data ──────────────────────────────────────────────────────────────────
df    = q_latest_kpi(center_type, region)
score = q_scorecard_summary(center_type, region).iloc[0]
fin   = q_financial_monthly(center_type, region)
mrr_t = q_monthly_by_type("mrr")
alerts_df = q_alerts()

if df.empty:
    st.warning("No centers match the selected filters.")
    st.stop()

# ── KPI metric cards ───────────────────────────────────────────────────────────
def delta_color(v, target, lower_better=False):
    good = (v <= target) if lower_better else (v >= target)
    return "normal" if good else "inverse"

c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
c1.metric("Avg MRR",       f"{score.avg_mrr:.1f}%",      "Target 86%",
          delta_color=delta_color(score.avg_mrr, 86))
c2.metric("Avg WDR",       f"{score.avg_wdr:.1f}%",      "Target 80%",
          delta_color=delta_color(score.avg_wdr, 80))
c3.metric("Avg CSS",       f"{score.avg_css:.2f}/5",     "Target 4.2",
          delta_color=delta_color(score.avg_css, 4.2))
c4.metric("Downtime",      f"{score.avg_downtime:.1f}%", "Target ≤5%",
          delta_color=delta_color(score.avg_downtime, 5, True))
c5.metric("Contamination", f"{score.avg_contam:.1f}%",   "Target ≤6%",
          delta_color=delta_color(score.avg_contam, 6, True))
c6.metric("Trans. Eff.",   f"{score.avg_te:.1f}%",       "Target 88%",
          delta_color=delta_color(score.avg_te, 88))
total_rev = fin["total_revenue"].iloc[-1] if not fin.empty else 0
c7.metric("Revenue ($K)",  f"${total_rev:,.0f}K",        "+4.2% MoM")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Material Recovery Rate by Center Type")
    fig = px.line(
        mrr_t, x="report_month", y="avg_val", color="center_type",
        labels={"report_month": "Month", "avg_val": "MRR (%)", "center_type": "Type"},
        color_discrete_map={"Municipal": "#1e7a49", "Commercial": "#3a8ee0",
                            "Electronic": "#e09d20", "Hazardous": "#d94a4a"},
        markers=True)
    fig.update_layout(height=300, margin=dict(t=10, b=0),
                      yaxis=dict(range=[60, 100]), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Total Tonnage Processed (Monthly)")
    ton_d  = q_monthly_statewide("tons_processed")
    ton_d2 = q_monthly_statewide("tons_diverted")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Processed", x=ton_d["report_month"],
                          y=ton_d["avg_val"]*20, marker_color="#1e7a49", opacity=0.85))
    fig2.add_trace(go.Bar(name="Diverted",  x=ton_d2["report_month"],
                          y=ton_d2["avg_val"]*20, marker_color="#9fe1cb", opacity=0.85))
    fig2.update_layout(height=300, margin=dict(t=10, b=0), barmode="group",
                       yaxis_title="Tons", xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4, col5 = st.columns(3)
with col3:
    st.markdown("#### Contamination by Region")
    regions = df.groupby("region")["contam"].mean().reset_index()
    fig3 = px.bar(regions, x="region", y="contam",
                  color="contam",
                  color_continuous_scale=["#1e7a49", "#f5c842", "#d94a4a"],
                  labels={"contam": "Contamination (%)", "region": "Region"})
    fig3.update_layout(height=280, margin=dict(t=10, b=0),
                       showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Downtime by Cause")
    causes = pd.DataFrame({
        "Cause": ["Scheduled Maint.", "Mechanical Failure",
                  "Power Outage", "Operator Error", "Other"],
        "Pct": [42, 28, 12, 10, 8]})
    fig4 = px.pie(causes, names="Cause", values="Pct", hole=0.55,
                  color_discrete_sequence=["#1e7a49","#3a8ee0","#e09d20","#d94a4a","#8c8c88"])
    fig4.update_layout(height=280, margin=dict(t=10, b=0),
                       legend=dict(font_size=10))
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.markdown("#### Customer Satisfaction (12-month)")
    css_t = q_monthly_statewide("css")
    fig5 = px.line(css_t, x="report_month", y="avg_val",
                   labels={"report_month": "Month", "avg_val": "CSS"},
                   color_discrete_sequence=["#3a8ee0"])
    fig5.add_hline(y=4.2, line_dash="dash", line_color="#d94a4a",
                   annotation_text="Target 4.2")
    fig5.update_layout(height=280, margin=dict(t=10, b=0),
                       yaxis=dict(range=[3.0, 5.0]), xaxis_title="")
    fig5.update_traces(fill="tozeroy", fillcolor="rgba(58,142,224,0.08)")
    st.plotly_chart(fig5, use_container_width=True)

# ── Top Centers Table ──────────────────────────────────────────────────────────
st.divider()
st.markdown("#### 🏆 Top Performing Centers")

def score_badge(s):
    if s >= 85: return "🟢 Excellent"
    if s >= 75: return "🔵 Good"
    if s >= 65: return "🟡 Fair"
    return "🔴 Needs Attention"

top = df[["center_name","city","center_type","region","mrr","wdr",
          "css","composite_score","downtime","contam"]].copy()
top.columns = ["Center","City","Type","Region","MRR %","WDR %",
               "CSS","Score","Downtime %","Contam %"]
top["Status"] = top["Score"].apply(score_badge)
top = top.sort_values("Score", ascending=False).head(10).reset_index(drop=True)
top.index += 1
st.dataframe(
    top.style
       .background_gradient(subset=["Score"], cmap="Greens", vmin=60, vmax=100)
       .background_gradient(subset=["MRR %"], cmap="Greens", vmin=70, vmax=95)
       .format({"MRR %":"{:.1f}","WDR %":"{:.1f}","CSS":"{:.2f}",
                "Score":"{:.1f}","Downtime %":"{:.1f}","Contam %":"{:.1f}"}),
    use_container_width=True, height=360)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — FULL KPI DESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("## 📖 KPI Reference Guide")
st.caption("Detailed definitions, formulas, targets, and interpretation notes for every KPI dimension.")

# ── helper to render a KPI card block ─────────────────────────────────────────
def kpi_card(icon, name, category, cat_color, formula, target,
             interpretation, why_it_matters, data_source, unit=""):
    st.markdown(f"""
<div style="background:#ffffff;border:1px solid #e4e4e0;border-left:5px solid {cat_color};
            border-radius:12px;padding:18px 22px;margin-bottom:14px">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
    <span style="font-size:22px">{icon}</span>
    <div>
      <span style="font-size:15px;font-weight:700;color:#1a1a18">{name}</span>
      &nbsp;
      <span style="font-size:10px;font-weight:600;padding:2px 9px;border-radius:20px;
                   background:{cat_color}22;color:{cat_color}">{category}</span>
    </div>
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:12px">
    <tr style="vertical-align:top">
      <td style="width:22%;color:#666;padding:4px 8px 4px 0;font-weight:600">Formula</td>
      <td style="padding:4px 0"><code style="background:#f5f5f3;padding:2px 6px;border-radius:4px;
                 font-size:11px">{formula}</code></td>
    </tr>
    <tr style="vertical-align:top">
      <td style="color:#666;padding:4px 8px 4px 0;font-weight:600">Target</td>
      <td style="padding:4px 0;font-weight:600;color:{cat_color}">{target}</td>
    </tr>
    <tr style="vertical-align:top">
      <td style="color:#666;padding:4px 8px 4px 0;font-weight:600">Interpretation</td>
      <td style="padding:4px 0;color:#333">{interpretation}</td>
    </tr>
    <tr style="vertical-align:top">
      <td style="color:#666;padding:4px 8px 4px 0;font-weight:600">Why it matters</td>
      <td style="padding:4px 0;color:#333">{why_it_matters}</td>
    </tr>
    <tr style="vertical-align:top">
      <td style="color:#666;padding:4px 8px 4px 0;font-weight:600">Data source</td>
      <td style="padding:4px 0;color:#666">{data_source}</td>
    </tr>
  </table>
</div>""", unsafe_allow_html=True)

# ── OPERATIONAL ───────────────────────────────────────────────────────────────
st.markdown("### ⚙️ Operational KPIs")
st.markdown("""
Operational KPIs measure the day-to-day efficiency, reliability, and throughput of each
recycling center. They directly determine how much material gets processed, how quickly,
and at what level of equipment and logistics performance.
""")

kpi_card(
    icon="♻️",
    name="Material Recovery Rate (MRR)",
    category="Operational",
    cat_color="#1e7a49",
    formula="MRR (%) = (Materials Recovered ÷ Total Input) × 100",
    target="≥ 86% (NYS DEC state standard)",
    interpretation=(
        "MRR measures the fraction of incoming waste that is successfully sorted, "
        "processed, and recovered as usable material rather than sent to landfill. "
        "A higher MRR reflects better sorting technology, staff training, and cleaner "
        "incoming streams. Values below 80% suggest significant process inefficiencies "
        "or high contamination levels requiring immediate intervention."
    ),
    why_it_matters=(
        "MRR is the primary operational success metric for any recycling facility. "
        "It directly determines landfill diversion tonnage, feedstock revenue, "
        "and compliance with NYS Part 360 solid-waste management regulations. "
        "Facilities below target risk permit sanctions and reduced tipping-fee income."
    ),
    data_source="batch_records → materials_recovered_tons / total_input_tons"
)

kpi_card(
    icon="⏱️",
    name="Processing Time per Batch (PTB)",
    category="Operational",
    cat_color="#1e7a49",
    formula="PTB (h) = Batch End Time − Batch Start Time (per completed batch)",
    target="≤ 4.0 hours (Municipal/Commercial); ≤ 5.5 h (Electronic); ≤ 7.0 h (Hazardous)",
    interpretation=(
        "PTB tracks how long each processing batch takes from intake to sorted output. "
        "Shorter times indicate efficient material flow, well-maintained sorting lines, "
        "and adequate staffing. Extended PTBs (>5 h for Municipal) signal conveyor "
        "bottlenecks, sorting errors requiring rework, or equipment slowdowns. "
        "Variance (std dev) in PTB is equally important — high variance suggests "
        "unpredictable operations that are hard to schedule and staff."
    ),
    why_it_matters=(
        "PTB drives throughput capacity. A center processing 10 batches/day at 4 h "
        "versus 6 h has 33% more capacity. Controlling PTB is essential for meeting "
        "tonnage contracts and avoiding overtime labor costs."
    ),
    data_source="batch_records → processing_hours per batch_id"
)

kpi_card(
    icon="🔧",
    name="Equipment Downtime Rate",
    category="Operational",
    cat_color="#1e7a49",
    formula="Downtime (%) = (Unplanned Downtime Hours ÷ Scheduled Operating Hours) × 100",
    target="≤ 5% of scheduled hours",
    interpretation=(
        "Equipment downtime quantifies time lost to mechanical failures, power outages, "
        "and operator error expressed as a share of planned production time. Scheduled "
        "preventive maintenance is excluded from the numerator. Values above 7% indicate "
        "systemic reliability problems. The four main causes tracked are: mechanical "
        "failure (28%), scheduled maintenance (42%), power outages (12%), and operator "
        "error (10%). Centers should target a maintenance-to-failure ratio > 3:1."
    ),
    why_it_matters=(
        "Every 1% increase in downtime costs approximately $18–22K/month in lost "
        "processing capacity and overtime recovery costs. Downtime above 8% triggers "
        "DEC operational review for permitted facilities."
    ),
    data_source="equipment_log × downtime_events → downtime_hours / scheduled_hours"
)

kpi_card(
    icon="🚛",
    name="Transportation Efficiency (TE)",
    category="Operational",
    cat_color="#1e7a49",
    formula="TE (%) = (Actual Payload ÷ Vehicle Capacity) × 100, averaged across all trips",
    target="≥ 88% load efficiency",
    interpretation=(
        "TE measures how fully loaded collection and outbound delivery vehicles are on "
        "average. A score of 88% means vehicles are carrying 88% of their rated capacity "
        "per trip. Values below 80% indicate route planning inefficiencies, scheduling "
        "mismatches, or under-utilization of fleet capacity. TE is also reported as "
        "trips/day and cost-per-ton-transported in operational reports."
    ),
    why_it_matters=(
        "Transportation represents 18–25% of a recycling center's total operating costs. "
        "A 10% improvement in TE reduces fuel consumption, driver hours, and fleet wear, "
        "typically saving $40–80K/year per center depending on volume."
    ),
    data_source="transport_records → payload_tons / vehicle_capacity_tons per trip"
)

# ── ENVIRONMENTAL ─────────────────────────────────────────────────────────────
st.markdown("### 🌿 Environmental KPIs")
st.markdown("""
Environmental KPIs capture the ecological performance and sustainability impact of
recycling operations — from how much waste is kept out of landfills to the contamination
of recovered streams and the energy footprint per ton processed.
""")

kpi_card(
    icon="🌎",
    name="Waste Diversion Rate (WDR)",
    category="Environmental",
    cat_color="#0f6e56",
    formula="WDR (%) = (Materials Diverted from Landfill ÷ Total Waste Received) × 100",
    target="≥ 80% statewide (NYS Climate Act alignment)",
    interpretation=(
        "WDR measures the proportion of waste received at a facility that is redirected "
        "away from landfill disposal through recycling, composting, or energy recovery. "
        "It is closely related to MRR but also counts organic waste diversion streams. "
        "A WDR of 80%+ means 4 out of every 5 tons received avoids the landfill. "
        "Regional variation is significant: NYC Metro typically achieves 82–88% while "
        "North Country centers average 70–76% due to higher contamination in rural streams."
    ),
    why_it_matters=(
        "WDR is the core metric for NYS Climate Leadership and Community Protection Act "
        "(CLCPA) compliance. Each ton diverted avoids approximately 0.5 metric tons of "
        "CO₂-equivalent greenhouse gas emissions from landfill methane. Statewide, "
        "the 20-center network diverts an estimated 85,000 tons/year from landfill."
    ),
    data_source="batch_records → diverted_tons / total_waste_tons"
)

kpi_card(
    icon="⚠️",
    name="Contamination Rate",
    category="Environmental",
    cat_color="#0f6e56",
    formula="Contamination (%) = (Contaminated Weight ÷ Total Stream Weight) × 100, per material stream",
    target="≤ 6% overall; ≤ 3% for Paper/Metal streams",
    interpretation=(
        "Contamination rate tracks the percentage of each material stream (Paper, Plastics, "
        "Glass, Metals, Electronics, Hazardous) that contains non-target materials rendering "
        "it unsaleable or requiring expensive re-processing. Paper contamination above 8% "
        "causes rejection by end-markets. Plastics above 10% fails MRF grade standards. "
        "Hazardous material contamination below 3% reflects proper source separation. "
        "Stream-level monitoring is essential: aggregate rates can mask critical "
        "individual stream failures."
    ),
    why_it_matters=(
        "Contamination is the single largest cause of recovered-material revenue loss. "
        "A 1% increase in plastic stream contamination reduces commodity value by "
        "approximately $8–12/ton. It also drives up reprocessing labor costs and "
        "generates secondary waste streams requiring landfill disposal."
    ),
    data_source="material_streams → contaminated_weight_kg / total_stream_weight_kg"
)

kpi_card(
    icon="⚡",
    name="Energy Consumption per Ton",
    category="Environmental",
    cat_color="#0f6e56",
    formula="Energy (kWh/ton) = Total kWh Consumed ÷ Tons Processed in Same Period",
    target="≤ 30 kWh/ton (Municipal/Commercial); ≤ 45 kWh/ton (Electronic/Hazardous)",
    interpretation=(
        "Energy intensity measures the electrical energy required to process one metric "
        "ton of material. Municipal MRFs with modern optical sorters typically achieve "
        "24–30 kWh/ton. E-waste centers require more energy for shredding/separation "
        "(38–50 kWh/ton). Hazardous material centers are most energy-intensive (50–60 "
        "kWh/ton) due to containment and treatment requirements. Month-over-month trends "
        "are more informative than absolute values due to seasonal variation in "
        "heating/cooling loads."
    ),
    why_it_matters=(
        "Energy costs represent 8–14% of total operating expenditure. Reducing energy "
        "intensity by 5 kWh/ton across 20 centers processing 85,000 tons/year saves "
        "approximately $212,500/year at average NYS commercial rates ($0.05/kWh). "
        "Energy performance also affects a facility's environmental permit conditions."
    ),
    data_source="energy_usage → kwh_consumed, joined to batch_records for tons denominator"
)

# ── FINANCIAL ─────────────────────────────────────────────────────────────────
st.markdown("### 💰 Financial KPIs")
st.markdown("""
Financial KPIs track the economic sustainability of recycling operations — from revenue
generation through commodity sales and tipping fees to operating cost efficiency,
margin performance, and customer satisfaction as a leading indicator of revenue retention.
""")

kpi_card(
    icon="💵",
    name="Revenue & Net Operating Margin",
    category="Financial",
    cat_color="#8b5cf6",
    formula="Net Margin ($) = Total Revenue − Total Opex; Margin % = (Net Margin ÷ Revenue) × 100",
    target="Margin % ≥ 20%; Revenue growth ≥ 3% YoY",
    interpretation=(
        "Revenue for recycling centers comes from three sources: (1) tipping fees charged "
        "per ton of incoming waste, (2) commodity sales of sorted materials (paper, metals, "
        "plastics), and (3) government program grants. Operating costs include labor (55%), "
        "maintenance (20%), transportation (18%), and utilities (7%). Net margin above 20% "
        "indicates a financially sustainable operation. Municipal centers often operate at "
        "lower margins (10–18%) as they cross-subsidize residential service. Commercial "
        "centers target 22–28% margins. A negative margin requires municipal subsidy review."
    ),
    why_it_matters=(
        "Financial sustainability determines a center's ability to invest in equipment "
        "upgrades, maintain competitive wages, and expand capacity. Centers running "
        "negative margins for 2+ consecutive quarters typically require operational "
        "restructuring or public funding intervention."
    ),
    data_source="financial_transactions → revenue, operating_cost by category and month"
)

kpi_card(
    icon="🏷️",
    name="Cost per Ton Processed",
    category="Financial",
    cat_color="#8b5cf6",
    formula="Cost/Ton ($) = Total Operating Expenditure ÷ Tons Processed",
    target="≤ $55/ton (Municipal); ≤ $65/ton (Commercial); ≤ $95/ton (E-Waste); ≤ $140/ton (Hazardous)",
    interpretation=(
        "Cost per ton is the primary efficiency benchmark for comparing centers of different "
        "sizes and types. It normalizes total operating costs against output volume. "
        "Hazardous material centers are expected to have costs 2–3× higher than municipal "
        "facilities due to regulatory compliance, specialized containment, and disposal "
        "requirements. Month-over-month cost-per-ton trends reflect the combined effect "
        "of process improvements, volume changes, and input cost pressures."
    ),
    why_it_matters=(
        "Cost-per-ton benchmarking enables NYS DEC to identify underperforming facilities "
        "for operational assistance and informs tipping-fee rate setting across regions. "
        "A $5/ton improvement across the 20-center network saves approximately $425K/year."
    ),
    data_source="financial_transactions (opex) ÷ batch_records (tons_processed)"
)

kpi_card(
    icon="⭐",
    name="Customer Satisfaction Score (CSS)",
    category="Financial",
    cat_color="#8b5cf6",
    formula="CSS = Average survey rating (1–5 scale) across all respondents in the period",
    target="≥ 4.2 / 5.0 (rolling 90-day average)",
    interpretation=(
        "CSS aggregates post-service surveys from residential customers, commercial haulers, "
        "and municipal program participants. The survey covers: drop-off experience (25%), "
        "staff helpfulness (20%), facility cleanliness (20%), wait time (20%), and "
        "information clarity (15%). Scores below 3.8 indicate service quality concerns "
        "that increase program abandonment risk. NYC Metro centers typically achieve higher "
        "CSS (4.3–4.6) due to more modern facilities. North Country centers face structural "
        "challenges (limited hours, long travel distances) that suppress scores."
    ),
    why_it_matters=(
        "CSS is a leading indicator of participation rates. A 0.3-point CSS decline "
        "correlates with a 4–8% reduction in voluntary drop-off volumes, directly "
        "reducing tipping fee revenue and diversion rates. High CSS also reduces the "
        "cost of public education campaigns."
    ),
    data_source="customer_surveys → avg(score) by center and 90-day rolling window"
)

# ── WORKFORCE ─────────────────────────────────────────────────────────────────
st.markdown("### 👷 Workforce KPIs")
st.markdown("""
Workforce KPIs measure the human capital health of recycling operations — retention,
safety, and the stability of the people who keep the facilities running. These metrics
are leading indicators of operational performance: high turnover and safety incidents
predictably precede process quality deterioration.
""")

kpi_card(
    icon="🔄",
    name="Employee Turnover Rate (ETR)",
    category="Workforce",
    cat_color="#a36b0b",
    formula="ETR (%) = (Terminations in Period ÷ Average Headcount) × 100",
    target="≤ 15% annualized",
    interpretation=(
        "ETR measures voluntary and involuntary separations as a percentage of average "
        "staff headcount. The recycling industry average is 18–22% nationally; NYS centers "
        "target ≤15% through competitive wages and safety culture. Turnover above 20% "
        "is a critical signal: experienced sorters take 3–4 months to reach full "
        "productivity, so high turnover directly degrades MRR and contamination rates. "
        "North Country centers face structural headwinds (thin labor markets, seasonal "
        "weather) that sustain higher turnover despite good management practices. "
        "Separate tracking of voluntary versus involuntary turnover is recommended."
    ),
    why_it_matters=(
        "Replacing a trained MRF sorter costs $4,500–7,000 in recruitment, onboarding, "
        "and productivity loss. A 5% ETR reduction across 20 centers (avg 45 staff each) "
        "saves approximately $202,500–315,000/year in replacement costs alone."
    ),
    data_source="hr_events → COUNT(terminations) / AVG(headcount) by center and period"
)

kpi_card(
    icon="🦺",
    name="Workplace Safety Incidents (WSI)",
    category="Workforce",
    cat_color="#a36b0b",
    formula="WSI = (Recordable Incidents × 100) ÷ Average Employee Count in Period",
    target="≤ 1.0 incidents per 100 employees (OSHA BLS recycling industry benchmark)",
    interpretation=(
        "WSI tracks OSHA-recordable injuries and illnesses per 100 full-time-equivalent "
        "employees. The metric includes: lacerations from sorting equipment (most common), "
        "musculoskeletal strain, forklift-related incidents, and chemical exposure events "
        "at hazardous material centers. Minor incidents (first-aid only) are tracked "
        "separately as leading indicators. Severity weighting (minor=1, serious=5, "
        "lost-time=10) produces a weighted incident index for trend analysis. Centers "
        "above 1.5 WSI/100 trigger mandatory DEC safety review. Above 2.5 can result "
        "in operating permit conditions."
    ),
    why_it_matters=(
        "Beyond human cost, each recordable incident generates $35,000–85,000 in direct "
        "and indirect costs (medical, investigation, productivity loss, OSHA fines). "
        "WSI trends are the strongest predictor of workers' compensation insurance "
        "rate changes, which represent 3–6% of total payroll."
    ),
    data_source="safety_incidents → COUNT(incident_id) × 100 / AVG(headcount)"
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — KPI SCORECARD SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("## 📋 KPI Scorecard Summary")
st.caption("Performance vs. target for all 10 KPI dimensions — current filter selection")

SCORECARD_DEFS = [
    ("mrr",      "Material Recovery Rate",    "%",     86,   False, "#1e7a49",  "Operational"),
    ("ptb",      "Processing Time / Batch",   "h",     4.0,  True,  "#1e7a49",  "Operational"),
    ("downtime", "Equipment Downtime",         "%",     5.0,  True,  "#1e7a49",  "Operational"),
    ("te",       "Transportation Efficiency", "%",     88,   False, "#1e7a49",  "Operational"),
    ("wdr",      "Waste Diversion Rate",      "%",     80,   False, "#0f6e56",  "Environmental"),
    ("contam",   "Contamination Rate",        "%",     6.0,  True,  "#0f6e56",  "Environmental"),
    ("energy",   "Energy Consumption",        "kWh/t", 30,   True,  "#0f6e56",  "Environmental"),
    ("css",      "Customer Satisfaction",     "/5",    4.2,  False, "#8b5cf6",  "Financial"),
    ("etr",      "Employee Turnover Rate",    "%",     15,   True,  "#a36b0b",  "Workforce"),
    ("wsi",      "Safety Incidents / 100",    "",      1.0,  True,  "#a36b0b",  "Workforce"),
]

sc_col1, sc_col2 = st.columns(2)
for i, (key, label, unit, target, lower_better, color, cat) in enumerate(SCORECARD_DEFS):
    val = float(getattr(score, f"avg_{key}"))
    if lower_better:
        pct = min(100.0, target / max(val, 0.001) * 100)
    else:
        pct = min(100.0, val / target * 100)
    bar_color = "#1e7a49" if pct >= 90 else "#e09d20" if pct >= 70 else "#d94a4a"
    icon = "🟢" if pct >= 90 else "🟡" if pct >= 70 else "🔴"
    direction = "↓ lower better" if lower_better else "↑ higher better"

    col = sc_col1 if i % 2 == 0 else sc_col2
    with col:
        st.markdown(f"""
<div style="background:#fff;border:1px solid #e4e4e0;border-left:4px solid {color};
            border-radius:10px;padding:12px 16px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
    <span style="font-size:12px;font-weight:600">{icon} {label}</span>
    <span style="font-size:10px;background:{color}22;color:{color};
                 padding:2px 7px;border-radius:10px;font-weight:600">{cat}</span>
  </div>
  <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:6px">
    <span style="font-size:20px;font-weight:700;color:{bar_color}">{val:.2f}{unit}</span>
    <span style="font-size:11px;color:#888">Target: {target}{unit} · {direction}</span>
  </div>
  <div style="background:#e4e4e0;border-radius:4px;height:7px;overflow:hidden">
    <div style="background:{bar_color};width:{pct:.1f}%;height:100%;border-radius:4px"></div>
  </div>
  <div style="font-size:10px;color:#999;text-align:right;margin-top:3px">{pct:.0f}% of target</div>
</div>""", unsafe_allow_html=True)

# Radar chart
st.markdown("#### KPI Radar — Statewide Average vs. Target")
radar_labels = [d[1] for d in SCORECARD_DEFS]
actual_vals, target_vals = [], []
for key, label, unit, target, lower_better, color, cat in SCORECARD_DEFS:
    val = float(getattr(score, f"avg_{key}"))
    pct = min(100.0, target / max(val, 0.001) * 100) if lower_better else min(100.0, val / target * 100)
    actual_vals.append(pct)
    target_vals.append(100)

fig_r = go.Figure()
fig_r.add_trace(go.Scatterpolar(
    r=actual_vals + [actual_vals[0]],
    theta=radar_labels + [radar_labels[0]],
    fill="toself", name="Statewide Avg",
    fillcolor="rgba(30,122,73,0.15)",
    line=dict(color="#1e7a49", width=2.5)))
fig_r.add_trace(go.Scatterpolar(
    r=target_vals + [100],
    theta=radar_labels + [radar_labels[0]],
    fill="toself", name="Target (100%)",
    fillcolor="rgba(58,142,224,0.06)",
    line=dict(color="#3a8ee0", width=1.5, dash="dash")))
fig_r.update_layout(
    polar=dict(radialaxis=dict(range=[0, 115], tickfont_size=9)),
    height=440, margin=dict(t=30, b=10),
    legend=dict(orientation="h", y=-0.08))
st.plotly_chart(fig_r, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ALERTS & ESCALATION OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("## 🔔 Alerts & Escalation Overview")
st.caption("Current threshold breaches and operational notifications requiring attention")

LEVEL_CFG = {
    "critical": dict(icon="🔴", color="#d94a4a", bg="#fdf0f0", border="#d94a4a", label="CRITICAL"),
    "warning":  dict(icon="🟡", color="#a36b0b", bg="#fef8ee", border="#e09d20", label="WARNING"),
    "ok":       dict(icon="🟢", color="#1e7a49", bg="#f0faf4", border="#3aaa6a", label="OK"),
}

crit_n = len(alerts_df[alerts_df["level"] == "critical"])
warn_n = len(alerts_df[alerts_df["level"] == "warning"])
ok_n   = len(alerts_df[alerts_df["level"] == "ok"])

a1, a2, a3 = st.columns(3)
for col, level, n in [(a1,"critical",crit_n),(a2,"warning",warn_n),(a3,"ok",ok_n)]:
    cfg = LEVEL_CFG[level]
    col.markdown(f"""
<div style="background:{cfg['bg']};border:2px solid {cfg['border']};border-radius:12px;
            padding:16px;text-align:center">
  <div style="font-size:26px;font-weight:700;color:{cfg['color']}">{n}</div>
  <div style="font-size:12px;font-weight:600;color:{cfg['color']}">{cfg['icon']} {cfg['label']}</div>
</div>""", unsafe_allow_html=True)

st.markdown("")

# Alert escalation protocol explanation
with st.expander("📘 Escalation Protocol & Threshold Definitions"):
    st.markdown("""
    #### How the Alert System Works

    The NYS Recycling KPI Dashboard monitors **8 threshold rules** continuously against
    the latest monthly KPI data. Each rule compares a center's reported value against
    the defined threshold and assigns a severity level:

    | Severity | Definition | Response Timeline |
    |----------|-----------|-------------------|
    | 🔴 **Critical** | Hard breach of a regulatory or operational safety threshold | Immediate — within 24 hours |
    | 🟡 **Warning** | KPI approaching limit or sustained below target for ≥ 2 months | Scheduled — within 5 business days |
    | 🟢 **OK** | All monitored KPIs meeting or exceeding targets | Routine monitoring — monthly review |

    #### Monitored Thresholds

    | KPI | Warning Threshold | Critical Threshold |
    |-----|------------------|-------------------|
    | Material Recovery Rate | < 83% | < 78% |
    | Waste Diversion Rate | < 77% | < 70% |
    | Contamination Rate | > 7% | > 8% |
    | Equipment Downtime | > 6% | > 7% |
    | Safety Incidents (WSI) | > 1.3/100 | > 1.5/100 |
    | Employee Turnover | > 18% | > 20% |
    | Customer Satisfaction | < 4.0/5 | < 3.8/5 |
    | Transportation Efficiency | < 82% | < 80% |

    #### Escalation Actions
    - **Critical alerts** trigger automatic notification to the Regional DEC Solid Waste Manager
      and the facility director. A corrective action plan (CAP) is required within 72 hours.
    - **Warning alerts** generate a weekly digest sent to facility operations managers.
      Two consecutive warning months for the same KPI automatically escalate to Critical.
    - **OK notifications** are compiled into the monthly performance scorecard distributed
      to the NYS DEC Commissioner's office.
    """)

# Show alert cards
show_all_alerts = st.checkbox("Show all alerts", value=True)
display_alerts = alerts_df if show_all_alerts else alerts_df[alerts_df["level"].isin(["critical","warning"])]

for _, row in display_alerts.iterrows():
    cfg = LEVEL_CFG.get(row["level"], LEVEL_CFG["ok"])
    st.markdown(f"""
<div style="background:{cfg['bg']};border:1px solid #e4e4e0;
            border-left:4px solid {cfg['border']};
            border-radius:10px;padding:13px 18px;margin-bottom:8px">
  <div style="display:flex;align-items:flex-start;gap:10px">
    <span style="font-size:16px;flex-shrink:0">{cfg['icon']}</span>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;flex-wrap:wrap">
        <b style="font-size:13px">{row['center_name']}</b>
        <span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;
                     background:{cfg['color']}22;color:{cfg['color']}">{cfg['label']}</span>
        <span style="font-size:10px;font-weight:600;color:#3a8ee0;padding:2px 7px;
                     background:#eaf2fc;border-radius:10px">{row['kpi']}</span>
      </div>
      <div style="font-size:12px;color:#333;margin-bottom:5px">{row['message']}</div>
      <div style="display:flex;gap:16px;font-size:11px;color:#666">
        <span>Value: <b style="color:#1a1a18">{row['value']}</b></span>
        <span>Threshold: <b style="color:#1a1a18">{row['threshold']}</b></span>
        <span>Date: <b style="color:#1a1a18">{row['created_at']}</b></span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
