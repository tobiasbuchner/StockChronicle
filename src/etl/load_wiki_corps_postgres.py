import pandas as pd
from sqlalchemy import create_engine, exc
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
from logging.handlers import TimedRotatingFileHandler
import yaml


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, "load_wiki_corps_postgres.log")

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
        "logs/load_wiki_corps_postgres.json", mode="a", encoding="utf-8"
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


def load_data_to_db(engine, index_name, file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        if {"ticker", "company", "index"}.issubset(df.columns):
            df["ingestion_timestamp"] = datetime.now()
            df["ingestion_date"] = datetime.now().date()
            # Add date-only timestamp

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


def load_indices_from_yaml(yaml_path):
    try:
        with open(yaml_path, "r") as file:
            config = yaml.safe_load(file)
            indices = config.get("sources", {}).get("wikipedia", {}).get(
                "indices", {}
            )
            return list(indices.keys())
    except Exception as e:
        logger.error(f"Error loading indices from YAML: {e}")
        return []


if __name__ == "__main__":
    logger = setup_logging()
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    yaml_path = "config/wikipedia_sources.yaml"
    index_names = load_indices_from_yaml(yaml_path)

    data_dir = "data/wiki_corps"

    for index_name in index_names:
        file_path = os.path.join(data_dir, f"{index_name}_companies.csv")

        if os.path.exists(file_path):
            logger.info(f"📥 Loading data from {file_path}")
            load_data_to_db(engine, index_name, file_path)
        else:
            logger.warning(f"⚠️ File not found: {file_path}, skipping...")

    logger.info("🎉 All datasets have been processed!")
