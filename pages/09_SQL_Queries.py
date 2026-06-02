"""pages/09_SQL_Queries.py — Pre-defined library + rich custom query builder."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.db_engine import run_query, get_connection

st.set_page_config(page_title="SQL Queries · NYS Recycling", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# PRE-DEFINED QUERY LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
SQL_LIBRARY = {
    "MRR — Monthly by Center": {
        "category": "Operational",
        "description": "Material Recovery Rate per center per month with rolling 3-month average and statewide target.",
        "sql": """\
SELECT
    c.center_id,
    c.center_name,
    c.region,
    c.center_type,
    k.report_month,
    ROUND(k.mrr, 2)                            AS material_recovery_rate_pct,
    ROUND(AVG(k.mrr) OVER (
        PARTITION BY c.center_type
        ORDER BY k.report_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                      AS type_rolling_3mo_avg,
    86.0                                       AS nys_mrr_target,
    CASE WHEN k.mrr >= 86 THEN 'On Target'
         WHEN k.mrr >= 80 THEN 'Watch'
         ELSE 'Below Target' END               AS status
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
ORDER BY k.report_month DESC, material_recovery_rate_pct DESC;"""},

    "WDR — Regional Monthly Trend": {
        "category": "Environmental",
        "description": "Waste Diversion Rate aggregated by region with min/max spread and target comparison.",
        "sql": """\
SELECT
    k.report_month,
    c.region,
    ROUND(AVG(k.wdr), 2)   AS avg_wdr_pct,
    ROUND(MIN(k.wdr), 2)   AS min_wdr_pct,
    ROUND(MAX(k.wdr), 2)   AS max_wdr_pct,
    ROUND(MAX(k.wdr) - MIN(k.wdr), 2) AS range_wdr,
    80.0                   AS nys_wdr_target
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY k.report_month, c.region
ORDER BY k.report_month, c.region;"""},

    "Contamination by Material Stream": {
        "category": "Environmental",
        "description": "Average contamination rate per material stream broken down by region and center type.",
        "sql": """\
SELECT
    s.material,
    c.region,
    c.center_type,
    ROUND(AVG(s.contamination_pct), 3)  AS avg_contamination_pct,
    ROUND(MIN(s.contamination_pct), 3)  AS min_contamination_pct,
    ROUND(MAX(s.contamination_pct), 3)  AS max_contamination_pct,
    ROUND(SUM(s.rejected_tons), 1)      AS total_rejected_tons,
    ROUND(SUM(s.recovered_tons), 1)     AS total_recovered_tons,
    6.0                                 AS target_max_contam_pct
FROM material_streams s
JOIN centers c ON c.center_id = s.center_id
GROUP BY s.material, c.region, c.center_type
ORDER BY avg_contamination_pct DESC;"""},

    "Processing Time per Batch": {
        "category": "Operational",
        "description": "Average PTB with min, max per center and target comparison.",
        "sql": """\
SELECT
    c.center_id,
    c.center_name,
    c.center_type,
    c.region,
    ROUND(AVG(k.ptb), 2)  AS avg_ptb_hours,
    ROUND(MIN(k.ptb), 2)  AS min_ptb_hours,
    ROUND(MAX(k.ptb), 2)  AS max_ptb_hours,
    4.0                   AS ptb_target_hours,
    CASE WHEN AVG(k.ptb) <= 4.0 THEN 'On Target'
         WHEN AVG(k.ptb) <= 5.0 THEN 'Watch'
         ELSE 'Above Target' END AS status
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_id, c.center_name, c.center_type, c.region
ORDER BY avg_ptb_hours;"""},

    "Equipment Downtime by Type": {
        "category": "Operational",
        "description": "Downtime % grouped by center type with min/max range and target flag.",
        "sql": """\
SELECT
    c.center_type,
    ROUND(AVG(k.downtime), 2)     AS avg_downtime_pct,
    ROUND(MIN(k.downtime), 2)     AS min_downtime_pct,
    ROUND(MAX(k.downtime), 2)     AS max_downtime_pct,
    COUNT(DISTINCT c.center_id)   AS center_count,
    5.0                           AS target_max_downtime_pct,
    CASE WHEN AVG(k.downtime) <= 5 THEN 'On Target'
         WHEN AVG(k.downtime) <= 7 THEN 'Watch'
         ELSE 'Critical' END      AS status
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_type
ORDER BY avg_downtime_pct DESC;"""},

    "Revenue vs Opex Monthly": {
        "category": "Financial",
        "description": "Monthly statewide revenue, opex, net margin, margin %, and cost per ton.",
        "sql": """\
SELECT
    k.report_month,
    ROUND(SUM(k.revenue), 0)                          AS total_revenue_k,
    ROUND(SUM(k.opex), 0)                             AS total_opex_k,
    ROUND(SUM(k.revenue - k.opex), 0)                AS net_margin_k,
    ROUND(AVG((k.revenue-k.opex)*100.0/k.revenue),1) AS avg_margin_pct,
    ROUND(SUM(k.opex)/SUM(k.tons_processed), 2)      AS cost_per_ton_usd
FROM monthly_kpi k
GROUP BY k.report_month
ORDER BY k.report_month;"""},

    "Customer Satisfaction Score": {
        "category": "Financial",
        "description": "CSS by center with 3-month rolling average and target comparison.",
        "sql": """\
SELECT
    c.center_id,
    c.center_name,
    c.region,
    c.center_type,
    k.report_month,
    ROUND(k.css, 2)                                AS css_score,
    ROUND(AVG(k.css) OVER (
        PARTITION BY c.center_id
        ORDER BY k.report_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                          AS rolling_3mo_avg,
    4.2                                            AS target_css,
    CASE WHEN k.css >= 4.2 THEN 'On Target'
         WHEN k.css >= 3.8 THEN 'Watch'
         ELSE 'Below Target' END                   AS status
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
ORDER BY k.report_month DESC, css_score DESC;"""},

    "Employee Turnover Rate": {
        "category": "Workforce",
        "description": "Monthly ETR by region with min/max range and target comparison.",
        "sql": """\
SELECT
    k.report_month,
    c.region,
    ROUND(AVG(k.etr), 2)  AS avg_turnover_rate_pct,
    ROUND(MIN(k.etr), 2)  AS min_etr,
    ROUND(MAX(k.etr), 2)  AS max_etr,
    15.0                  AS target_max_etr
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY k.report_month, c.region
ORDER BY k.report_month, avg_turnover_rate_pct DESC;"""},

    "Safety Incidents per 100 Employees": {
        "category": "Workforce",
        "description": "WSI per 100 employees by center with compliance classification.",
        "sql": """\
SELECT
    c.center_name,
    c.region,
    c.center_type,
    ROUND(AVG(k.wsi), 2)  AS avg_wsi_per_100,
    ROUND(MIN(k.wsi), 2)  AS min_wsi,
    ROUND(MAX(k.wsi), 2)  AS max_wsi,
    CASE
        WHEN AVG(k.wsi) <= 1.0 THEN 'Compliant'
        WHEN AVG(k.wsi) <= 1.5 THEN 'Watch'
        ELSE                        'Non-Compliant'
    END                   AS safety_status,
    1.0                   AS target_max_wsi
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_name, c.region, c.center_type
ORDER BY avg_wsi_per_100 DESC;"""},

    "Composite KPI Score — Map Geo": {
        "category": "Geo / Map",
        "description": "Full geo + KPI snapshot for map visualization with weighted composite scoring formula.",
        "sql": """\
SELECT
    c.center_id,
    c.center_name,
    c.city,
    c.region,
    c.center_type,
    c.latitude,
    c.longitude,
    k.mrr, k.wdr, k.css, k.contam,
    k.downtime, k.te, k.etr, k.energy,
    k.revenue, k.opex,
    ROUND(
      (CASE WHEN k.mrr    >= 86 THEN 30 ELSE k.mrr/86.0*30   END) +
      (CASE WHEN k.wdr    >= 80 THEN 20 ELSE k.wdr/80.0*20   END) +
      (CASE WHEN k.contam <=  6 THEN 15 ELSE 6.0/k.contam*15 END) +
      (k.css/5.0*20) +
      (CASE WHEN k.te     >= 88 THEN 15 ELSE k.te/88.0*15    END)
    , 1) AS composite_kpi_score,
    CASE
        WHEN ROUND((CASE WHEN k.mrr>=86 THEN 30 ELSE k.mrr/86.0*30 END)+
                   (CASE WHEN k.wdr>=80 THEN 20 ELSE k.wdr/80.0*20 END)+
                   (CASE WHEN k.contam<=6 THEN 15 ELSE 6.0/k.contam*15 END)+
                   (k.css/5.0*20)+
                   (CASE WHEN k.te>=88 THEN 15 ELSE k.te/88.0*15 END),1) >= 85
             THEN 'Excellent'
        WHEN ROUND((CASE WHEN k.mrr>=86 THEN 30 ELSE k.mrr/86.0*30 END)+
                   (CASE WHEN k.wdr>=80 THEN 20 ELSE k.wdr/80.0*20 END)+
                   (CASE WHEN k.contam<=6 THEN 15 ELSE 6.0/k.contam*15 END)+
                   (k.css/5.0*20)+
                   (CASE WHEN k.te>=88 THEN 15 ELSE k.te/88.0*15 END),1) >= 75
             THEN 'Good'
        WHEN ROUND((CASE WHEN k.mrr>=86 THEN 30 ELSE k.mrr/86.0*30 END)+
                   (CASE WHEN k.wdr>=80 THEN 20 ELSE k.wdr/80.0*20 END)+
                   (CASE WHEN k.contam<=6 THEN 15 ELSE 6.0/k.contam*15 END)+
                   (k.css/5.0*20)+
                   (CASE WHEN k.te>=88 THEN 15 ELSE k.te/88.0*15 END),1) >= 65
             THEN 'Fair'
        ELSE 'Needs Attention'
    END AS performance_tier
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
WHERE k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)
ORDER BY composite_kpi_score DESC;"""},

    "Energy Consumption per Ton": {
        "category": "Environmental",
        "description": "Energy intensity kWh/ton by center type and region with monthly trend.",
        "sql": """\
SELECT
    c.center_type,
    c.region,
    k.report_month,
    ROUND(AVG(k.energy), 2)  AS avg_kwh_per_ton,
    ROUND(MIN(k.energy), 2)  AS min_kwh_per_ton,
    ROUND(MAX(k.energy), 2)  AS max_kwh_per_ton,
    30.0                     AS target_kwh_per_ton
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_type, c.region, k.report_month
ORDER BY k.report_month, avg_kwh_per_ton DESC;"""},

    "Full Operational Scorecard — Latest Month": {
        "category": "Scorecard",
        "description": "All 10 KPIs in a single row per center for the most recent reporting month, with status flags.",
        "sql": """\
SELECT
    c.center_name,
    c.city,
    c.region,
    c.center_type,
    ROUND(k.mrr,1)      AS mrr_pct,
    CASE WHEN k.mrr>=86 THEN 'OK' WHEN k.mrr>=80 THEN 'Watch' ELSE 'Alert' END AS mrr_status,
    ROUND(k.wdr,1)      AS wdr_pct,
    CASE WHEN k.wdr>=80 THEN 'OK' WHEN k.wdr>=75 THEN 'Watch' ELSE 'Alert' END AS wdr_status,
    ROUND(k.ptb,2)      AS ptb_h,
    CASE WHEN k.ptb<=4 THEN 'OK' WHEN k.ptb<=5 THEN 'Watch' ELSE 'Alert' END   AS ptb_status,
    ROUND(k.downtime,1) AS downtime_pct,
    CASE WHEN k.downtime<=5 THEN 'OK' WHEN k.downtime<=7 THEN 'Watch' ELSE 'Alert' END AS dt_status,
    ROUND(k.contam,1)   AS contam_pct,
    CASE WHEN k.contam<=6 THEN 'OK' WHEN k.contam<=8 THEN 'Watch' ELSE 'Alert' END AS cn_status,
    ROUND(k.css,2)      AS css,
    CASE WHEN k.css>=4.2 THEN 'OK' WHEN k.css>=3.8 THEN 'Watch' ELSE 'Alert' END  AS css_status,
    ROUND(k.te,1)       AS te_pct,
    ROUND(k.etr,1)      AS etr_pct,
    ROUND(k.wsi,2)      AS wsi_per_100,
    ROUND(k.energy,1)   AS energy_kwh_t
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
WHERE k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)
ORDER BY c.region, c.center_name;"""},

    "Alert Threshold Violations": {
        "category": "Alerts",
        "description": "Identify all centers currently breaching any KPI threshold in the latest month.",
        "sql": """\
SELECT
    c.center_name,
    c.region,
    c.center_type,
    'MRR'       AS kpi,
    ROUND(k.mrr,2) AS value,
    86.0           AS threshold,
    'below target' AS direction
FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi) AND k.mrr < 83

UNION ALL
SELECT c.center_name, c.region, c.center_type,
    'Contamination', ROUND(k.contam,2), 8.0, 'above threshold'
FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi) AND k.contam > 8

