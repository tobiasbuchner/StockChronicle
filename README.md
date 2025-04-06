# 📊 StockChronicle

StockChronicle is an automated system for collecting, storing, and analyzing stock prices from the S&P 500, Dow Jones, and DAX indices.  
Data is ingested daily into a PostgreSQL database and used for AI-based predictions as well as interactive dashboards.

---

## 📁 Project Structure
```
StockChronicle/
│── config/              # Configuration files
│   ├── config.yaml             # Centralized configuration file
│   ├── .env                    # Database credentials
│── data/                # Raw data, CSVs, etc.
│   ├── wiki_corps/             # Extracted Wikipedia data
│   ├── yfin_ohlc/              # Yahoo Finance OHLC data
│   ├── yfin_company_data/      # Yahoo Finance company details
│── logs/                # Log files
│   ├── fetch_wiki_corps.log    # Logs for Wikipedia extraction
│   ├── fetch_yfin_ohlc.log     # Logs for Yahoo Finance OHLC extraction
│   ├── load_wiki_corps.log     # Logs for loading Wikipedia data into Postgres
│── notebooks/           # Jupyter Notebooks for analysis
│── src/                 # Source code
│   ├── database/        # Database schema creation and management
│   │   ├── create_schema.py    # Script to create database schema
│   ├── etl/             # ETL scripts (Extract, Transform, Load)
│   │   ├── fetch_wiki_corps.py  # Wikipedia data extraction script
│   │   ├── fetch_yfin_ohlc.py   # Yahoo Finance OHLC data extraction script
│   │   ├── fetch_company_info.py  # Yahoo Finance company details extraction script
│   │   ├── load_wiki_corps_postgres.py  # Load Wikipedia data into Postgres
│   │   ├── load_ohlc_postgres.py  # Load OHLC data into Postgres
│   ├── models/          # AI models for predictions
│   ├── visualization/   # Dashboards & plots
│   ├── utils/           # Reusable helper functions
│   │   ├── logger.py           # Centralized logging setup
│   │   ├── db_utils.py         # Database utility functions
│   │   ├── config_loader.py    # YAML configuration loader
│   │   ├── file_utils.py       # File management utilities
│── tests/               # Unit tests
│── .gitignore           # Files to ignore in Git
│── environment.yml      # Conda environment dependencies
│── requirements.txt     # Alternative for pip dependencies
│── README.md            # Project documentation
```

---

## 🚀 Setup & Installation  

### **1️⃣ Clone the repository**
```bash
git clone https://github.com/your-github-username/StockChronicle.git
cd StockChronicle
```

### **2️⃣ Install required dependencies**
#### With Conda:
```bash
conda env create -f environment.yml
conda activate stockchronicle
```
#### With pip:
```bash
pip install -r requirements.txt
```

### **3️⃣ Set up configuration files**
- Create a `.env` file in the `config` directory with your database credentials:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
```
- Adjust the `config.yaml` file in the `config` directory to configure paths, cleanup settings, and data sources.

### **4️⃣ Create the database schema**
- Run the `create_schema.py` script to create the required tables in the PostgreSQL database:
```bash
python src/database/create_schema.py
```

### **5️⃣ Extract and load data**
#### Extract company data from Wikipedia:
```bash
python src/etl/fetch_wiki_corps.py
```
#### Load the extracted data into the PostgreSQL database:
```bash
python src/etl/load_wiki_corps_postgres.py
```
#### Extract OHLC (Open, High, Low, Close) data from Yahoo Finance:
```bash
python src/etl/fetch_yfin_ohlc.py
```
#### Extract company details from Yahoo Finance:
```bash
python src/etl/fetch_company_info.py
```
#### Load the OHLC data into the PostgreSQL database:
```bash
python src/etl/load_ohlc_postgres.py
```

### **6️⃣ Perform analysis and predictions**
- Use the Jupyter Notebooks in the `notebooks` directory to perform analysis and make predictions:
```bash
jupyter notebook
```

---

## 🧪 Run tests
- Execute the unit tests in the `tests` directory to ensure everything is working as expected:
```bash
pytest tests/
```

---

## 🛠️ Key Features
- **Centralized Utilities**:
  - Logging: All scripts use a centralized logger from `logger.py`.
  - Configuration: All scripts load settings from `config.yaml` using `config_loader.py`.
  - Database Management: Database connections and queries are handled via `db_utils.py`.
  - File Management: File cleanup and other utilities are managed via `file_utils.py`.
- **Automated ETL Pipelines**:
  - Extract data from Wikipedia and Yahoo Finance, transform it, and load it into a PostgreSQL database.
- **AI-Powered Predictions**:
  - Use machine learning models to predict stock trends and prices.
- **Interactive Dashboards**:
  - Visualize stock data and predictions with interactive plots and dashboards.
- **Modular Design**:
  - Reusable components for logging, database management, and data validation.

---

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## 📞 Support
If you encounter any issues or have questions, feel free to open an issue on GitHub or contact the project maintainer.

---

## 🌟 Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

---

## 📚 References
- [Wikipedia API Documentation](https://www.mediawiki.org/wiki/API:Main_page)
- [Yahoo Finance API Documentation](https://finance.yahoo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)