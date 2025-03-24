import pandas as pd
from sqlalchemy import create_engine, exc, Table, MetaData, update
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, "load_wiki_corps_postgres.log")

    # Setup log rotation (daily, keep last 30 days)
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
    """Load environment variables from a .env file."""
    load_dotenv(dotenv_path="config/.env")
    return {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME")
    }


def create_database_engine(env_vars):
    """Create a SQLAlchemy engine using the provided environment variables."""
    DATABASE_URL = (
        f"postgresql://{env_vars['DB_USER']}:{env_vars['DB_PASSWORD']}@"
        f"{env_vars['DB_HOST']}:{env_vars['DB_PORT']}/{env_vars['DB_NAME']}"
    )
    return create_engine(DATABASE_URL)


def load_data_to_db(engine, file_path):
    """Load data from a CSV file into the PostgreSQL database."""
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        if {"ticker", "company", "index", "sector"}.issubset(df.columns):
            df["ingestion_timestamp"] = datetime.now()

            metadata = MetaData()
            companies = Table('companies', metadata, autoload_with=engine)

            # Update existing entries and insert new entries
            with engine.begin() as connection:  # Automatic commit/rollback
                for _, row in df.iterrows():
                    # Check if the entry exists
                    stmt = companies.select().where(
                        (companies.c.ticker == row['ticker']) &
                        (companies.c.index == row['index'])
                    )
                    existing_entry = connection.execute(stmt).fetchone()

                    if existing_entry:
                        # Update only the timestamp
                        connection.execute(
                            update(companies)
                            .where((companies.c.ticker == row['ticker']) &
                                   (companies.c.index == row['index']))
                            .values(
                                ingestion_timestamp=row['ingestion_timestamp']
                            )
                        )
                    else:
                        # If no entry exists, create a new one
                        connection.execute(companies.insert().values(
                            ticker=row['ticker'],
                            index=row['index'],
                            company=row['company'],
                            sector=row['sector'],
                            ingestion_timestamp=row['ingestion_timestamp']
                        ))

            logger.info(
                f"✅ Successfully processed {len(df)} rows from {file_path}."
            )
        else:
            logger.error(
                f"❌ Missing required columns in {file_path}, skipping..."
            )

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

    data_dir = "data/wiki_corps"

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                logger.info(f"📥 Loading data from {file_path}")
                load_data_to_db(engine, file_path)

    logger.info("🎉 All datasets have been processed!")
