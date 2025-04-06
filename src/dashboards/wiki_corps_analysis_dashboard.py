import streamlit as st
import pandas as pd
from src.utils.db_utils import (
    load_environment_variables,
    create_database_engine,
)

# Title of the dashboard
st.title("📊 Wiki Stock Index Table Viewer")
st.markdown(
    (
        "This dashboard displays data from the `companies` table with "
        "filtering options."
    )
)

# Establish database connection
try:
    # Load environment variables and create the database engine
    env_vars = load_environment_variables()
    engine = create_database_engine(env_vars)
    st.success("✅ Successfully connected to the database.")
except Exception as e:
    st.error(f"❌ Error connecting to the database: {e}")
    st.stop()


# Function to fetch data from the "companies" table
@st.cache_data
def load_companies_data():
    query = "SELECT * FROM companies"
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


# Load data
companies_df = load_companies_data()

# Display data with filtering options
if not companies_df.empty:
    st.subheader("📋 Companies Table")

    # Add filtering options
    # Filter by index (Multiselect)
    index_options = companies_df['index'].unique()
    selected_index = st.multiselect(
        "Filter by Index",
        options=index_options,
        default=index_options
    )

    # Dynamically filter sectors based on selected index
    filtered_sectors = companies_df[
        companies_df['index'].isin(selected_index)
    ]['sector'].dropna().unique()
    selected_sector = st.multiselect(
        "Filter by Sector",
        options=filtered_sectors,
        default=filtered_sectors
    )

    # Filter by ingestion date (Multiple Choice Dropdown)
    companies_df['ingestion_date'] = pd.to_datetime(
        companies_df['ingestion_timestamp']
    ).dt.date
    available_dates = sorted(
        companies_df['ingestion_date'].unique()
    )  # Get available dates
    selected_dates = st.multiselect(
        "Filter by Ingestion Dates",
        options=available_dates,
        default=available_dates
    )

    # Add a reset button
    if st.button("Reset Filters"):
        selected_index = index_options
        selected_sector = filtered_sectors
        selected_dates = available_dates
        st.experimental_rerun()  # Rerun the app to reset filters

    # Apply filters
    filtered_df = companies_df[
        (companies_df['index'].isin(selected_index)) &
        (companies_df['sector'].isin(selected_sector)) &
        (companies_df['ingestion_date'].isin(selected_dates))
    ]

    # Display the filtered table
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.warning("⚠️ No data found in the `companies` table.")
