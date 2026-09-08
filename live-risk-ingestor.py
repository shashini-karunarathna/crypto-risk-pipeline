import sqlite3
import requests
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Initializing Live Blockchain Ingestion & Risk Pipeline (Phase 2)...")

# Public Ethereum RPC Endpoint (No API key required for basic block headers & tx lookups)
RPC_URL = "https://eth.public-rpc.com"

def fetch_latest_block_transactions():
    """Fetches real transaction data from the latest live Ethereum block via JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", True],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        result = response.json()
        
        if "result" in result and result["result"] is not None:
            block = result["result"]
            raw_txs = block.get("transactions", [])
            print(f"[SUCCESS] Connected to Ethereum Node. Latest Block Hash: {block.get('hash')[:10]}...")
            print(f"-> Retrieved {len(raw_txs)} live transactions from mainnet block.")
            
            parsed_txs = []
            for tx in raw_txs[:100]: # Cap to a manageable sample size for local analysis
                # Convert hex values to readable decimals/integers
                value_wei = int(tx.get("value", "0x0"), 16)
                value_eth = value_wei / 1e18 # Convert Wei to ETH
                gas_used = int(tx.get("gas", "0x5208"), 16)
                
                parsed_txs.append({
                    "TxHash": tx.get("hash"),
                    "Sender": tx.get("from"),
                    "Receiver": tx.get("to") or "0x0000000000000000000000000000000000000000",
                    "Value_ETH": value_eth,
                    "Gas_Used": gas_used
                })
            return pd.DataFrame(parsed_txs)
    except Exception as e:
        print(f"[WARNING] Live RPC connection failed ({e}). Falling back to robust synthetic backtest frame.")
    
    return None

# 1. Attempt Live Ingestion, Fallback to Synthetic Baseline if Network/Rate-limited
df = fetch_latest_block_transactions()

if df is None or len(df) == 0:
    print("[INFO] Initializing fallback simulation framework for robust local execution...")
    np.random.seed(42)
    n_transactions = 150
    senders = [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 40))}" for _ in range(20)]
    df = pd.DataFrame({
        "TxHash": [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 64))}" for _ in range(n_transactions)],
        "Sender": [np.random.choice(senders) for _ in range(n_transactions)],
        "Receiver": [f"0x{''.join(np.random.choice(list('0123456789abcdef'), 40))}" for _ in range(n_transactions)],
        "Value_ETH": np.random.exponential(scale=0.5, size=n_transactions),
        "Gas_Used": np.random.randint(21000, 150000, size=n_transactions)
    })

# 2. Compute Risk Indicators & Metrics
df["Tx_Frequency"] = df.groupby("Sender")["Sender"].transform("count")
gas_mean = df["Gas_Used"].mean() if len(df) > 0 else 21000
gas_std = df["Gas_Used"].std() if len(df) > 1 else 1000
df["Gas_Anomaly"] = df["Gas_Used"] > (gas_mean + (2 * gas_std if gas_std > 0 else 1000))

# 3. Store Data into SQLite Database & Execute Relational Associations
conn = sqlite3.connect("crypto_risk_live.db")
cursor = conn.cursor()

df.to_sql("live_transactions", conn, if_exists="replace", index=False)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_risk_tags (
        Sender TEXT PRIMARY KEY,
        Risk_Tier TEXT
    )
""")

unique_senders = df["Sender"].unique()[:10]
sample_tags = [(s, np.random.choice(["High-Risk Monitor", "Standard", "VIP Watchlist"])) for s in unique_senders]
cursor.executemany("INSERT OR REPLACE INTO wallet_risk_tags (Sender, Risk_Tier) VALUES (?, ?)", sample_tags)
conn.commit()

# 4. Advanced SQL Query: JOINs + Window Functions
advanced_sql_query = """
SELECT 
    t.TxHash,
    t.Sender,
    t.Value_ETH,
    t.Tx_Frequency,
    COALESCE(w.Risk_Tier, 'Unclassified') AS Risk_Tier,
    SUM(t.Value_ETH) OVER (PARTITION BY t.Sender ORDER BY t.TxHash) AS Running_Cumulative_Volume,
    RANK() OVER (PARTITION BY t.Sender ORDER BY t.Value_ETH DESC) AS Sender_Value_Rank
FROM live_transactions t
LEFT JOIN wallet_risk_tags w ON t.Sender = w.Sender
LIMIT 10;
"""

print("\n--- Executing Live SQL Engine (JOIN + Window Functions) ---")
sql_result_df = pd.read_sql_query(advanced_sql_query, conn)
print(sql_result_df.to_string(index=False))
print("-----------------------------------------------------------\n")

# 5. Statistical Risk Backtesting (Z-Score Anomaly Detection)
mean_val = df["Value_ETH"].mean()
std_val = df["Value_ETH"].std()

df["Z_Score"] = (df["Value_ETH"] - mean_val) / (std_val if std_val > 0 else 1.0)
df["Is_Anomalous"] = (df["Z_Score"] > 2.5) | df["Gas_Anomaly"]

total_volume = df["Value_ETH"].sum()
anomaly_count = df["Is_Anomalous"].sum()

print(f"[SUCCESS] Processed {len(df)} records through Live/Hybrid pipeline.")
print(f"-> Total Tracked Volume: {total_volume:.4f} ETH")
print(f"-> Flagged Risk Anomalies: {anomaly_count}")

# 6. Generate Interactive Plotly Dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Live Transfer Distribution", "Risk Anomalies & Spikes", "Gas Usage vs Value", "Pipeline Health KPIs"),
    specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "xy"}, {"type": "table"}]]
)

fig.add_trace(go.Histogram(x=df["Value_ETH"], name="Value Distribution", marker_color="#2b5c8f"), row=1, col=1)

colors = ['red' if x else 'blue' for x in df["Is_Anomalous"]]
fig.add_trace(go.Scatter(x=df.index, y=df["Value_ETH"], mode='markers', marker=dict(color=colors, size=6), name="Live Risk Flags"), row=1, col=2)

fig.add_trace(go.Scatter(x=df["Gas_Used"], y=df["Value_ETH"], mode='markers', marker=dict(color=df["Tx_Frequency"], colorscale='Plasma', showscale=True), name="Gas vs Value"), row=2, col=1)

fig.add_trace(go.Table(
    header=dict(values=["Metric", "Live Value"], fill_color='lightsteelblue', align='left'),
    cells=dict(values=[
        ["Ingested Records", "Flagged Risks", "Max Transfer (ETH)", "Mean Transfer (ETH)"],
        [len(df), anomaly_count, f"{df['Value_ETH'].max():.4f}", f"{mean_val:.4f}"]
    ], fill_color='whitesmoke', align='left')
), row=2, col=2)

fig.update_layout(title_text="<b>Live On-Chain Risk & Transaction Intelligence Dashboard</b>", template="plotly_white", height=800, showlegend=False)

fig.write_html("live_risk_dashboard.html")
print("[SUCCESS] Live dashboard compiled and saved as 'live_risk_dashboard.html'!")
conn.close()


