import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="config/.env")

# Database connection settings
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create database engine
engine = create_engine(DATABASE_URL)

# Directory where the CSV files are stored
data_dir = "data"

# List of index names (should match the filenames created in the extraction step)
index_names = ["S&P500", "Dow Jones", "NASDAQ", "DAX"]

# Iterate through all index datasets and load them into the database
for index_name in index_names:
    file_path = os.path.join(data_dir, f"{index_name}_companies.csv")

    if os.path.exists(file_path):
        print(f"📥 Loading data from {file_path}")

        # Read the CSV into a DataFrame
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        # Ensure correct column names
        if {"ticker", "company", "index"}.issubset(df.columns):
            #df = df.rename(columns={"index": "index_name"})

            # Load data into the PostgreSQL database
            df.to_sql("companies", engine, if_exists="append", index=False)
            print(f"✅ Successfully inserted {len(df)} rows for {index_name} into 'companies' table.")
        else:
            print(f"❌ Missing required columns in {file_path}, skipping...")
    else:
        print(f"⚠️ File not found: {file_path}, skipping...")

print("🎉 All datasets have been processed!")
