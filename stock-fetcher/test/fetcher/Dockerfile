
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install fastapi psycopg2-binary uvicorn

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
