import os
import time
from io import StringIO
import requests
import pandas as pd
from bs4 import BeautifulSoup
from src.utils.logger import setup_logging  # Import the logger setup function
from src.utils.config_loader import (
    load_yaml_config,
    validate_config,  # Import the YAML loader
)

# Instantiate the logger
logger = setup_logging("fetch_wiki_corps")


def extract_stock_table(
    url: str,
    column_criteria: dict,
    expected_range: tuple[int, int],
    index_name: str,
    table_index: int = 0,
    save_path: str = "data/wiki_corps",
    max_retries: int = 3,
    retry_delay: int = 5
) -> pd.DataFrame | None:
    """
    Extracts stock data from Wikipedia, ensures completeness,
    and saves it as CSV.

    :param url: URL of the Wikipedia page.
    :param column_criteria: Dictionary mapping column names to possible
        matches.
    :param expected_range: Tuple specifying the expected row count range.
    :param index_name: Name of the stock index.
    :param table_index: Index of the table on the Wikipedia page.
    :param save_path: Directory to save the extracted CSV file.
    :param max_retries: Maximum number of retries for HTTP requests.
    :param retry_delay: Delay between retries in seconds.
    :return: DataFrame containing the extracted data, or None if an error
        occurs.
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

    if not config:
        logger.critical("Failed to load configuration. Exiting script.")
        return
    # Validate the configuration
    try:
        validate_config(config, required_keys=["paths", "sources"])
        validate_config(config["sources"], required_keys=["wikipedia"])
        validate_config(
            config["sources"]["wikipedia"],
            required_keys=["indices"]
        )
    except ValueError as e:
        logger.critical(f"Configuration validation failed: {e}")
        return

    # Extract save_path from the config
    save_path = config.get("paths", {}).get("save_path", "data/wiki_corps")

    # Extract Wikipedia-specific configuration
    wikipedia_config = config.get("sources", {}).get("wikipedia", {}).get(
        "indices", {}
    )

    if wikipedia_config:
        for index_name, data in wikipedia_config.items():
            logger.info(f"🔍 Extracting data for: {index_name}")
            df = extract_stock_table(
                url=data["url"],
                column_criteria=data["columns"],
                expected_range=tuple(data.get("expected_range", [0, 9999])),
                table_index=data.get("table_index", 0),
                index_name=index_name,
                save_path=save_path
            )
            if df is not None:
                logger.debug(f"First 5 rows for {index_name}: \n{df.head()}")
    else:
        logger.critical(
            "Wikipedia configuration could not be loaded. Exiting script."
        )


if __name__ == "__main__":
    main()
