
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    PRIMARY KEY (symbol, date)
);


CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol TEXT PRIMARY KEY,
    long_name TEXT,
    sector TEXT,
    industry TEXT,
    market_cap BIGINT,
    price NUMERIC,
    exchange TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
