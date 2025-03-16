import logging
import os
import time
import json
from io import StringIO
import requests
import pandas as pd
from bs4 import BeautifulSoup
import yaml
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Standard log file
    log_filename = os.path.join(log_dir, "fetch_wiki_corps.log")

    # Setup log rotation (daily, keep last 30 days)
    handler = TimedRotatingFileHandler(
        log_filename, when="midnight", interval=1,
        backupCount=30, encoding="utf-8"
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
        "logs/fetch_wiki_corps.json", mode="a", encoding="utf-8"
    )
    json_handler.setFormatter(JsonFormatter())

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG, handlers=[handler, json_handler,
                                       logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def load_yaml_config(file_path: str):
    """Loads the YAML configuration file."""
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
            if (not config or "sources" not in config or
                    "wikipedia" not in config["sources"] or
                    "indices" not in config["sources"]["wikipedia"]):
                raise ValueError("Invalid or empty configuration file.")
            return config["sources"]["wikipedia"]["indices"]
    except Exception as e:
        logger.exception(f"Failed to load YAML file {file_path}: {e}")
        return None


def extract_stock_table(
    url: str,
    column_criteria: dict,
    expected_range: tuple,
    index_name: str,
    table_index: int = 0,
    save_path: str = "data/wiki_corps",
    max_retries: int = 3,
    retry_delay: int = 5
):
    """
    Extracts stock data from Wikipedia, ensures completeness,
    and saves it as CSV.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    start_time = time.time()

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt+1}/{max_retries}: Fetching {url}")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"Successfully fetched {url}")
                break
            else:
                logger.warning(
                    f"HTTP {response.status_code} - Retrying in {retry_delay}s"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on {url}: {e}")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    else:
        logger.critical(f"Failed to fetch {url} after {max_retries} attempts")
        return None

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", {"class": "wikitable"})

    if table_index >= len(tables):
        logger.error(f"No table at index {table_index} on {url}")
        return None

    try:
        df = pd.read_html(StringIO(str(tables[table_index])))[0]
        df.columns = [str(col).lower() for col in df.columns]

        df_selected = {}
        for key, possible_names in column_criteria.items():
            found_col = next(
                (col for col in df.columns
                 if col in [name.lower() for name in possible_names]),
                None
            )
            if found_col:
                df_selected[key] = df[found_col]

        if len(df_selected) < 2:
            logger.warning(
                f"No matching columns found for {index_name} on {url}")
            return None

        df = pd.DataFrame(df_selected)
        df["Index"] = index_name

        if not (expected_range[0] <= len(df) <= expected_range[1]):
            logger.warning(
                f"Row count {len(df)} out of expected range "
                f"{expected_range} for {index_name}"
            )

        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{index_name}_companies.csv")
        df.to_csv(file_path, index=False)

        elapsed_time = time.time() - start_time
        logger.info(
            f"📁 Data saved to {file_path} in {elapsed_time:.2f} seconds")
        return df
    except Exception as e:
        logger.exception(f"Error processing table {table_index} on {url}: {e}")
        return None


def main():
    # Load YAML config
    config_path = "config/wikipedia_sources.yaml"
    config = load_yaml_config(config_path)

    if config:
        for index_name, data in config.items():
            logger.info(f"🔍 Extracting data for: {index_name}")
            df = extract_stock_table(
                url=data["url"],
                column_criteria=data["columns"],
                expected_range=tuple(data.get("expected_range", [0, 9999])),
                table_index=data.get("table_index", 0),
                index_name=index_name
            )
            if df is not None:
                logger.debug(f"First 5 rows for {index_name}: \n{df.head()}")
    else:
        logger.critical(
            "YAML configuration could not be loaded. Exiting script."
        )


if __name__ == "__main__":
    logger = setup_logging()
    main()
