
from fastapi import FastAPI
import psycopg2
from datetime import datetime, timedelta

app = FastAPI()

def get_conn():
    return psycopg2.connect(
        host="db",
        database="stockdb",
        user="stockuser",
        password="stockpass"
    )

@app.get("/stock/{symbol}")
def read_stock(symbol: str, limit: int = 10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, open, high, low, close, volume
        FROM stocks
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT %s
    """, (symbol.upper(), limit))
    rows = cur.fetchall()
    conn.close()
    return {"symbol": symbol.upper(), "data": rows}

@app.get("/stock/{symbol}/daily-summary")
def read_daily_summary(symbol: str):
    conn = get_conn()
    cur = conn.cursor()
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    cur.execute("""
        SELECT date, high, low, close
        FROM stocks
        WHERE symbol = %s AND date >= %s
        ORDER BY date DESC
    """, (symbol.upper(), start_date.date()))
    rows = cur.fetchall()
    conn.close()
    return [{"date": row[0], "high": row[1], "low": row[2], "close": row[3]} for row in rows]

@app.get("/stock/{symbol}/metadata")
def read_metadata(symbol: str):
    metadata = {
        "AAPL": {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        "GOOG": {"symbol": "GOOG", "name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services"},
        "MSFT": {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"}
    }
    return metadata.get(symbol.upper(), {})
