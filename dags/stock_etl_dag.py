from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import timedelta, datetime
import pandas as pd
import boto3
import os
from stock_api import fetch_alpha_vantage_data
from transform_stock_data import transform_stock_csv

# Constants
SYMBOL = "IBM"
API_KEY = "UN1RFI6DVBTCRSIE"  
LOCAL_PATH = f"/tmp/{SYMBOL}_daily.csv"
TRANSFORMED_PATH = f"/tmp/{SYMBOL}_daily_transformed.csv"
S3_BUCKET = "stock-data-finance"
S3_KEY = f"stock-data/{SYMBOL}/{SYMBOL}_daily.csv"

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def extract_stock_data(**kwargs):
    try:
        df = fetch_alpha_vantage_data(SYMBOL, API_KEY)
        if df.empty:
            raise ValueError("Empty DataFrame returned from API.")

        df.to_csv(LOCAL_PATH, index=False)
        print(f"Saved stock data to {LOCAL_PATH}")
    except Exception as e:
        raise RuntimeError(f"Extraction failed: {e}")
    
def transform_data_with_pyspark(**kwargs):
    try:
        transform_stock_csv(input_path=LOCAL_PATH, output_path=TRANSFORMED_PATH)
        print(f"Transformed data saved to {TRANSFORMED_PATH}")
    except Exception as e:
        raise RuntimeError(f"Transformation failed: {e}")

def upload_csv_to_s3(**kwargs):
    try:
        s3_hook = S3Hook(aws_conn_id="aws_conn")
        s3_hook.load_file(
            filename=TRANSFORMED_PATH,
            key=S3_KEY,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print(f"Uploaded using AWS Hook to s3://{S3_BUCKET}/{S3_KEY}")
        # Clean up local files
        os.remove(LOCAL_PATH)
        os.remove(TRANSFORMED_PATH)
    except Exception as e:
        raise RuntimeError(f"S3 upload via AWS Hook failed: {e}")


with DAG(
    dag_id='stock_etl_split_upload',
    default_args=default_args,
    description='Extract stock data and upload to S3 (2-step DAG)',
    schedule='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['stock', 's3', 'api'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_stock_data',
        python_callable=extract_stock_data
    )

    transform_task = PythonOperator(
        task_id='transform_data_with_pyspark',
        python_callable=transform_data_with_pyspark
    )

    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_csv_to_s3
    )

    extract_task >> transform_task >> upload_task