UNION ALL
SELECT c.center_name, c.region, c.center_type,
    'Downtime', ROUND(k.downtime,2), 7.0, 'above threshold'
FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi) AND k.downtime > 7

UNION ALL
SELECT c.center_name, c.region, c.center_type,
    'Safety WSI', ROUND(k.wsi,2), 1.5, 'above threshold'
FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi) AND k.wsi > 1.5

UNION ALL
SELECT c.center_name, c.region, c.center_type,
    'Turnover', ROUND(k.etr,2), 20.0, 'above threshold'
FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
WHERE k.report_month=(SELECT MAX(report_month) FROM monthly_kpi) AND k.etr > 20

ORDER BY kpi, value DESC;"""},
}

CAT_COLORS = {
    "Operational": "#3a8ee0", "Environmental": "#1e7a49",
    "Workforce": "#e09d20",   "Financial": "#8b5cf6",
    "Geo / Map": "#1d9e75",   "Scorecard": "#0f6e56",
    "Alerts": "#d94a4a",
}

# ── Custom query templates (seed data for the builder) ─────────────────────────
CUSTOM_TEMPLATES = {
    "— blank —": "",
    "Top 5 centers by MRR (latest month)": """\
SELECT c.center_name, c.region, c.center_type, ROUND(k.mrr,2) AS mrr_pct
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
WHERE k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)
ORDER BY mrr_pct DESC
LIMIT 5;""",
    "Centers with contamination > 7%": """\
