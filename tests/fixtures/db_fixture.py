import pytest
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

@pytest.fixture(scope="session")
def db_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    yield conn
    conn.close()

def query_loan_by_id(conn, loan_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_id, amount FROM loan WHERE id=%s", (loan_id,))
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "customer_id": row[1], "amount": row[2]}
    return None
