import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Initializing On-Chain Risk Pipeline & Embedded SQL Engine...")

# 1. Simulate Transaction Data (matching your blockchain indexer structure)
np.random.seed(42)
n_transactions = 500

senders = [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 40))}" for _ in range(50)]
sender_pool = [np.random.choice(senders) for _ in range(n_transactions)]

data = {
    "TxHash": [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 64))}" for _ in range(n_transactions)],
    "Sender": sender_pool,
    "Receiver": [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 40))}" for _ in range(n_transactions)],
    "Value_ETH": np.random.exponential(scale=0.5, size=n_transactions),
    "Gas_Used": np.random.randint(21000, 150000, size=n_transactions)
}

df = pd.DataFrame(data)

# Inject intentional high-value spikes to simulate suspicious whale movements / risks
df.loc[15, "Value_ETH"] = 52.4
df.loc[132, "Value_ETH"] = 68.9
df.loc[410, "Value_ETH"] = 41.2

# 2. Store Data into Local SQLite Database & Execute Advanced SQL Queries
conn = sqlite3.connect("crypto_risk.db")
cursor = conn.cursor()

# Push Pandas DataFrame directly into a SQL table named 'transactions'
df.to_sql("transactions", conn, if_exists="replace", index=False)

# Create a secondary reference table for Multi-Table Association (JOINs)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_risk_tags (
        Sender TEXT PRIMARY KEY,
        Risk_Tier TEXT
    )
""")

# Tag a subset of senders with risk profiles
unique_senders = df["Sender"].unique()[:15]
sample_tags = [(s, np.random.choice(["High-Risk Monitor", "Standard", "VIP Watchlist"])) for s in unique_senders]
cursor.executemany("INSERT OR REPLACE INTO wallet_risk_tags (Sender, Risk_Tier) VALUES (?, ?)", sample_tags)
conn.commit()

# Advanced SQL Query: Multi-table JOIN + Window Function (Running Cumulative Volume)
advanced_sql_query = """
SELECT 
    t.TxHash,
    t.Sender,
    t.Value_ETH,
    COALESCE(w.Risk_Tier, 'Unclassified') AS Risk_Tier,
    SUM(t.Value_ETH) OVER (PARTITION BY t.Sender ORDER BY t.TxHash) AS Running_Cumulative_Volume
FROM transactions t
LEFT JOIN wallet_risk_tags w ON t.Sender = w.Sender
LIMIT 10;
"""

print("\n--- Executing Advanced SQL Query (Multi-Table Join & Window Function) ---")
sql_result_df = pd.read_sql_query(advanced_sql_query, conn)
print(sql_result_df.to_string(index=False))
print("-------------------------------------------------------------------------\n")

# 3. Statistical Risk Backtesting (Z-Score Anomaly Detection)
mean_val = df["Value_ETH"].mean()
std_val = df["Value_ETH"].std()

df["Z_Score"] = (df["Value_ETH"] - mean_val) / std_val
df["Is_Anomalous"] = df["Z_Score"] > 3

total_volume = df["Value_ETH"].sum()
anomaly_count = df["Is_Anomalous"].sum()

print(f"[SUCCESS] Analyzed {len(df)} transactions via SQL engine.")
print(f"-> Total Volume Tracked: {total_volume:.2f} ETH")
print(f"-> High-Risk Anomalies Flagged: {anomaly_count}")

# 4. Build Interactive Visual Dashboard using Plotly
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Transaction Value Distribution", "Anomalous Volume Spikes", "Gas Usage vs Transfer Value", "Risk Summary KPIs"),
    specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "xy"}, {"type": "table"}]]
)

# Chart 1: Distribution Histogram
fig.add_trace(
    go.Histogram(x=df["Value_ETH"], name="Value Distribution", marker_color="#3366cc"),
    row=1, col=1
)

# Chart 2: Scatter plot highlighting risk anomalies in red
colors = ['red' if x else 'blue' for x in df["Is_Anomalous"]]
fig.add_trace(
    go.Scatter(
        x=df.index, y=df["Value_ETH"],
        mode='markers',
        marker=dict(color=colors, size=6),
        name="Transactions (Red = Flagged Risk)"
    ),
    row=1, col=2
)

# Chart 3: Gas vs Value Correlation
fig.add_trace(
    go.Scatter(
        x=df["Gas_Used"], y=df["Value_ETH"],
        mode='markers',
        marker=dict(color='purple', opacity=0.5),
        name="Gas vs Value"
    ),
    row=2, col=1
)

# Chart 4: KPI Indicator Table
fig.add_trace(
    go.Table(
        header=dict(values=["Metric", "Value"], fill_color='paleturquoise', align='left'),
        cells=dict(values=[
            ["Total Transactions", "Flagged Anomalies", "Max Value (ETH)", "Mean Value (ETH)"],
            [len(df), anomaly_count, f"{df['Value_ETH'].max():.2f}", f"{mean_val:.2f}"]
        ], fill_color='lavender', align='left')
    ),
    row=2, col=2
)

fig.update_layout(
    title_text="<b>On-Chain Risk & Anomaly Monitoring Dashboard (SQL Integrated)</b>",
    template="plotly_white",
    height=800,
    showlegend=False
)

# Save dashboard as an interactive HTML file
output_file = "risk_monitoring_dashboard.html"
fig.write_html(output_file)
print(f"[SUCCESS] Interactive dashboard generated and saved as '{output_file}'!")
conn.close()

