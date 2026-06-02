"""
db_engine.py
Builds an in-memory SQLite database populated with simulated NYS recycling
center data, and exposes a run_query() helper used by all dashboard pages.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta
import random, math

random.seed(42)
np.random.seed(42)

# ── Center master data ─────────────────────────────────────────────────────────
CENTERS = [
    ("C001","NYC Brooklyn MRF",       "Brooklyn",        "NYC Metro",    "Municipal",  40.6501,-73.9496),
    ("C002","Queens Materials Recovery","Queens",         "NYC Metro",    "Commercial", 40.7282,-73.7949),
    ("C003","Bronx E-Waste Hub",       "Bronx",           "NYC Metro",    "Electronic", 40.8374,-73.8651),
    ("C004","Staten Island Hazmat",    "Staten Island",   "NYC Metro",    "Hazardous",  40.5795,-74.1502),
    ("C005","Manhattan Recycling Co.", "Manhattan",       "NYC Metro",    "Commercial", 40.7580,-73.9855),
    ("C006","Buffalo MRF",             "Buffalo",         "Western NY",   "Municipal",  42.8864,-78.8784),
    ("C007","Rochester Green Materials","Rochester",      "Western NY",   "Commercial", 43.1548,-77.6163),
    ("C008","Niagara Recycling Center","Niagara Falls",   "Western NY",   "Municipal",  43.0962,-79.0377),
    ("C009","Syracuse Central MRF",    "Syracuse",        "Central NY",   "Municipal",  43.0481,-76.1474),
    ("C010","Utica Materials Hub",     "Utica",           "Central NY",   "Commercial", 43.1009,-75.2327),
    ("C011","Albany Capital Recyclers","Albany",          "Capital Region","Municipal", 42.6526,-73.7562),
    ("C012","Troy Green Solutions",    "Troy",            "Capital Region","Commercial",42.7284,-73.6918),
    ("C013","Schenectady E-Waste",     "Schenectady",     "Capital Region","Electronic",42.8142,-73.9396),
    ("C014","Plattsburgh North MRF",   "Plattsburgh",     "North Country","Municipal",  44.6995,-73.4529),
    ("C015","Watertown Regional",      "Watertown",       "North Country","Commercial", 43.9748,-75.9108),
    ("C016","Long Island South Shore MRF","Hempstead",   "NYC Metro",    "Municipal",  40.7062,-73.6187),
    ("C017","Yonkers Metro Recycling", "Yonkers",         "NYC Metro",    "Commercial", 40.9312,-73.8988),
    ("C018","Binghamton Southern Tier","Binghamton",      "Central NY",   "Municipal",  42.0987,-75.9179),
    ("C019","Elmira Chemung MRF",      "Elmira",          "Central NY",   "Commercial", 42.0898,-76.8077),
    ("C020","Saratoga Springs Green Hub","Saratoga Springs","Capital Region","Municipal",43.0831,-73.7846),
]

# Base KPI targets per center type
BASE_KPI = {
    "Municipal":   dict(mrr=85, wdr=80, ptb=3.8, downtime=5.0, wsi=1.0, css=4.2, te=89, etr=13, contam=5.5, energy=29),
    "Commercial":  dict(mrr=83, wdr=78, ptb=4.2, downtime=5.5, wsi=1.1, css=4.1, te=87, etr=15, contam=6.5, energy=32),
    "Electronic":  dict(mrr=79, wdr=75, ptb=5.4, downtime=6.3, wsi=0.6, css=4.0, te=83, etr=17, contam=3.2, energy=43),
    "Hazardous":   dict(mrr=72, wdr=68, ptb=6.7, downtime=8.0, wsi=2.0, css=3.8, te=76, etr=22, contam=2.9, energy=55),
}

# Per-center multipliers (simulate variation)
CENTER_MULT = {
    "C001": 1.02, "C002": 0.98, "C003": 0.96, "C004": 0.94,
    "C005": 1.07, "C006": 1.01, "C007": 1.03, "C008": 0.93,
    "C009": 0.99, "C010": 0.91, "C011": 1.05, "C012": 1.02,
    "C013": 0.97, "C014": 0.88, "C015": 0.92, "C016": 1.04,
    "C017": 1.02, "C018": 0.94, "C019": 0.90, "C020": 1.08,
}

MONTHS = pd.date_range("2024-01-01", periods=12, freq="MS")
MATERIAL_STREAMS = ["Paper","Plastics","Glass","Metals","Electronics","Hazardous"]


def _jitter(base, pct=0.06):
    return base * (1 + random.uniform(-pct, pct))


def build_database() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    cur = con.cursor()

    # ── centers table ──────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE centers (
            center_id TEXT PRIMARY KEY,
            center_name TEXT,
            city TEXT,
            region TEXT,
            center_type TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    cur.executemany("INSERT INTO centers VALUES (?,?,?,?,?,?,?)", CENTERS)

    # ── monthly_kpi table ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE monthly_kpi (
            center_id TEXT,
            report_month TEXT,
            mrr REAL, wdr REAL, ptb REAL, downtime REAL,
            wsi REAL, css REAL, te REAL, etr REAL,
            contam REAL, energy REAL,
            revenue REAL, opex REAL,
            tons_processed REAL, tons_diverted REAL,
            PRIMARY KEY (center_id, report_month)
        )
    """)

    rows = []
    for cid, cname, city, region, ctype, lat, lon in CENTERS:
        base = BASE_KPI[ctype]
        m = CENTER_MULT[cid]
        for i, mo in enumerate(MONTHS):
            trend = 1 + i * 0.003          # slight improvement trend
            rows.append((
                cid, mo.strftime("%Y-%m-%d"),
                round(_jitter(base["mrr"]  * m * trend), 2),
                round(_jitter(base["wdr"]  * m * trend), 2),
                round(_jitter(base["ptb"]  / (m * trend), 0.08), 2),
                round(_jitter(base["downtime"] / (m * trend), 0.1), 2),
                round(_jitter(base["wsi"]  / (m * trend), 0.15), 2),
                round(min(5.0, _jitter(base["css"] * m * trend, 0.04)), 2),
                round(_jitter(base["te"]   * m * trend), 2),
                round(_jitter(base["etr"]  / (m * trend), 0.1), 2),
                round(_jitter(base["contam"] / (m * trend), 0.12), 2),
                round(_jitter(base["energy"] / (m * trend), 0.08), 2),
                round(_jitter(m * 2200 * (1 + i*0.004)), 0),  # revenue $K
                round(_jitter(m * 1650 * (1 + i*0.002)), 0),  # opex $K
                round(_jitter(m * 420  * trend), 1),           # tons processed
                round(_jitter(m * 340  * trend), 1),           # tons diverted
            ))
    cur.executemany("INSERT INTO monthly_kpi VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)

    # ── material_streams table ─────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE material_streams (
            center_id TEXT, report_month TEXT,
            material TEXT, contamination_pct REAL,
            recovered_tons REAL, rejected_tons REAL
        )
    """)
    stream_base = {"Paper":5.5,"Plastics":7.2,"Glass":3.8,"Metals":3.1,"Electronics":3.5,"Hazardous":2.4}
    srows = []
    for cid, *_ , ctype, lat, lon in CENTERS:
        for mo in MONTHS:
            for mat in MATERIAL_STREAMS:
                b = stream_base[mat] * CENTER_MULT[cid]
                c = round(_jitter(b, 0.15), 2)
                rt = round(_jitter(60 * CENTER_MULT[cid]), 1)
                srows.append((cid, mo.strftime("%Y-%m-%d"), mat, c, rt, round(rt*c/100, 1)))
    cur.executemany("INSERT INTO material_streams VALUES (?,?,?,?,?,?)", srows)

    # ── alerts table ───────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            center_id TEXT, center_name TEXT,
            level TEXT, kpi TEXT, message TEXT,
            value REAL, threshold REAL,
            created_at TEXT
        )
    """)
    alert_rows = [
        ("C014","Plattsburgh North MRF","critical","Contamination Rate",
         "Contamination at 10.2% — exceeds 8% threshold for 3 consecutive weeks.",10.2,8.0,"2025-01-22"),
        ("C010","Utica Materials Hub","critical","Equipment Downtime",
         "Downtime rate reached 8.4%. Primary baler offline; estimated repair 48 h.",8.4,7.0,"2025-01-22"),
        ("C015","Watertown Regional","critical","Safety Incidents",
         "2 minor injuries reported. OSHA review scheduled. Lost workdays: 3.",2.1,1.5,"2025-01-21"),
        ("C008","Niagara Recycling Center","warning","MRR",
         "MRR at 78%, below 86% state target. Processing queue backup detected.",78.0,86.0,"2025-01-22"),
        ("C014","Plattsburgh North MRF","warning","Employee Turnover",
         "Turnover at 24%, above 20% threshold. HR review initiated.",24.0,20.0,"2025-01-21"),
        ("C004","Staten Island Hazmat","warning","Energy Consumption",
         "Energy intensity increased 8% MoM across hazardous material centers.",58.0,50.0,"2025-01-20"),
        ("C009","Syracuse Central MRF","warning","Transportation Efficiency",
         "TE decreased from 88% to 79% due to fuel cost increases.",79.0,85.0,"2025-01-20"),
        ("C010","Utica Materials Hub","warning","Customer Satisfaction",
         "CSS dropped to 3.7 after service delays. Follow-up survey dispatched.",3.7,4.0,"2025-01-19"),
        ("C005","Manhattan Recycling Co.","ok","Composite Score",
         "All KPIs green. Composite score 93/100. Nominated for best-practice review.",93.0,85.0,"2025-01-22"),
        ("C020","Saratoga Springs Green Hub","ok","Composite Score",
         "Score 92/100. Energy efficiency: 24 kWh/ton. All metrics at target.",92.0,85.0,"2025-01-22"),
        ("C011","Albany Capital Recyclers","ok","Safety Milestone",
         "180 days without recordable safety incident. Team recognition scheduled.",0.0,1.0,"2025-01-22"),
    ]
    cur.executemany(
        "INSERT INTO alerts (center_id,center_name,level,kpi,message,value,threshold,created_at) VALUES (?,?,?,?,?,?,?,?)",
        alert_rows
    )

    con.commit()
    return con


# Singleton connection
_CON: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    global _CON
    if _CON is None:
        _CON = build_database()
    return _CON


def run_query(sql: str, params=()) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_connection(), params=params)
