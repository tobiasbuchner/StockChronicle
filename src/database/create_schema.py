from sqlalchemy import (
    Column, Integer, String, MetaData, Table, DateTime,
    Date, Float, BigInteger,
    PrimaryKeyConstraint, CheckConstraint, UniqueConstraint
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
    PrimaryKeyConstraint("ticker", "index"),
    UniqueConstraint("ticker", "index", name="unique_ticker_per_index"),
    CheckConstraint("char_length(ticker) > 0", name="check_ticker_not_empty"),
    CheckConstraint("char_length(index) > 0", name="check_index_not_empty"),
    CheckConstraint(
        "char_length(company) > 0", name="check_company_not_empty"
    ),
    CheckConstraint("char_length(sector) > 0", name="check_sector_not_empty")
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
    Column("ingestion_date", Date, nullable=False),
    UniqueConstraint("ticker", "date", name="unique_ticker_date"),
    CheckConstraint(
        "char_length(index) > 0",
        name="check_ohlc_index_not_empty"
    ),
    CheckConstraint("char_length(ticker) > 0",
                    name="check_ohlc_ticker_not_empty"),
    CheckConstraint("open >= 0", name="check_open_non_negative"),
    CheckConstraint("high >= 0", name="check_high_non_negative"),
    CheckConstraint("low >= 0", name="check_low_non_negative"),
    CheckConstraint("close >= 0", name="check_close_non_negative"),
    CheckConstraint("volume >= 0", name="check_volume_non_negative"),
    CheckConstraint("high >= low", name="check_high_gte_low"),
    CheckConstraint("open BETWEEN low AND high",
                    name="check_open_between_low_high"),
    CheckConstraint("close BETWEEN low AND high",
                    name="check_close_between_low_high")
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
