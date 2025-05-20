# IBM Stock ETL Pipeline with Airflow, PySpark, and Docker

## 📌 Project Overview

This project is an end-to-end ETL pipeline that extracts daily IBM stock data from the [Alpha Vantage API](https://www.alphavantage.co/), transforms and cleans the data using PySpark, and uploads the processed data to an AWS S3 bucket. The workflow is orchestrated with **Apache Airflow**, and all components run inside **Docker containers** using Docker Compose.

---

## 🔧 Technologies Used

- **Apache Airflow** – Workflow orchestration
- **PySpark** – Data transformation and cleaning
- **Alpha Vantage API** – Source for daily stock data
- **AWS S3** – Destination for cleaned data
- **Docker & Docker Compose** – Containerization and orchestration

---

## 🔄 ETL Workflow

1. **Extract**:  
   The DAG calls the Alpha Vantage API to download daily stock data for IBM and saves it as a raw CSV file.

2. **Transform**:  
   A PySpark job:
   - Drops rows with missing values in key columns
   - Casts columns to appropriate data types
   - Adds a new column for daily change percentage

3. **Load**:  
   The transformed data is written to a CSV file and uploaded to an S3 bucket.

---

## 📁 Project Structure

├── dags

│ ├── stock_etl_dag.py 

│ └── transform_stock_data.py

├── requirements.txt # Python dependencies

├── Dockerfile # Custom Airflow image

└── docker-compose.yml # Multi-container setup

🛠 Future Improvements
- Add retry logic for API failures
- Enable daily scheduling in Airflow
- Add tests for PySpark transformations
- Implement logging and monitoring
