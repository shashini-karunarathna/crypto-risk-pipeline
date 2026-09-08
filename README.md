# On-Chain Risk & Anomaly Monitoring Pipeline

An automated data pipeline, embedded SQLite database engine, and interactive visual dashboard built in Python to ingest, clean, store, and analyze blockchain transaction data for risk assessment and anomaly detection.

## Core Features
* **Data Ingestion & Simulation:** Simulates and structures raw blockchain transactions (Senders, Receivers, Values, Gas Usage).
* **Embedded SQL Engine & Relational Joins:** Pushes transaction records into a local SQLite database and executes multi-table associations (`JOIN`) against wallet risk-tier reference tables.
* **Advanced SQL Window Functions:** Implements analytical window functions (`SUM() OVER (PARTITION BY ... ORDER BY ...)`) to track rolling cumulative transaction volumes per wallet address.
* **Statistical Risk Backtesting:** Implements Z-Score anomaly detection algorithms to programmatically flag high-risk transfers and volume spikes exceeding statistical thresholds.
* **Interactive Risk Dashboard:** Generates a multi-chart visual report using Plotly featuring distribution histograms, risk scatter plots, correlation analysis, and dynamic summary KPIs.

## Tech Stack
* Language: Python, SQL
* Database: SQLite
* Libraries: Pandas, NumPy, Plotly

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/shashini-karunarathna/crypto-risk-pipeline.git

