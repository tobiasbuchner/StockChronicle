import os
import logging
import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy import create_engine
from dotenv import load_dotenv


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Standard log file
    log_filename = os.path.join(log_dir, "fetch_yfin_ohlc.log")

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
        "logs/fetch_yfin_ohlc.json", mode="a", encoding="utf-8"
    )
    json_handler.setFormatter(JsonFormatter())

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG, handlers=[handler, json_handler,
                                       logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


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


def fetch_stock_data(tickers, index_name, interval="1d",
                     save_path="data/yfin_ohlc"):
    """
    Fetch historical stock data from Yahoo Finance.

    :param tickers: List of stock symbols (e.g., ["AAPL", "MSFT"])
    :param index_name: Name of the index
    :param interval: Data interval ("1d", "1wk", "1mo")
    :param save_path: Directory to save CSV files
    :return: Dictionary of DataFrames with stock data
    """
    os.makedirs(save_path, exist_ok=True)
    stock_data = {}

    for ticker in tickers:
        try:
            logger.info(
                f"Fetching maximum history data for {ticker} at "
                f"{interval} interval"
            )
            stock = yf.Ticker(ticker)
            df = stock.history(period="max", interval=interval)

            if df.empty:
                logger.warning(f"No data found for {ticker}")
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

    return stock_data


def main():
    # Load environment variables
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)

    # Query to get the latest tickers from the PostgreSQL table
    query = """
    SELECT ticker, index
    FROM companies
    WHERE (index, ingestion_date) IN (
        SELECT index, MAX(ingestion_date)
        FROM companies
        GROUP BY index
    )
    """

    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            logger.warning("No data found in the database.")
            return

        for index_name, group in df.groupby("index"):
            tickers = group["ticker"].tolist()
            logger.info(
                f"Loaded {len(tickers)} tickers for index {index_name}"
            )

            interval = "1d"
            save_path = os.path.join("data/yfin_ohlc", index_name)
            data = fetch_stock_data(tickers, index_name, interval=interval,
                                    save_path=save_path)

            # Show a preview of the first stock's data
            if data:
                print(data[list(data.keys())[0]].head())
    except Exception as e:
        logger.error(f"Error querying the database: {e}")


if __name__ == "__main__":
    logger = setup_logging()
    main()
