# On-Chain Risk & Anomaly Monitoring Pipeline

An enterprise-grade, modular data pipeline built in Python and SQLite designed to ingest, clean, store, and analyze blockchain transaction data. It features a decoupled architecture supporting both synthetic backtesting and live Ethereum JSON-RPC mainnet ingestion.

## Core Architecture & Phases
* **Phase 1 (Analytical Core):** Embedded SQLite database engine executing multi-table relational joins (`JOIN`), advanced window functions (`SUM() OVER`, `RANK() OVER`), and Z-score statistical anomaly detection.
* **Phase 2 (Live Ingestion Layer):** Real-time blockchain data connector utilizing JSON-RPC over `requests` to ingest live mainnet transaction payloads, paired with a robust local fallback mechanism.
* **Interactive Intelligence Dashboard:** Generates dynamic, multi-chart visual reports (`risk_monitoring_dashboard.html` & `live_risk_dashboard.html`) using Plotly.

## Tech Stack
* Language: Python, SQL
* Database: SQLite
* Libraries & Frameworks: Pandas, NumPy, Plotly, Requests

## Getting Started
1. Clone the repository:
   ```bash
   git clone [https://github.com/shashini-karunarathna/crypto-risk-pipeline.git](https://github.com/shashini-karunarathna/crypto-risk-pipeline.git)






   