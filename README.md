# Hybrid Blockchain Risk Pipeline

An automated Python-based blockchain transaction risk-analysis pipeline supporting live Ethereum JSON-RPC ingestion and synthetic backtesting. The pipeline stores transaction data in SQLite, applies SQL joins and window functions, calculates multi-factor risk indicators, performs statistical anomaly detection, runs automated tests, and generates interactive Plotly dashboards.

## Architecture

Ethereum JSON-RPC
       ↓
Live Transaction Ingestion
       ↓
Validation / Normalization
       ↓
SQLite
       ↓
SQL Analytics
 ├── JOIN
 ├── Window Functions
 └── Ranking
       ↓
Risk Indicators
 ├── Transaction Frequency
 ├── Gas Anomaly
 ├── Z-Score
 └── Risk Tier
       ↓
Anomaly Detection
       ↓
Plotly Dashboard

## Core Features & Implementation
* **Hybrid Ingestion Layer:** Connects to public Ethereum nodes via JSON-RPC (`requests`) to pull real mainnet block transactions, equipped with an automated fallback mechanism to a robust synthetic backtesting framework if network rate limits or disruptions occur.
* **Embedded SQL Engine & Relational Joins:** Pushes transaction records into local SQLite databases (`crypto_risk_live.db`) and executes multi-table associations against wallet risk-tier reference tables.
* **Advanced SQL Window Functions & Ranking:** Leverages analytical window functions (`SUM() OVER (PARTITION BY ...)` and `RANK() OVER (...)`) to compute rolling cumulative transfer volumes and intra-wallet transaction rankings.
* **Multi-Factor Risk Indicators:** Dynamically calculates transaction frequency per sender, gas usage deviations, and Z-score statistical anomalies.
* **Automated Unit Testing:** Includes an integrated test suite (`tests/test_risk_pipeline.py`) validating SQL window functions and anomaly detection math.
* **Interactive Visual Dashboards:** Compiles multi-chart analytical reports (`risk_monitoring_dashboard.html` & `live_risk_dashboard.html`) utilizing Plotly.

## Tech Stack
* Language: Python, SQL
* Database: SQLite
* Libraries: Pandas, NumPy, Plotly, Requests

## Getting Started
1. Clone the repository:
   ```bash
   git clone [https://github.com/shashini-karunarathna/crypto-risk-pipeline.git](https://github.com/shashini-karunarathna/crypto-risk-pipeline.git)

   