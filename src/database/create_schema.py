from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Database connection
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define schema
companies = Table(
    "companies", metadata,
    Column("id", Integer, primary_key=True),
    Column("index_name", String(50), nullable=False),
    Column("ticker", String(20), nullable=False),
    Column("company", String(255), nullable=False)
)

# Create table
metadata.create_all(engine)
print("✅ Table 'companies' created in PostgreSQL.")
