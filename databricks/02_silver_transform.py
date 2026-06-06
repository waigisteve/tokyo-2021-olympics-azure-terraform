# Databricks notebook/source file
# Silver layer transformation for Tokyo 2021 Olympics dataset

from pyspark.sql.functions import col, trim, current_timestamp

storage_account = "sttokyo2021waigi"

bronze_base_path = f"abfss://bronze@{storage_account}.dfs.core.windows.net/tokyo-2021"
silver_base_path = f"abfss://silver@{storage_account}.dfs.core.windows.net/tokyo-2021"


def clean_column_names(df):
    """
    Standardize column names:
    - lowercase
    - trim spaces
    - replace spaces and special characters with underscores
    """
    for old_col in df.columns:
        new_col = (
            old_col.strip()
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
        )
        df = df.withColumnRenamed(old_col, new_col)
    return df


def trim_string_columns(df):
    """
    Trim whitespace from all string columns.
    """
    for field in df.schema.fields:
        if field.dataType.simpleString() == "string":
            df = df.withColumn(field.name, trim(col(field.name)))
    return df


def prepare_silver_table(df):
    """
    Apply standard silver-layer cleanup.
    """
    df = clean_column_names(df)
    df = trim_string_columns(df)
    df = df.dropDuplicates()
    df = df.withColumn("load_timestamp", current_timestamp())
    return df


def write_silver_table(df, table_name):
    target_path = f"{silver_base_path}/{table_name}"

    (
        df.write
        .mode("overwrite")
        .format("delta")
        .save(target_path)
    )

    print(f"Silver table written: {target_path}")


# Athletes
athletes = spark.read.format("delta").load(f"{bronze_base_path}/athletes")
athletes_silver = prepare_silver_table(athletes)
write_silver_table(athletes_silver, "athletes")


# Coaches
coaches = spark.read.format("delta").load(f"{bronze_base_path}/coaches")
coaches_silver = prepare_silver_table(coaches)
write_silver_table(coaches_silver, "coaches")


# Entries Gender
entries_gender = spark.read.format("delta").load(f"{bronze_base_path}/entries_gender")
entries_gender_silver = prepare_silver_table(entries_gender)

entries_gender_silver = (
    entries_gender_silver
    .withColumnRenamed("female", "female_entries")
    .withColumnRenamed("male", "male_entries")
    .withColumnRenamed("total", "total_entries")
)

write_silver_table(entries_gender_silver, "entries_gender")


# Medals
medals = spark.read.format("delta").load(f"{bronze_base_path}/medals")
medals_silver = prepare_silver_table(medals)

medals_silver = (
    medals_silver
    .withColumnRenamed("team_noc", "country")
    .withColumnRenamed("gold", "gold_medals")
    .withColumnRenamed("silver", "silver_medals")
    .withColumnRenamed("bronze", "bronze_medals")
    .withColumnRenamed("total", "total_medals")
)

write_silver_table(medals_silver, "medals")


# Teams
teams = spark.read.format("delta").load(f"{bronze_base_path}/teams")
teams_silver = prepare_silver_table(teams)
write_silver_table(teams_silver, "teams")


print("Silver transformation completed successfully.")

