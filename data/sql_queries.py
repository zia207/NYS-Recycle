"""
sql_queries.py
Pre-defined SQL queries used across all KPI pages.
Each function returns a pandas DataFrame.
"""

from data.db_engine import run_query


# ── Centers ────────────────────────────────────────────────────────────────────

def q_centers_all(center_type="All", region="All") -> object:
    where = []
    params = []
    if center_type != "All":
        where.append("center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("region = ?")
        params.append(region)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    return run_query(f"SELECT * FROM centers {clause} ORDER BY region, center_name", params)


# ── Latest-month KPI snapshot ──────────────────────────────────────────────────

def q_latest_kpi(center_type="All", region="All") -> object:
    where = ["k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)"]
    params = []
    if center_type != "All":
        where.append("c.center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = "WHERE " + " AND ".join(where)
    sql = f"""
        SELECT
            c.center_id, c.center_name, c.city, c.region, c.center_type,
            c.latitude, c.longitude,
            k.mrr, k.wdr, k.ptb, k.downtime, k.wsi,
            k.css, k.te, k.etr, k.contam, k.energy,
            k.revenue, k.opex,
            ROUND(k.revenue - k.opex, 0)               AS net_margin,
            ROUND((k.revenue-k.opex)*100.0/k.revenue,1) AS margin_pct,
            k.tons_processed, k.tons_diverted,
            ROUND(
              (CASE WHEN k.mrr   >=86 THEN 30 ELSE k.mrr/86.0*30 END) +
              (CASE WHEN k.wdr   >=80 THEN 20 ELSE k.wdr/80.0*20 END) +
              (CASE WHEN k.contam<=6  THEN 15 ELSE 6.0/k.contam*15 END) +
              (k.css/5.0*20) +
              (CASE WHEN k.te    >=88 THEN 15 ELSE k.te/88.0*15 END)
            , 1) AS composite_score
        FROM centers c
        JOIN monthly_kpi k ON c.center_id = k.center_id
        {clause}
        ORDER BY composite_score DESC
    """
    return run_query(sql, params)


# ── Monthly trend for one or all centers ──────────────────────────────────────

def q_monthly_trend(center_id=None, kpi_col="mrr", center_type="All", region="All") -> object:
    where = []
    params = []
    if center_id:
        where.append("k.center_id = ?")
        params.append(center_id)
    if center_type != "All":
        where.append("c.center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT
            k.report_month,
            c.center_name, c.region, c.center_type,
            ROUND(AVG(k.{kpi_col}),2) AS kpi_value
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        {clause}
        GROUP BY k.report_month, c.center_name, c.region, c.center_type
        ORDER BY k.report_month
    """
    return run_query(sql, params)


def q_monthly_statewide(kpi_col="mrr") -> object:
    sql = f"""
        SELECT
            report_month,
            ROUND(AVG({kpi_col}),2) AS avg_val,
            ROUND(MIN({kpi_col}),2) AS min_val,
            ROUND(MAX({kpi_col}),2) AS max_val
        FROM monthly_kpi
        GROUP BY report_month
        ORDER BY report_month
    """
    return run_query(sql)


def q_monthly_by_type(kpi_col="mrr") -> object:
    sql = f"""
        SELECT
            k.report_month,
            c.center_type,
            ROUND(AVG(k.{kpi_col}),2) AS avg_val
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        GROUP BY k.report_month, c.center_type
        ORDER BY k.report_month
    """
    return run_query(sql)


def q_monthly_by_region(kpi_col="wdr") -> object:
    sql = f"""
        SELECT
            k.report_month,
            c.region,
            ROUND(AVG(k.{kpi_col}),2) AS avg_val
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        GROUP BY k.report_month, c.region
        ORDER BY k.report_month
    """
    return run_query(sql)


# ── Material streams ───────────────────────────────────────────────────────────

def q_contamination_by_stream(region="All") -> object:
    where = []
    params = []
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT
            s.material,
            c.region,
            ROUND(AVG(s.contamination_pct),2) AS avg_contam
        FROM material_streams s
        JOIN centers c ON c.center_id = s.center_id
        {clause}
        GROUP BY s.material, c.region
        ORDER BY avg_contam DESC
    """
    return run_query(sql, params)


def q_contamination_by_stream_type() -> object:
    return run_query("""
        SELECT
            s.material,
            c.center_type,
            ROUND(AVG(s.contamination_pct),2) AS avg_contam
        FROM material_streams s
        JOIN centers c ON c.center_id = s.center_id
        GROUP BY s.material, c.center_type
        ORDER BY s.material, avg_contam DESC
    """)


# ── Financial ──────────────────────────────────────────────────────────────────

def q_financial_monthly(center_type="All", region="All") -> object:
    where = []
    params = []
    if center_type != "All":
        where.append("c.center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT
            k.report_month,
            ROUND(SUM(k.revenue),0)  AS total_revenue,
            ROUND(SUM(k.opex),0)     AS total_opex,
            ROUND(SUM(k.revenue-k.opex),0) AS net_margin,
            ROUND(AVG((k.revenue-k.opex)*100.0/k.revenue),1) AS avg_margin_pct,
            ROUND(SUM(k.opex)/SUM(k.tons_processed),2) AS cost_per_ton
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        {clause}
        GROUP BY k.report_month
        ORDER BY k.report_month
    """
    return run_query(sql, params)


def q_cost_per_ton_by_type() -> object:
    return run_query("""
        SELECT
            c.center_type,
            ROUND(AVG(k.opex / k.tons_processed),2) AS avg_cost_per_ton
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        GROUP BY c.center_type
        ORDER BY avg_cost_per_ton DESC
    """)


# ── Workforce ──────────────────────────────────────────────────────────────────

def q_workforce_monthly_by_region() -> object:
    return run_query("""
        SELECT
            k.report_month,
            c.region,
            ROUND(AVG(k.etr),2) AS avg_etr,
            ROUND(AVG(k.wsi),2) AS avg_wsi
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        GROUP BY k.report_month, c.region
        ORDER BY k.report_month
    """)


# ── Scorecard ──────────────────────────────────────────────────────────────────

def q_scorecard_summary(center_type="All", region="All") -> object:
    where = ["k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)"]
    params = []
    if center_type != "All":
        where.append("c.center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = "WHERE " + " AND ".join(where)
    sql = f"""
        SELECT
            ROUND(AVG(k.mrr),1)      AS avg_mrr,
            ROUND(AVG(k.wdr),1)      AS avg_wdr,
            ROUND(AVG(k.ptb),2)      AS avg_ptb,
            ROUND(AVG(k.downtime),1) AS avg_downtime,
            ROUND(AVG(k.wsi),2)      AS avg_wsi,
            ROUND(AVG(k.css),2)      AS avg_css,
            ROUND(AVG(k.te),1)       AS avg_te,
            ROUND(AVG(k.etr),1)      AS avg_etr,
            ROUND(AVG(k.contam),1)   AS avg_contam,
            ROUND(AVG(k.energy),1)   AS avg_energy
        FROM monthly_kpi k
        JOIN centers c ON c.center_id = k.center_id
        {clause}
    """
    return run_query(sql, params)


# ── Alerts ─────────────────────────────────────────────────────────────────────

def q_alerts(level=None) -> object:
    if level:
        return run_query("SELECT * FROM alerts WHERE level=? ORDER BY created_at DESC", (level,))
    return run_query("SELECT * FROM alerts ORDER BY CASE level WHEN 'critical' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END, created_at DESC")


# ── Map data ───────────────────────────────────────────────────────────────────

def q_map_data(metric="mrr", center_type="All", region="All") -> object:
    safe_metrics = {"mrr","wdr","ptb","downtime","wsi","css","te","etr","contam","energy"}
    col = metric if metric in safe_metrics else "mrr"
    where = ["k.report_month = (SELECT MAX(report_month) FROM monthly_kpi)"]
    params = []
    if center_type != "All":
        where.append("c.center_type = ?")
        params.append(center_type)
    if region != "All":
        where.append("c.region = ?")
        params.append(region)
    clause = "WHERE " + " AND ".join(where)
    sql = f"""
        SELECT
            c.center_id, c.center_name, c.city, c.region, c.center_type,
            c.latitude, c.longitude,
            k.{col} AS metric_value,
            k.mrr, k.wdr, k.css, k.contam, k.downtime, k.te, k.etr, k.energy,
            k.revenue, k.opex,
            ROUND(
              (CASE WHEN k.mrr   >=86 THEN 30 ELSE k.mrr/86.0*30 END) +
              (CASE WHEN k.wdr   >=80 THEN 20 ELSE k.wdr/80.0*20 END) +
              (CASE WHEN k.contam<=6  THEN 15 ELSE 6.0/k.contam*15 END) +
              (k.css/5.0*20) +
              (CASE WHEN k.te    >=88 THEN 15 ELSE k.te/88.0*15 END)
            , 1) AS composite_score
        FROM centers c
        JOIN monthly_kpi k ON c.center_id = k.center_id
        {clause}
        ORDER BY composite_score DESC
    """
    return run_query(sql, params)