SELECT c.center_name, c.region, c.center_type,
       ROUND(k.contam,2) AS contamination_pct,
       k.report_month
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
WHERE k.contam > 7.0
ORDER BY k.contam DESC;""",
    "Monthly revenue trend for a specific region": """\
SELECT k.report_month,
       ROUND(SUM(k.revenue),0) AS total_revenue_k,
       ROUND(SUM(k.opex),0)    AS total_opex_k,
       ROUND(SUM(k.revenue-k.opex),0) AS net_margin_k
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
WHERE c.region = 'NYC Metro'   -- change region here
GROUP BY k.report_month
ORDER BY k.report_month;""",
    "Average KPIs by center type": """\
SELECT c.center_type,
       ROUND(AVG(k.mrr),1)      AS avg_mrr,
       ROUND(AVG(k.wdr),1)      AS avg_wdr,
       ROUND(AVG(k.contam),2)   AS avg_contam,
       ROUND(AVG(k.downtime),2) AS avg_downtime,
       ROUND(AVG(k.css),2)      AS avg_css,
       ROUND(AVG(k.etr),1)      AS avg_etr,
       ROUND(AVG(k.energy),1)   AS avg_energy_kwh_t,
       COUNT(DISTINCT c.center_id) AS n_centers
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
GROUP BY c.center_type
ORDER BY avg_mrr DESC;""",
    "Compare two centers side-by-side": """\
