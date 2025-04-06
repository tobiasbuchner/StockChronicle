import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from src.utils.logger import setup_logging  # Import the logger setup function
from src.utils.db_utils import (
    load_environment_variables,
    create_database_engine,
)  # Import the utility functions
from src.utils.config_loader import load_yaml_config  # Import the YAML loader
from src.utils.file_utils import (
    delete_old_csv_files,  # Import the generic function
)

# Instantiate the logger
logger = setup_logging("fetch_yfin_ohlc")


def fetch_stock_data(
    tickers, index_name, engine, interval="1d", save_path=None
):
    """
    Fetch historical stock data from Yahoo Finance.

    :param tickers: List of stock symbols (e.g., ["AAPL", "MSFT"])
    :param index_name: Name of the index
    :param engine: SQLAlchemy engine for database connection
    :param interval: Data interval ("1d", "1wk", "1mo")
    :param save_path: Directory to save CSV files (optional,
                      loaded from config if None)
    :return: Dictionary of DataFrames with stock data
    """
    if save_path is None:
        logger.error("❌ Save path is not provided.")
        return {}

    os.makedirs(save_path, exist_ok=True)
    stock_data = {}
    no_data_tickers = []  # List to track tickers with no data

    for ticker in tickers:
        try:
            # Query to get the maximum date for the ticker
            query = text("""
            SELECT MAX(date) as max_date
            FROM ohlc_data
            WHERE ticker = :ticker AND "index" = :index_name
            """)
            with engine.connect() as connection:
                result = connection.execute(
                    query, {"ticker": ticker, "index_name": index_name}
                ).fetchone()
            max_date = result[0]  # Access the first element of the tuple

            if max_date is None:
                start_date = "1900-01-01"  # If no data, fetch maximum history
            else:
                start_date = (max_date + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                )

            end_date = datetime.now().strftime("%Y-%m-%d")

            # Skip fetching data if the max_date is today
            if max_date and max_date >= datetime.now().date():
                logger.info(
                    f"No new data to fetch for {ticker} as max_date is today."
                )
                continue

            logger.info(
                f"Fetching data for {ticker} from {start_date} to {end_date} "
                f"at {interval} interval"
            )
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date, end=end_date, interval=interval
            )

            if df.empty:
                logger.warning(f"No data found for {ticker}")
                no_data_tickers.append(ticker)
                continue

            df["Index"] = index_name  # Add index column
            df["Ticker"] = ticker  # Add ticker column
            # Replace spaces with underscores in column names
            df.columns = df.columns.str.replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_{timestamp}.csv"
            df.to_csv(os.path.join(save_path, filename))
            stock_data[ticker] = df
            logger.info(f"Saved {ticker} data to {save_path}/{filename}")
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            no_data_tickers.append(ticker)

    # Log analysis after processing all tickers for the index
    if no_data_tickers:
        logger.info(
            f"Analysis for index {index_name}: {len(no_data_tickers)} tickers "
            f"had no data. Tickers: {', '.join(no_data_tickers)}"
        )
    else:
        logger.info(f"Analysis for index {index_name}: All tickers had data.")

    # Delete old CSV files after successful data fetching
    delete_old_csv_files(save_path, days=1)

    return stock_data


def main():
    """
    Main function to fetch historical stock data from Yahoo Finance
    and save it as CSV files.
    """
    # Load YAML config
    config_path = "config/config.yaml"
    config = load_yaml_config(config_path)

    if not config:
        logger.critical("❌ Failed to load configuration. Exiting script.")
        return

    # Load environment variables
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    # Query to get the latest tickers from the PostgreSQL table
    query = """
    SELECT ticker, index
    FROM companies
    WHERE DATE(ingestion_timestamp) = (
        SELECT DATE(MAX(ingestion_timestamp))
        FROM companies
    )
    """

    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            logger.warning("No data found in the database.")
            return

        # Load save_path for Yahoo Finance data from config
        save_path = config["paths"]["yfin_ohlc_save_path"]

        for index_name, group in df.groupby("index"):
            tickers = group["ticker"].tolist()
            logger.info(
                f"Loading {len(tickers)} tickers for index {index_name}"
            )

            interval = "1d"
            save_path_index = os.path.join(save_path, index_name)
            data = fetch_stock_data(
                tickers, index_name, engine,
                interval=interval, save_path=save_path_index
            )

            # Show a preview of the first stock's data
            if data:
                print(data[list(data.keys())[0]].head())
    except Exception as e:
        logger.error(f"Error querying the database: {e}")


if __name__ == "__main__":
    main()
