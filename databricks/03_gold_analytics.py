# Databricks notebook/source file
# Gold analytics layer for Tokyo 2021 Olympics dataset

from pyspark.sql.functions import (
    col,
    count,
    countDistinct,
    sum as spark_sum,
    round as spark_round,
    current_timestamp
)

storage_account = "sttokyo2021waigi"

silver_base_path = f"abfss://silver@{storage_account}.dfs.core.windows.net/tokyo-2021"
gold_base_path = f"abfss://gold@{storage_account}.dfs.core.windows.net/tokyo-2021"


def write_gold_table(df, table_name):
    target_path = f"{gold_base_path}/{table_name}"

    (
        df.write
        .mode("overwrite")
        .format("delta")
        .save(target_path)
    )

    print(f"Gold table written: {target_path}")


# Read Silver tables
athletes = spark.read.format("delta").load(f"{silver_base_path}/athletes")
coaches = spark.read.format("delta").load(f"{silver_base_path}/coaches")
entries_gender = spark.read.format("delta").load(f"{silver_base_path}/entries_gender")
medals = spark.read.format("delta").load(f"{silver_base_path}/medals")
teams = spark.read.format("delta").load(f"{silver_base_path}/teams")


# ------------------------------------------------------------
# 1. Medal ranking by country
# ------------------------------------------------------------
medal_rankings = (
    medals
    .select(
        col("rank"),
        col("country"),
        col("gold_medals"),
        col("silver_medals"),
        col("bronze_medals"),
        col("total_medals")
    )
    .orderBy(col("rank").asc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(medal_rankings, "medal_rankings")


# ------------------------------------------------------------
# 2. Top medal countries
# ------------------------------------------------------------
top_medal_countries = (
    medals
    .select(
        col("country"),
        col("gold_medals"),
        col("silver_medals"),
        col("bronze_medals"),
        col("total_medals")
    )
    .orderBy(col("total_medals").desc(), col("gold_medals").desc())
    .limit(20)
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(top_medal_countries, "top_medal_countries")


# ------------------------------------------------------------
# 3. Gender participation by discipline
# ------------------------------------------------------------
gender_participation_by_discipline = (
    entries_gender
    .select(
        col("discipline"),
        col("female_entries"),
        col("male_entries"),
        col("total_entries")
    )
    .withColumn(
        "female_percentage",
        spark_round((col("female_entries") / col("total_entries")) * 100, 2)
    )
    .withColumn(
        "male_percentage",
        spark_round((col("male_entries") / col("total_entries")) * 100, 2)
    )
    .orderBy(col("total_entries").desc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(gender_participation_by_discipline, "gender_participation_by_discipline")


# ------------------------------------------------------------
# 4. Athlete count by country
# ------------------------------------------------------------
athlete_count_by_country = (
    athletes
    .groupBy("noc")
    .agg(
        countDistinct("name").alias("athlete_count")
    )
    .orderBy(col("athlete_count").desc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(athlete_count_by_country, "athlete_count_by_country")


# ------------------------------------------------------------
# 5. Athlete count by discipline
# ------------------------------------------------------------
athlete_count_by_discipline = (
    athletes
    .groupBy("discipline")
    .agg(
        countDistinct("name").alias("athlete_count")
    )
    .orderBy(col("athlete_count").desc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(athlete_count_by_discipline, "athlete_count_by_discipline")


# ------------------------------------------------------------
# 6. Team count by discipline and country
# ------------------------------------------------------------
team_count_by_discipline_country = (
    teams
    .groupBy("discipline", "noc")
    .agg(
        countDistinct("name").alias("team_count")
    )
    .orderBy(col("team_count").desc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(team_count_by_discipline_country, "team_count_by_discipline_country")


# ------------------------------------------------------------
# 7. Coach count by country and discipline
# ------------------------------------------------------------
coach_count_by_country_discipline = (
    coaches
    .groupBy("noc", "discipline")
    .agg(
        countDistinct("name").alias("coach_count")
    )
    .orderBy(col("coach_count").desc())
    .withColumn("load_timestamp", current_timestamp())
)

write_gold_table(coach_count_by_country_discipline, "coach_count_by_country_discipline")


# ------------------------------------------------------------
# 8. Olympics summary metrics
# ------------------------------------------------------------
summary_metrics = spark.createDataFrame(
    [
        ("total_athletes", athletes.select("name").distinct().count()),
        ("total_countries_in_athletes", athletes.select("noc").distinct().count()),
        ("total_disciplines", athletes.select("discipline").distinct().count()),
        ("total_coaches", coaches.select("name").distinct().count()),
        ("total_teams", teams.select("name").distinct().count()),
        ("total_medal_countries", medals.select("country").distinct().count()),
        ("total_gold_medals", medals.agg(spark_sum("gold_medals")).collect()[0][0]),
        ("total_silver_medals", medals.agg(spark_sum("silver_medals")).collect()[0][0]),
        ("total_bronze_medals", medals.agg(spark_sum("bronze_medals")).collect()[0][0]),
        ("total_medals", medals.agg(spark_sum("total_medals")).collect()[0][0]),
    ],
    ["metric_name", "metric_value"]
).withColumn("load_timestamp", current_timestamp())

write_gold_table(summary_metrics, "summary_metrics")


print("Gold analytics transformation completed successfully.")