SELECT k.report_month,
       MAX(CASE WHEN c.center_id='C001' THEN ROUND(k.mrr,1) END) AS brooklyn_mrr,
       MAX(CASE WHEN c.center_id='C005' THEN ROUND(k.mrr,1) END) AS manhattan_mrr,
       MAX(CASE WHEN c.center_id='C001' THEN ROUND(k.css,2) END) AS brooklyn_css,
       MAX(CASE WHEN c.center_id='C005' THEN ROUND(k.css,2) END) AS manhattan_css
FROM monthly_kpi k
JOIN centers c ON c.center_id = k.center_id
WHERE c.center_id IN ('C001','C005')
GROUP BY k.report_month
ORDER BY k.report_month;""",
    "Material stream recovery summary": """\
SELECT s.material,
       ROUND(SUM(s.recovered_tons),1)  AS total_recovered_tons,
       ROUND(SUM(s.rejected_tons),1)   AS total_rejected_tons,
       ROUND(AVG(s.contamination_pct),2) AS avg_contamination_pct,
       COUNT(DISTINCT s.center_id)     AS n_centers
FROM material_streams s
GROUP BY s.material
ORDER BY total_recovered_tons DESC;""",
    "Centers meeting ALL KPI targets (latest month)": """\
SELECT c.center_name, c.region, c.center_type,
       ROUND(k.mrr,1) AS mrr, ROUND(k.wdr,1) AS wdr,
       ROUND(k.contam,2) AS contam, ROUND(k.downtime,1) AS downtime,
       ROUND(k.css,2) AS css, ROUND(k.te,1) AS te
