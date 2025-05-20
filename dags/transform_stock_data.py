from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def transform_stock_csv(input_path: str, output_path: str):
    spark = SparkSession.builder \
        .appName("StockDataTransform") \
        .getOrCreate()
    # Load CSV into Spark DataFrame
    df = spark.read.option("header", True).csv(input_path)

    df_clean = df.dropna(subset=["date", "open", "close"])
    # 2. Cast columns to correct data types
    df_cast = df_clean \
        .withColumn("open", col("open").cast("double")) \
        .withColumn("close", col("close").cast("double")) \
        .withColumn("volume", col("volume").cast("long"))
    # 3. Add a new column, e.g., daily change percentage
    df_final = df_cast.withColumn(
        "daily_change_pct",
        ((col("close") - col("open")) / col("open")) * 100
    )
    df_final.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)
    spark.stop()
