# On-Chain Risk & Anomaly Monitoring Pipeline

An automated data pipeline, embedded SQLite database engine, and interactive visual dashboard built in Python to ingest, clean, store, and analyze blockchain transaction data for multi-factor risk assessment and anomaly detection.

## Core Features
* **Data Ingestion & Simulation:** Simulates and structures raw blockchain transactions (Senders, Receivers, Values, Gas Usage).
* **Embedded SQL Engine & Relational Joins:** Pushes transaction records into a local SQLite database and executes multi-table associations (`JOIN`) against wallet risk-tier reference tables.
* **Advanced SQL Window Functions & Ranking:** Implements analytical window functions (`SUM() OVER (PARTITION BY ...)` and `RANK() OVER (...)`) to track rolling cumulative transaction volumes and intra-wallet transaction ranking.
* **Multi-Factor Risk Indicators:** Computes dynamic metrics like transaction frequency per sender and gas usage anomalies alongside Z-Score statistical detection.
* **Interactive Risk Dashboard:** Generates a multi-chart visual report using Plotly featuring distribution histograms, risk scatter plots, correlation analysis, and dynamic summary KPIs.

## Tech Stack
* Language: Python, SQL
* Database: SQLite
* Libraries: Pandas, NumPy, Plotly

## Getting Started
1. Clone the repository:
   ```bash
   git clone [https://github.com/shashini-karunarathna/crypto-risk-pipeline.git](https://github.com/shashini-karunarathna/crypto-risk-pipeline.git)