FROM centers c
JOIN monthly_kpi k ON c.center_id = k.center_id
WHERE k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)
  AND k.mrr      >= 86
  AND k.wdr      >= 80
  AND k.contam   <=  6
  AND k.downtime <=  5
  AND k.css      >= 4.2
  AND k.te       >= 88
ORDER BY c.region;""",
    "Month-over-month KPI change (last 2 months)": """\
WITH ranked AS (
    SELECT k.*, c.center_name, c.region, c.center_type,
           ROW_NUMBER() OVER (PARTITION BY k.center_id ORDER BY k.report_month DESC) AS rn
    FROM monthly_kpi k JOIN centers c ON c.center_id=k.center_id
)
SELECT
    a.center_name, a.region, a.center_type,
    a.report_month AS current_month,
    ROUND(a.mrr - b.mrr, 2)           AS mrr_change,
    ROUND(a.wdr - b.wdr, 2)           AS wdr_change,
    ROUND(a.contam - b.contam, 2)     AS contam_change,
    ROUND(a.downtime - b.downtime, 2) AS downtime_change,
    ROUND(a.css - b.css, 2)           AS css_change
FROM ranked a
JOIN ranked b ON a.center_id = b.center_id AND b.rn = 2
WHERE a.rn = 1
ORDER BY mrr_change DESC;""",
}

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=56)
    st.markdown("### NYS Recycling Centers")
    st.caption("KPI Operations Dashboard")
    st.divider()
    cat_filter = st.multiselect(
        "Filter library by category",
        ["All", "Operational", "Environmental", "Workforce",
         "Financial", "Geo / Map", "Scorecard", "Alerts"],
        default=["All"])
    st.divider()
    st.markdown("**Available tables**")
    for t, desc in [("centers","Master list of 20 centers"),
                    ("monthly_kpi","12-month KPI rows (240 rows)"),
                    ("material_streams","Stream contamination (1,440 rows)"),
                    ("alerts","Pre-seeded threshold alerts")]:
        st.markdown(f"`{t}` — {desc}")
    st.divider()
    st.markdown("**Key column reference**")
    st.caption("""
