# 📊 StockChronicle

StockChronicle is an automated system for collecting, storing, and analyzing stock prices from the S&P 500, Dow Jones, and DAX indices.
Data is ingested daily into a PostgreSQL database and used for AI-based predictions as well as interactive dashboards.

---

## 📁 Project Structure
'''
StockChronicle/
│── data/ # Rohdaten, CSVs, etc.
│── notebooks/ # Jupyter Notebooks für Analysen
│── src/ # Quellcode
│ ├── etl/ # ETL-Skripte (Extract, Transform, Load)
│ │ ├── fetch_data.py # API-Abruf
│ │ ├── transform.py # Datenverarbeitung
│ │ ├── load_db.py # Daten in Postgres speichern
│ ├── models/ # KI-Modelle für Vorhersagen
│ ├── visualization/ # Dashboards & Plots
│── tests/ # Unittests
│── .gitignore # Dateien, die nicht ins Repo sollen
│── environment.yml # Conda-Environment mit allen Abhängigkeiten
│── requirements.txt # Alternativ für Pip-Abhängigkeiten
│── README.md # Projektdokumentation
'''
---

## 🚀 Setup & Installation  

### **1️⃣ Klone das Repository**  
```bash
git clone https://github.com/dein-github-user/StockChronicle.git
cd StockChronicle
