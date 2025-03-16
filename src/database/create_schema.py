from sqlalchemy import (
    create_engine, Column, Integer, String, MetaData, Table, DateTime,
    Date, Float, BigInteger
)
from sqlalchemy.engine import reflection
import os
from dotenv import load_dotenv
import logging
import json
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Standard log file
    log_filename = os.path.join(log_dir, "create_schema.log")

    # Setup log rotation (daily, keep last 30 days)
    handler = TimedRotatingFileHandler(
        log_filename, when="midnight", interval=1, backupCount=30,
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # JSON Logging
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "function": record.funcName,
                "message": record.getMessage()
            }
            return json.dumps(log_entry, ensure_ascii=False)

    json_handler = logging.FileHandler(
        "logs/create_schema.json", mode="a", encoding="utf-8"
    )
    json_handler.setFormatter(JsonFormatter())

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[handler, json_handler, logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


logger = setup_logging()

# Load environment variables
load_dotenv("config/.env")

# Database connection
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:"
    f"{DB_PORT}/{DB_NAME}"
)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define schema for companies table
companies = Table(
    "companies", metadata,
    Column("id", Integer, primary_key=True),
    Column("index", String(50), nullable=False),
    Column("ticker", String(20), nullable=False),
    Column("company", String(255), nullable=False),
    Column("sector", String(255), nullable=True),
    Column("ingestion_timestamp", DateTime, nullable=False),
    Column("ingestion_date", Date, nullable=False)  # Add date-only column
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
