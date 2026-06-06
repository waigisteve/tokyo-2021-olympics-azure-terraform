# Databricks notebook/source file
# Bronze layer load for Tokyo 2021 Olympics dataset

from pyspark.sql.functions import current_timestamp, col

storage_account = "sttokyo2021waigi"

raw_base_path = f"abfss://raw@{storage_account}.dfs.core.windows.net/tokyo-2021"
bronze_base_path = f"abfss://bronze@{storage_account}.dfs.core.windows.net/tokyo-2021"

files = {
    "athletes": "Athletes.csv",
    "coaches": "Coaches.csv",
    "entries_gender": "EntriesGender.csv",
    "medals": "Medals.csv",
    "teams": "Teams.csv"
}

for table_name, file_name in files.items():
    source_path = f"{raw_base_path}/{file_name}"
    target_path = f"{bronze_base_path}/{table_name}"

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(source_path)
        .withColumn("source_file", col("_metadata.file_path"))
        .withColumn("ingestion_timestamp", current_timestamp())
    )

    df.write.mode("overwrite").format("delta").save(target_path)

    print(f"Loaded {file_name} into Bronze table: {target_path}")