`mrr` · `wdr` · `ptb` · `downtime`
`wsi` · `css` · `te` · `etr`
`contam` · `energy`
`revenue` · `opex`
`tons_processed` · `tons_diverted`
    """)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📄 SQL Query Library & Custom Query Builder")
st.caption("Run pre-defined KPI queries or build your own SQL against the live in-memory SQLite database")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A — CUSTOM QUERY BUILDER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### ⌨️ Custom Query Builder")
st.markdown("""
Write any `SELECT` statement against the four database tables. Use the **template picker**
below to load a pre-written example, then modify it to suit your analysis.
""")

# Template picker
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    template_choice = st.selectbox(
        "📂 Load a query template",
        list(CUSTOM_TEMPLATES.keys()),
        help="Pick a starter query — it will be loaded into the editor below.")
with col_t2:
    st.markdown("<br>", unsafe_allow_html=True)
    load_template = st.button("Load ↓", use_container_width=True)

# Session state for the editor contents
if "custom_sql_text" not in st.session_state:
    st.session_state.custom_sql_text = "SELECT * FROM centers LIMIT 5;"
if load_template and template_choice != "— blank —":
    st.session_state.custom_sql_text = CUSTOM_TEMPLATES[template_choice]
elif load_template and template_choice == "— blank —":
    st.session_state.custom_sql_text = ""

custom_sql = st.text_area(
    "SQL Editor — write or paste your query here",
    value=st.session_state.custom_sql_text,
    height=180,
    key="custom_sql_editor",
    placeholder="SELECT * FROM centers LIMIT 5;",
    help="Only SELECT statements are permitted.")

# Run options
opt_col1, opt_col2, opt_col3, opt_col4 = st.columns([2, 1, 1, 1])
with opt_col1:
    row_limit = st.slider("Max rows to display", 10, 500, 100, 10)
with opt_col2:
    auto_chart = st.checkbox("Auto-chart numeric columns", value=True)
with opt_col3:
    show_types = st.checkbox("Show column types", value=False)
with opt_col4:
    st.markdown("<br>", unsafe_allow_html=True)
    run_custom = st.button("▶ Run Query", type="primary", use_container_width=True)

if run_custom:
    sql_input = custom_sql.strip()
    if not sql_input:
        st.warning("⚠️ Please enter a SQL query.")
    elif not sql_input.upper().lstrip().startswith("SELECT"):
        st.error("🚫 Only SELECT statements are permitted for security.")
    else:
        try:
            t0 = time.time()
            result = run_query(sql_input)
            elapsed = time.time() - t0
            total_rows = len(result)
            display_df = result.head(row_limit)

            st.success(
                f"✅ Query returned **{total_rows:,} rows** "
                f"({elapsed*1000:.1f} ms) · showing first {min(row_limit, total_rows)}")

            if show_types:
                type_info = pd.DataFrame({"Column": result.columns,
                                          "dtype": [str(d) for d in result.dtypes]})
                with st.expander("Column types"):
                    st.dataframe(type_info, use_container_width=True, hide_index=True)

            st.dataframe(display_df, use_container_width=True, height=320)

            # CSV / clipboard download
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                csv_bytes = result.to_csv(index=False).encode()
                st.download_button(
                    "⬇ Download full result as CSV",
                    data=csv_bytes,
                    file_name="custom_query_result.csv",
                    mime="text/csv",
                    use_container_width=True)
            with dl_col2:
                json_str = result.to_json(orient="records", indent=2)
                st.download_button(
                    "⬇ Download as JSON",
                    data=json_str.encode(),
                    file_name="custom_query_result.json",
                    mime="application/json",
                    use_container_width=True)

            # Auto-chart
            if auto_chart and not display_df.empty:
                num_cols = display_df.select_dtypes(include="number").columns.tolist()
                str_cols = display_df.select_dtypes(include="object").columns.tolist()
                if len(num_cols) >= 1 and len(str_cols) >= 1:
                    st.markdown("#### 📊 Auto-generated Chart")
                    ch_col1, ch_col2, ch_col3 = st.columns(3)
                    with ch_col1:
                        chart_type = st.selectbox(
                            "Chart type",
                            ["Bar", "Line", "Scatter", "Pie/Donut", "Histogram"],
                            key="cq_ctype")
                    with ch_col2:
                        x_col = st.selectbox("X axis / label", str_cols + num_cols, key="cq_x")
                    with ch_col3:
                        y_col = st.selectbox("Y axis / value", num_cols, key="cq_y")

                    color_col = st.selectbox(
                        "Color / group by (optional)",
                        ["None"] + str_cols,
                        key="cq_color")
                    color_arg = None if color_col == "None" else color_col

                    try:
                        if chart_type == "Bar":
                            fig = px.bar(display_df, x=x_col, y=y_col,
                                         color=color_arg, barmode="group",
                                         color_discrete_sequence=px.colors.qualitative.Safe)
                        elif chart_type == "Line":
                            fig = px.line(display_df, x=x_col, y=y_col,
                                          color=color_arg, markers=True,
                                          color_discrete_sequence=px.colors.qualitative.Safe)
                        elif chart_type == "Scatter":
                            fig = px.scatter(display_df, x=x_col, y=y_col,
                                             color=color_arg,
                                             color_discrete_sequence=px.colors.qualitative.Safe)
                        elif chart_type == "Pie/Donut":
                            fig = px.pie(display_df, names=x_col, values=y_col,
                                         hole=0.4,
                                         color_discrete_sequence=px.colors.qualitative.Safe)
                        else:  # Histogram
                            fig = px.histogram(display_df, x=y_col, color=color_arg,
                                               color_discrete_sequence=px.colors.qualitative.Safe)
                        fig.update_layout(height=380, margin=dict(t=30, b=10))
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as chart_err:
                        st.info(f"Chart could not be rendered: {chart_err}")

        except Exception as e:
            st.error(f"**SQL Error:** {e}")
            st.info("Tip: Check column names with `PRAGMA table_info(table_name);`")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B — PRE-DEFINED QUERY LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
show_all_cats = "All" in cat_filter or not cat_filter
filtered_lib = {
    k: v for k, v in SQL_LIBRARY.items()
    if show_all_cats or v["category"] in cat_filter}

st.markdown(f"### 📚 Pre-defined Query Library ({len(filtered_lib)} queries)")
st.caption("Click **▶ Run** inside any expander to execute the query live and download results.")

# Category summary badges
badge_counts = {}
for v in SQL_LIBRARY.values():
    badge_counts[v["category"]] = badge_counts.get(v["category"], 0) + 1
badge_html = " ".join(
    f'<span style="background:{CAT_COLORS.get(cat,"#888")}22;color:{CAT_COLORS.get(cat,"#888")};'
    f'padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:4px">'
    f'{cat} ({n})</span>'
    for cat, n in sorted(badge_counts.items()))
st.markdown(badge_html, unsafe_allow_html=True)
st.markdown("")

for name, qdef in filtered_lib.items():
    cat   = qdef["category"]
    color = CAT_COLORS.get(cat, "#888")
    with st.expander(f"**{name}**  ·  {qdef['description']}"):
        hdr_col, run_col = st.columns([5, 1])
        with hdr_col:
            st.markdown(
                f'<span style="background:{color}22;color:{color};padding:2px 9px;'
                f'border-radius:20px;font-size:11px;font-weight:600">{cat}</span>',
                unsafe_allow_html=True)
        with run_col:
            run_btn = st.button("▶ Run", key=f"run_{name}", use_container_width=True)

        st.code(qdef["sql"], language="sql")

        if run_btn:
            try:
                t0  = time.time()
                res = run_query(qdef["sql"])
                elapsed = time.time() - t0
                st.success(f"✅ {len(res):,} rows · {elapsed*1000:.1f} ms")
                st.dataframe(res, use_container_width=True, height=300)

                # Quick chart for numeric results
                num_c = res.select_dtypes(include="number").columns.tolist()
                str_c = res.select_dtypes(include="object").columns.tolist()
                if len(num_c) >= 1 and len(str_c) >= 1:
                    try:
                        qfig = px.bar(
                            res.head(30), x=str_c[0], y=num_c[0],
                            color=str_c[1] if len(str_c) > 1 else None,
                            color_discrete_sequence=px.colors.qualitative.Safe,
                            title=f"{name} — {num_c[0]} by {str_c[0]}")
                        qfig.update_layout(height=300, margin=dict(t=40, b=0))
                        st.plotly_chart(qfig, use_container_width=True)
                    except Exception:
                        pass

                # Downloads
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button(
                        "⬇ CSV", res.to_csv(index=False).encode(),
                        file_name=f"{name.replace(' ','_')}.csv",
                        mime="text/csv", key=f"dl_csv_{name}")
                with dl2:
                    st.download_button(
                        "⬇ JSON", res.to_json(orient="records", indent=2).encode(),
                        file_name=f"{name.replace(' ','_')}.json",
                        mime="application/json", key=f"dl_json_{name}")
            except Exception as e:
                st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION C — SCHEMA BROWSER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🗂️ Schema Browser")

tables = ["centers", "monthly_kpi", "material_streams", "alerts"]
sel_table = st.selectbox("Inspect table", tables)

try:
    t_count = run_query(f"SELECT COUNT(*) AS n FROM {sel_table}").iloc[0]["n"]
    preview = run_query(f"SELECT * FROM {sel_table} LIMIT 20")
    info    = run_query(f"PRAGMA table_info({sel_table})")

    sb1, sb2 = st.columns([2, 1])
    with sb1:
        st.caption(f"`{sel_table}` — {t_count:,} rows · showing first 20")
        st.dataframe(preview, use_container_width=True, height=280)
    with sb2:
        st.caption("Column definitions")
        st.dataframe(
            info[["name", "type", "notnull", "pk"]].rename(
                columns={"name": "Column", "type": "Type",
                         "notnull": "Not Null", "pk": "PK"}),
            use_container_width=True, height=280, hide_index=True)

    # Numeric summary
    num_preview = preview.select_dtypes(include="number")
    if not num_preview.empty:
        with st.expander(f"📊 Numeric summary for `{sel_table}`"):
            st.dataframe(
                num_preview.describe().round(3),
                use_container_width=True)
except Exception as e:
    st.error(str(e))
