import os
import pandas as pd
from datetime import datetime
from sqlalchemy import exc
from src.utils.logger import setup_logging  # Import the logger setup function
from src.utils.db_utils import (
    load_environment_variables,
    create_database_engine,
)  # Import database utility functions
from src.utils.config_loader import load_yaml_config  # Import the YAML loader

# Instantiate the logger
logger = setup_logging("load_ohlc_postgres")


def load_csv_to_db(engine, file_path):
    """
    Load a CSV file into the PostgreSQL database.

    :param engine: SQLAlchemy engine for database connection.
    :param file_path: Path to the CSV file to be loaded.
    """
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        # Check if required columns are present
        required_columns = {
            "ticker", "date", "open", "high", "low", "close", "volume",
            "dividends", "stock_splits", "index"
        }
        if required_columns.issubset(df.columns):
            df["ingestion_timestamp"] = datetime.now()  # Add timestamp column
            df["ingestion_date"] = datetime.now().date()
            # Add date-only column

            # Load data into the PostgreSQL database
            df.to_sql("ohlc_data", engine, if_exists="append", index=False)
            logger.info(
                f"✅ Successfully inserted {len(df)} rows from {file_path} "
                f"into 'ohlc_data' table."
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


def main():
    """
    Main function to load OHLC data from CSV files into a PostgreSQL database.
    """
    # Load YAML config
    config_path = "config/config.yaml"
    config = load_yaml_config(config_path)

    if not config:
        logger.critical("❌ Failed to load configuration. Exiting script.")
        return

    # Load environment variables and create a database engine
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    # Load the data directory path from the configuration
    data_dir = config["paths"]["yfin_ohlc_save_path"]

    # Iterate through all CSV files in the data directory
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                logger.info(f"📥 Loading data from {file_path}")
                load_csv_to_db(engine, file_path)

    logger.info("🎉 All datasets have been processed!")


if __name__ == "__main__":
    main()
