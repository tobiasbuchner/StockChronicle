# 📊 StockChronicle

StockChronicle is an automated system for collecting, storing, and analyzing stock prices from the S&P 500, Dow Jones, and DAX indices.
Data is ingested daily into a PostgreSQL database and used for AI-based predictions as well as interactive dashboards.

---

## 📁 Project Structure
```
StockChronicle/
│── config/              # ✅ Configuration files
│   ├── wikipedia_sources.yaml  # Index sources & validation counts
│   ├── .env                    # Database credentials
│── data/                # Raw data, CSVs, etc.
│── notebooks/           # Jupyter Notebooks for analysis
│── src/                 # Source code
│   ├── etl/             # ETL scripts (Extract, Transform, Load)
│   │   ├── fetch_wiki_idx_corps.py  # Wikipedia data extraction script
│   │   ├── transform.py            # Data processing
│   │   ├── load_db.py              # Load data into Postgres
│   ├── models/          # AI models for predictions
│   ├── visualization/   # Dashboards & plots
│   ├── utils/           # ✅ Reusable helper functions (e.g., logging, error handling)
│   ├── db/              # ✅ Database connection handling
│       ├── db_connection.py # Handles PostgreSQL connection
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
- Adjust the `wikipedia_sources.yaml` file in the `config` directory to configure the desired indices and validation counts.

### **4️⃣ Extract and load data**
- Run the `fetch_wiki_idx_corps.py` script to extract data from Wikipedia:
```bash
python src/etl/fetch_wiki_idx_corps.py
```
- Load the extracted data into the PostgreSQL database:
```bash
python src/etl/load_db.py
```

### **5️⃣ Perform analysis and predictions**
- Use the Jupyter Notebooks in the `notebooks` directory to perform analysis and make predictions.

---

## 🧪 Run tests
- Execute the unit tests in the `tests` directory:
```bash
pytest tests/
```

---

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for more details.