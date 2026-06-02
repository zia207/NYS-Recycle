# NYS Recycling Center KPI Dashboard

A Streamlit application was developed to demonstrate a comprehensive KPI tracking and reporting framework using simulated data from 20 recycling centers across five regions of New York State (NYS). The platform provides interactive dashboards, performance monitoring, data visualization, and automated reporting capabilities to support operational analysis and decision-making.

## Quick Start

```bash
cd /home/zia207/WebSites/Python_Website/data-visualization-dashboard/Recycle_centre/

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Project Structure

```
Recycle_centre/
├── app.py                          # Home / landing page
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Theme: green palette
├── data/
│   ├── __init__.py
│   ├── db_engine.py                # SQLite in-memory DB + run_query()
│   └── sql_queries.py              # All predefined SQL KPI queries
└── pages/
    ├── 01_Executive_Summary.py     # Statewide overview
    ├── 02_Interactive_Map.py       # Folium/OSM with KPI markers
    ├── 03_Operational_KPIs.py      # PTB, downtime, transport efficiency
    ├── 04_Environmental_KPIs.py    # WDR, contamination, energy
    ├── 05_Financial_KPIs.py        # Revenue, opex, margin, cost/ton
    ├── 06_Workforce_KPIs.py        # Turnover, safety incidents
    ├── 07_KPI_Scorecard.py         # Radar + progress bars
    ├── 08_Alerts.py                # Threshold alerts system
    └── 09_SQL_Queries.py           # Interactive SQL runner + schema browser
```

## KPI Dimensions

| KPI | Category | Target |
|-----|----------|--------|
| Material Recovery Rate | Operational | ≥ 86% |
| Processing Time / Batch | Operational | ≤ 4.0 h |
| Equipment Downtime | Operational | ≤ 5% |
| Workplace Safety Incidents | Workforce | ≤ 1.0/100 |
| Waste Diversion Rate | Environmental | ≥ 80% |
| Customer Satisfaction Score | Financial | ≥ 4.2/5 |
| Transportation Efficiency | Operational | ≥ 88% |
| Employee Turnover Rate | Workforce | ≤ 15% |
| Contamination Rate | Environmental | ≤ 6% |
| Energy Consumption | Environmental | ≤ 30 kWh/t |

## Data

All data is simulated in-memory via SQLite at startup. The `data/db_engine.py`
module generates 20 centers × 12 months × all KPI columns, plus material stream
contamination records and a pre-seeded alerts table.

## Centers (20 total)

| Region | Centers |
|--------|---------|
| NYC Metro | Brooklyn, Queens, Bronx, Staten Island, Manhattan, Long Island, Yonkers |
| Western NY | Buffalo, Rochester, Niagara Falls |
| Central NY | Syracuse, Utica, Binghamton, Elmira |
| Capital Region | Albany, Troy, Schenectady, Saratoga Springs |
| North Country | Plattsburgh, Watertown |
