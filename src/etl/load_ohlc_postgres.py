import os
import pandas as pd
from sqlalchemy import create_engine, exc
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, "load_ohlc_postgres.log")

    handler = TimedRotatingFileHandler(
        log_filename, when="midnight",
        interval=1, backupCount=30, encoding="utf-8"
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
        "logs/load_ohlc_postgres.json", mode="a", encoding="utf-8"
    )
    json_handler.setFormatter(JsonFormatter())

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG, handlers=[handler, json_handler,
                                       logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def load_environment_variables():
    load_dotenv(dotenv_path="config/.env")
    return {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME")
    }


def create_database_engine(env_vars):
    DATABASE_URL = (
        f"postgresql://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@"
        f"{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['DB_NAME']}"
    )
    return create_engine(DATABASE_URL)


def load_csv_to_db(engine, file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        if {"ticker", "date", "open", "high", "low", "close", "volume",
                "dividends", "stock_splits", "index"}.issubset(df.columns):
            df["ingestion_timestamp"] = datetime.now()  # Add timestamp column
            df["ingestion_date"] = datetime.now().date()
            # Add date-only timestamp
            # Load data into the PostgreSQL database
            df.to_sql("ohlc_data", engine, if_exists="append", index=False)
            logger.info(
                f"✅ Successfully inserted {len(df)} rows from {file_path} "
                f"into 'ohlc_data' table.")
        else:
            logger.error(
                f"❌ Missing required columns in {file_path}, skipping...")
    except pd.errors.EmptyDataError:
        logger.error(f"❌ No data found in {file_path}, skipping...")
    except pd.errors.ParserError:
        logger.error(f"❌ Error parsing data in {file_path}, skipping...")
    except exc.SQLAlchemyError as e:
        logger.error(f"❌ Database error: {e}, skipping...")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}, skipping...")


if __name__ == "__main__":
    logger = setup_logging()
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    data_dir = "data/yfin_ohlc"

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                logger.info(f"📥 Loading data from {file_path}")
                load_csv_to_db(engine, file_path)

    logger.info("🎉 All datasets have been processed!")