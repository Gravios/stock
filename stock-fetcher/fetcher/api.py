"""doc."""
import os
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from datetime import datetime, timedelta

frontend_host = os.getenv("FRONTEND_HOST")
frontend_port = os.getenv("FRONTEND_PORT")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000",
                   "http://localhost:5000/api/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection function
def get_stockdb_conn():
    """
    docs.

    docs
    """
    print(os.getenv("STOCKDB_HOST"))
    print(os.getenv("STOCKDB_DB"))
    print(os.getenv("STOCKDB_USER"))
    print(os.getenv("STOCKDB_PASSWORD"))
    return psycopg2.connect(
        host=os.getenv("STOCKDB_HOST"),
        database=os.getenv("STOCKDB_DB"),
        user=os.getenv("STOCKDB_USER"),
        password=os.getenv("STOCKDB_PASSWORD")
    )


# Fetch stock data from Yahoo Finance
def get_stock_data(symbol: str, start_date: str, end_date: str):
    """
    docs.

    docs
    """
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    return data


# Insert stock data into the database
def insert_data_into_db(data, symbol: str):
    """
    docs.

    docs
    """
    conn = get_stockdb_conn()
    cur = conn.cursor()

    for date, row in data.iterrows():
        open_price = float(row['Open'])
        high_price = float(row['High'])
        low_price = float(row['Low'])
        close_price = float(row['Close'])
        volume = int(row['Volume'])

        cur.execute("""
            INSERT INTO stocks (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO NOTHING
        """, (symbol, date.date(), open_price, high_price,
              low_price, close_price, volume))

    conn.commit()
    conn.close()


# Insert metadata into PostgreSQL
def insert_metadata_into_db(metadata):
    """
    docs.

    docs
    """
    conn = get_stockdb_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO stock_metadata
        (symbol, long_name, sector, industry,
         market_cap, price, exchange, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (symbol) DO UPDATE SET
            long_name = EXCLUDED.long_name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            market_cap = EXCLUDED.market_cap,
            price = EXCLUDED.price,
            exchange = EXCLUDED.exchange,
            last_updated = NOW();
    """, (
        metadata['symbol'], metadata['long_name'],
        metadata['sector'], metadata['industry'],
        metadata['market_cap'], metadata['price'],
        metadata['exchange']
    ))
    conn.commit()
    conn.close()


# Endpoint to populate stock data
@app.get("/api/populate/{symbol}")
async def populate_stock_data(symbol: str, start_date: str, end_date: str):
    """
    docs.

    docs
    """
    # Convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD.")

    # Fetch data from Yahoo Finance
    stock_data = get_stock_data(symbol, start_date, end_date)

    if stock_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {symbol} in the given date range.")

    # Insert data into the database
    insert_data_into_db(stock_data, symbol)

    return {"message": f"Stock data for {symbol} has been successfully "
            + f"populated from {start_date} to {end_date}."}


# Endpoint to fetch and populate metadata for a given symbol
@app.get("/api/populate-metadata/{symbol}")
async def populate_metadata(symbol: str):
    """
    docs.

    docs
    """
    stock = yf.Ticker(symbol)
    info = stock.info

    if not info:
        raise HTTPException(status_code=404,
                            detail=f"No metadata found for symbol: {symbol}")

    metadata = {
        'symbol': symbol.upper(),
        'long_name': info.get('longName'),
        'sector': info.get('sector'),
        'industry': info.get('industry'),
        'market_cap': info.get('marketCap'),
        'price': info.get('currentPrice'),
        'exchange': info.get('exchange'),
    }

    insert_metadata_into_db(metadata)

    return {"message": f"Metadata for {symbol.upper()} populated successfully.",
            "data": metadata}



# Endpoint to fetch stock data from the database
@app.get("/api/stock/{symbol}")
def read_stock(symbol: str, limit: int = 10):
    """
    docs.

    docs
    """
    conn = get_stockdb_conn()
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


# Endpoint for daily stock summary (7-day data)
@app.get("/api/stock/{symbol}/daily-summary")
def read_daily_summary(symbol: str):
    """
    docs.

    docs
    """
    conn = get_stockdb_conn()
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
    return [
        {
            "date": row[0],
            "high": row[1],
            "low": row[2],
            "close": row[3]
        } for row in rows]


# Endpoint to get metadata for specific stock symbols
@app.get("/api/stock/{symbol}/metadata")
def read_metadata(symbol: str):
    """
    docs.

    docs
    """
    metadata = {
        "AAPL":
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics"
        },
        "GOOG":
        {
            "symbol": "GOOG",
            "name": "Alphabet Inc.",
            "sector": "Technology",
            "industry": "Internet Services"
        },
        "MSFT":
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software"
        }
    }
    return metadata.get(symbol.upper(), {})
