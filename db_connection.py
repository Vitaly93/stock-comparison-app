# conn to DB
import sqlite3
import pandas as pd

db = 'mydatabase.db'
conn = sqlite3.connect(db)

df = pd.read_sql("""
SELECT * FROM stock_features
ORDER BY Ticker
""", conn)
conn.close()
