import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import yaml


def load_yaml_config(file_path: str):
    """Loads the YAML configuration file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def extract_stock_table(url: str, column_criteria: list, expected_count: int, index_name: str, save_path: str = "data"):
    """
    Extracts stock data from Wikipedia, ensures completeness, and saves it as CSV.

    :param url: Wikipedia URL of the stock index page
    :param column_criteria: List of possible column names to identify the correct table
    :param expected_count: Expected number of companies in the index
    :param index_name: Name of the stock index (used for the CSV filename)
    :param save_path: Directory where the CSV file should be saved
    :return: Pandas DataFrame containing the stock data or None if extraction fails
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error fetching the page: {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", {"class": "wikitable"})

    for i, table in enumerate(tables):
        df = pd.read_html(str(table))[0]  # Convert HTML table to Pandas DataFrame
        df.columns = [col.lower() for col in df.columns]  # Normalize column names

        # Find the actual column names for "Company" and "Ticker"
        company_col = next((col for col in df.columns if any(c.lower() in col for c in ["company", "security"])), None)
        ticker_col = next((col for col in df.columns if any(c.lower() in col for c in ["ticker", "symbol"])), None)

        if company_col and ticker_col:
            print(f"✅ Correct table found for {index_name} (Index {i})")

            # Keep only "Ticker" and "Company" columns
            df = df[[ticker_col, company_col]]
            df.columns = ["Ticker", "Company"]  # Standardize column names

            # Check if the number of extracted companies matches 
            # the expected count
            extracted_count = len(df)
            if extracted_count < expected_count:
                print(f"⚠️ Warning: Extracted {extracted_count} companies, but expected {expected_count} for {index_name}!")

            # Ensure save directory exists
            os.makedirs(save_path, exist_ok=True)

            # Save DataFrame as CSV
            file_path = os.path.join(save_path, f"{index_name}_companies.csv")
            df.to_csv(file_path, index=False)
            print(f"📁 Data saved to {file_path}")

            return df

    print(f"❌ No matching table with 'Company' and 'Ticker' found on {url}.")
    return None


# Load configuration from YAML file
config_path = "config/wikipedia_sources.yaml"
config = load_yaml_config(config_path)

# Extract and save data for each index
for index_name, data in config["indices"].items():
    print(f"\n🔍 Extracting data for: {index_name}")
    df = extract_stock_table(url=data["url"], column_criteria=data["columns"], 
                             expected_count=data["expected_count"], index_name=index_name)
    if df is not None:
        print(df.head())  # Display the first few rows of the extracted table
