import pandas as pd
from sqlalchemy import exc, Table, MetaData, update
import os
from datetime import datetime
from src.utils.logger import setup_logging  # Import the logger setup function
from src.utils.db_utils import (
    load_environment_variables,
    create_database_engine,
)
from src.utils.config_loader import (
    load_yaml_config,
    validate_config,  # Import the YAML loader and validator
)

# Instantiate the logger
logger = setup_logging("load_wiki_corps_postgres")


def load_data_to_db(engine, file_path):
    """
    Load data from a CSV file into the PostgreSQL database.

    This function reads a CSV file containing companies of a specific index,
    validates its structure, and loads the data
    into the 'companies' table in the PostgreSQL database. It updates existing
    entries and inserts new ones. Errors during processing are logged.

    :param engine: SQLAlchemy engine object for database connection.
        Used to execute queries and interact with the database.
    :param file_path: str
        Path to the stocks index CSV file to be loaded into the database.

    :return: None
        The function does not return any value. It logs the results of the
        operation, including success or failure for each row and the overall
        file processing status.
    """
    try:
        # Check if the file exists and is not empty
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        if df.empty:
            logger.warning(f"❌ The file {file_path} is empty. Skipping...")
            return

        # Convert column names to lowercase for consistency
        df.columns = df.columns.str.lower()

        # Check if the required columns are present in the DataFrame
        required_columns = {"ticker", "company", "index", "sector"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            logger.error(
                (
                    f"❌ Missing columns {missing_columns} in {file_path}. "
                    "Skipping..."
                )
            )
            return

        # Add an ingestion timestamp to the DataFrame
        df["ingestion_timestamp"] = datetime.now()

        # Load the metadata and define the 'companies' table
        metadata = MetaData()
        companies = Table('companies', metadata, autoload_with=engine)

        # Update existing entries and insert new entries
        with engine.begin() as connection:  # Automatic commit/rollback
            new_entries = []  # List to store new entries
            for _, row in df.iterrows():
                try:
                    # Check if the entry already exists in the database
                    stmt = companies.select().where(
                        (companies.c.ticker == row['ticker']) &
                        (companies.c.index == row['index'])
                    )
                    existing_entry = connection.execute(stmt).fetchone()

                    if existing_entry:
                        # Update only the ingestion timestamp
                        # for existing entries
                        connection.execute(
                            update(companies)
                            .where((companies.c.ticker == row['ticker']) &
                                   (companies.c.index == row['index']))
                            .values(
                                ingestion_timestamp=row['ingestion_timestamp']
                            )
                        )
                    else:
                        # Add new entries to the list for batch insertion
                        new_entries.append({
                            "ticker": row['ticker'],
                            "index": row['index'],
                            "company": row['company'],
                            "sector": row['sector'],
                            "ingestion_timestamp": row['ingestion_timestamp']
                        })
                except exc.SQLAlchemyError as e:
                    # Log database errors for individual rows
                    logger.error(f"❌ Database error for row {row}: {e}")
                except Exception as e:
                    # Log unexpected errors for individual rows
                    logger.error(f"❌ Unexpected error for row {row}: {e}")

            # Perform batch insert for new entries
            if new_entries:
                try:
                    connection.execute(companies.insert(), new_entries)
                    logger.info(
                        (
                            f"✅ Inserted {len(new_entries)} new rows "
                            "into the database."
                        )
                    )
                except exc.SQLAlchemyError as e:
                    # Log errors during batch insert
                    logger.error(f"❌ Batch insert failed: {e}")

        # Log successful processing of the file
        logger.info(
            f"✅ Successfully processed {len(df)} rows from {file_path}."
        )

    except FileNotFoundError:
        # Log error if the file is not found
        logger.error(f"❌ File not found: {file_path}")
    except pd.errors.EmptyDataError:
        # Log error if the file is empty
        logger.error(f"❌ No data found in {file_path}, skipping...")
    except pd.errors.ParserError:
        # Log error if there is an issue parsing the file
        logger.error(f"❌ Error parsing data in {file_path}, skipping...")
    except exc.SQLAlchemyError as e:
        # Log general database errors
        logger.error(f"❌ Database error: {e}, skipping...")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"❌ Unexpected error: {e}, skipping...")


if __name__ == "__main__":
    """
    Main script to load company data from CSV files into a PostgreSQL database.
    """
    # Load the YAML configuration file
    config_path = "config/config.yaml"
    config = load_yaml_config(config_path)

    if not config:
        # Exit if the configuration file cannot be loaded
        logger.critical("❌ Failed to load configuration. Exiting script.")
        exit(1)

    # Validate the configuration
    try:
        validate_config(config, required_keys=["paths", "sources"])
        validate_config(
            config["paths"], required_keys=["wiki_corps_save_path"]
        )
        validate_config(config["sources"], required_keys=["wikipedia"])
    except ValueError as e:
        logger.critical(f"❌ Configuration validation failed: {e}")
        exit(1)

    # Load environment variables and create a database engine
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    # Load the data directory path from the configuration
    data_dir = config["paths"]["wiki_corps_save_path"]

    # Iterate through all CSV files in the data directory
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                logger.info(f"📥 Loading data from {file_path}")
                load_data_to_db(engine, file_path)

    # Log completion of the script
    logger.info("🎉 All datasets have been processed!")
