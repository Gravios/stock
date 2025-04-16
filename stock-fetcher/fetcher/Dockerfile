
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install fastapi psycopg2-binary uvicorn yfinance

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3000"]
