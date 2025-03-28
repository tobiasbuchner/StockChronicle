from sqlalchemy import (
    Column, Integer, String, MetaData, Table, DateTime,
    Date, Float, BigInteger, PrimaryKeyConstraint
)
from sqlalchemy.engine import reflection
from src.utils.logger import setup_logging  # Import the logger setup function
from src.utils.db_utils import (
    load_environment_variables,
    create_database_engine  # Import the utility functions
)

# Instantiate the logger
logger = setup_logging("create_schema")

# Load environment variables and create database engine
env_vars = load_environment_variables()
engine = create_database_engine(env_vars)
metadata = MetaData()

# Define schema for companies table
companies = Table(
    "companies", metadata,
    Column("ticker", String(20), nullable=False),
    Column("index", String(50), nullable=False),
    Column("company", String(255), nullable=False),
    Column("sector", String(255), nullable=False),
    Column("ingestion_timestamp", DateTime, nullable=False),
    PrimaryKeyConstraint("ticker", "index")
)

# Define schema for ohlc_data table
ohlc_data = Table(
    "ohlc_data", metadata,
    Column("id", Integer, primary_key=True),
    Column("index", String(50), nullable=False),
    Column("ticker", String(20), nullable=False),
    Column("date", Date, nullable=False),
    Column("open", Float, nullable=False),
    Column("high", Float, nullable=False),
    Column("low", Float, nullable=False),
    Column("close", Float, nullable=False),
    Column("volume", BigInteger, nullable=False),
    Column("dividends", Float, nullable=True),
    Column("stock_splits", Float, nullable=True),
    Column("ingestion_timestamp", DateTime, nullable=False),
    Column("ingestion_date", Date, nullable=False)  # Add date-only column
)

# Check if tables exist
inspector = reflection.Inspector.from_engine(engine)
if 'companies' in inspector.get_table_names():
    logger.warning("⚠️ Table 'companies' already exists in PostgreSQL.")
else:
    # Create companies table
    metadata.create_all(engine, tables=[companies])
    logger.info("✅ Table 'companies' created in PostgreSQL.")

if 'ohlc_data' in inspector.get_table_names():
    logger.warning("⚠️ Table 'ohlc_data' already exists in PostgreSQL.")
else:
    # Create ohlc_data table
    metadata.create_all(engine, tables=[ohlc_data])
    logger.info("✅ Table 'ohlc_data' created in PostgreSQL.")
