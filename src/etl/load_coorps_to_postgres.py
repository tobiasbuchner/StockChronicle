import pandas as pd
from sqlalchemy import create_engine, exc
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, "load_db.log")

    handler = TimedRotatingFileHandler(
        log_filename, when="midnight", 
        interval=1, backupCount=30, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG, handlers=[handler, logging.StreamHandler()]
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


def load_data_to_db(engine, index_name, file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        if {"ticker", "company", "index"}.issubset(df.columns):
            df["timestamp"] = datetime.now()

            # Load data into the PostgreSQL database
            df.to_sql("companies", engine, if_exists="append", index=False)
            logger.info(
                f"✅ Successfully inserted {len(df)} rows for {index_name} "
                f"into 'companies' table.")
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

    data_dir = "data"
    index_names = ["S&P500", "Dow Jones", "NASDAQ", "DAX"]

    for index_name in index_names:
        file_path = os.path.join(data_dir, f"{index_name}_companies.csv")

        if os.path.exists(file_path):
            logger.info(f"📥 Loading data from {file_path}")
            load_data_to_db(engine, index_name, file_path)
        else:
            logger.warning(f"⚠️ File not found: {file_path}, skipping...")

    logger.info("🎉 All datasets have been processed!")
