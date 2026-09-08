import unittest
import sqlite3
import pandas as pd
import numpy as np

class TestCryptoRiskPipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up an in-memory SQLite database and sample data for testing."""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        
        # Create mock transaction table
        self.cursor.execute("""
            CREATE TABLE transactions (
                TxHash TEXT,
                Sender TEXT,
                Value_ETH REAL,
                Gas_Used INTEGER
            )
        """)
        
        # Insert a balanced set of normal transactions plus an intentional massive whale anomaly
        mock_data = [
            ("0x1", "0xSenderA", 0.1, 21000),
            ("0x2", "0xSenderA", 0.2, 21000),
            ("0x3", "0xSenderB", 0.3, 22000),
            ("0x4", "0xSenderB", 0.15, 21000),
            ("0x5", "0xSenderC", 50.0, 150000) # High-value anomaly
        ]
        self.cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?)", mock_data)
        self.conn.commit()

    def tearDown(self):
        """Close the database connection after each test."""
        self.conn.close()

    def test_z_score_anomaly_detection(self):
        """Test that Z-score calculation correctly flags statistical anomalies."""
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn)
        
        mean_val = df["Value_ETH"].mean()
        std_val = df["Value_ETH"].std()
        
        if std_val > 0:
            df["Z_Score"] = (df["Value_ETH"] - mean_val) / std_val
        else:
            df["Z_Score"] = 0.0
            
        df["Is_Anomalous"] = df["Z_Score"] > 1.5
        
        # The fifth transaction (50.0 ETH) should be flagged as anomalous
        self.assertTrue(df.loc[df["TxHash"] == "0x5", "Is_Anomalous"].values[0])

    def test_sql_window_function_cumulative_volume(self):
        """Test SQL window function logic for running cumulative volume."""
        query = """
        SELECT 
            Sender,
            Value_ETH,
            SUM(Value_ETH) OVER (PARTITION BY Sender ORDER BY TxHash) AS Running_Cumulative_Volume
        FROM transactions
        """
        result_df = pd.read_sql_query(query, self.conn)
        
        # Check that SenderA's second transaction cumulative sum equals 0.1 + 0.2 = 0.3
        sender_a_rows = result_df[result_df["Sender"] == "0xSenderA"]
        final_cum_vol = sender_a_rows.iloc[-1]["Running_Cumulative_Volume"]
        
        self.assertAlmostEqual(final_cum_vol, 0.3)

if __name__ == "__main__":
    unittest.main()

    