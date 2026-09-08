import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Initializing Advanced On-Chain Risk Pipeline & SQL Engine...")

# 1. Simulate Transaction Data with Realistic Attributes
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

# Inject high-value anomalies / whale spikes
df.loc[15, "Value_ETH"] = 52.4
df.loc[132, "Value_ETH"] = 68.9
df.loc[410, "Value_ETH"] = 41.2

# 2. Compute Enhanced Risk Indicators (Frequency & Gas Spikes)
df["Tx_Frequency"] = df.groupby("Sender")["Sender"].transform("count")
gas_mean = df["Gas_Used"].mean()
gas_std = df["Gas_Used"].std()
df["Gas_Anomaly"] = df["Gas_Used"] > (gas_mean + 2 * gas_std)

# 3. Push Data to Local SQLite Database
conn = sqlite3.connect("crypto_risk.db")
cursor = conn.cursor()

df.to_sql("transactions", conn, if_exists="replace", index=False)

# Create Reference Table for Multi-Table Association
cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_risk_tags (
        Sender TEXT PRIMARY KEY,
        Risk_Tier TEXT
    )
""")

unique_senders = df["Sender"].unique()[:15]
sample_tags = [(s, np.random.choice(["High-Risk Monitor", "Standard", "VIP Watchlist"])) for s in unique_senders]
cursor.executemany("INSERT OR REPLACE INTO wallet_risk_tags (Sender, Risk_Tier) VALUES (?, ?)", sample_tags)
conn.commit()

# 4. Advanced SQL Query: Multi-table JOIN, Window Functions (Running Cumulative & Rank)
advanced_sql_query = """
SELECT 
    t.TxHash,
    t.Sender,
    t.Value_ETH,
    t.Tx_Frequency,
    COALESCE(w.Risk_Tier, 'Unclassified') AS Risk_Tier,
    SUM(t.Value_ETH) OVER (PARTITION BY t.Sender ORDER BY t.TxHash) AS Running_Cumulative_Volume,
    RANK() OVER (PARTITION BY t.Sender ORDER BY t.Value_ETH DESC) AS Sender_Value_Rank
FROM transactions t
LEFT JOIN wallet_risk_tags w ON t.Sender = w.Sender
LIMIT 10;
"""

print("\n--- Executing Advanced SQL Query (JOIN + Window Functions: Cumulative Sum & Rank) ---")
sql_result_df = pd.read_sql_query(advanced_sql_query, conn)
print(sql_result_df.to_string(index=False))
print("------------------------------------------------------------------------------------\n")

# 5. Statistical Risk Backtesting (Z-Score Anomaly Detection)
mean_val = df["Value_ETH"].mean()
std_val = df["Value_ETH"].std()

df["Z_Score"] = (df["Value_ETH"] - mean_val) / std_val
df["Is_Anomalous"] = (df["Z_Score"] > 3) | df["Gas_Anomaly"]

total_volume = df["Value_ETH"].sum()
anomaly_count = df["Is_Anomalous"].sum()

print(f"[SUCCESS] Analyzed {len(df)} transactions via enhanced SQL engine.")
print(f"-> Total Volume Tracked: {total_volume:.2f} ETH")
print(f"-> Multi-Factor Risk Anomalies Flagged: {anomaly_count}")

# 6. Build Interactive Visual Dashboard using Plotly
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Transaction Value Distribution", "Risk Anomalies & Spikes", "Gas Usage vs Transfer Value", "Risk Summary KPIs"),
    specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "xy"}, {"type": "table"}]]
)

# Chart 1: Distribution Histogram
fig.add_trace(
    go.Histogram(x=df["Value_ETH"], name="Value Distribution", marker_color="#3366cc"),
    row=1, col=1
)

# Chart 2: Scatter plot highlighting multi-factor risk anomalies in red
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

# Chart 3: Gas vs Value Correlation colored by frequency
fig.add_trace(
    go.Scatter(
        x=df["Gas_Used"], y=df["Value_ETH"],
        mode='markers',
        marker=dict(color=df["Tx_Frequency"], colorscale='Viridis', showscale=True, size=8),
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
    title_text="<b>Advanced On-Chain Risk & Anomaly Monitoring Dashboard</b>",
    template="plotly_white",
    height=800,
    showlegend=False
)

output_file = "risk_monitoring_dashboard.html"
fig.write_html(output_file)
print(f"[SUCCESS] Updated interactive dashboard generated and saved as '{output_file}'!")
conn.close()
