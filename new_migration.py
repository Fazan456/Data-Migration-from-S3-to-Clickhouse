import os
from pyspark.sql import SparkSession
import clickhouse_connect

os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''

spark = SparkSession.builder \
    .appName("S3 to ClickHouse") \
    .config("spark.jars", "/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar," \
                      "/home/mohamed-fazan2/clickhouse-jdbc-bridge/hadoop-aws-3.3.2.jar," \
                      "/home/mohamed-fazan2/clickhouse-jdbc-bridge/aws-java-sdk-bundle-1.11.1026.jar," \
                      "/home/mohamed-fazan2/clickhouse-jdbc-bridge/snappy-java-1.1.8.4.jar") \
    .config("spark.driver.extraClassPath", "/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar") \
    .config("spark.executor.extraClassPath", "/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ['AWS_ACCESS_KEY_ID']) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ['AWS_SECRET_ACCESS_KEY']) \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .getOrCreate()

spark.sparkContext.setLogLevel("INFO")

try:
    s3Data = spark.read.format("csv") \
        .option("header", "true") \
        .load("s3 file path")

    s3Data.printSchema()
    s3Data.show(5, truncate=False)

    client = clickhouse_connect.get_client(
        host='',
        port=8443,
        username='default',
        password='',
        secure=True
    )

    create_table_sql = """
CREATE TABLE default.sampe_table
(
table definition & data compression
) ENGINE = MergeTree()
ORDER BY field;

    """
    client.query(create_table_sql)
    print("ClickHouse table created or already exists.")

    try:
        s3Data.write \
            .format("jdbc") \
            .option("url", "") \
            .option("driver", "") \
            .option("dbtable", "") \
            .option("user", "") \
            .option("password", "") \
            .mode("append") \
            .save()
        print("Data successfully written to ClickHouse.")
    except Exception as e:
        print(f"Error writing data to ClickHouse: {e}")

except Exception as e:
    print(f"Error reading data from S3 or processing: {e}")

finally:
    spark.stop()
    print("Spark session stopped.")
