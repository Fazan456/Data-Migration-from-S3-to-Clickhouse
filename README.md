# Data Migration from S3 to ClickHouse

This project is designed to migrate data from an S3 bucket to ClickHouse for analysis purposes. It aims to reduce cloud costs, minimize Redshift traffic, and utilize resources optimally.

## Prerequisites

- **Python**: Ensure you have Python 3 installed.
- **Apache Spark**: Make sure Apache Spark is installed and configured.
- **ClickHouse JDBC Driver**: Required JAR files are listed below.
- **AWS Credentials**: Set up your AWS credentials.

## Setup

### AWS Credentials

Export your AWS credentials using the following commands:

```bash
export AWS_ACCESS_KEY_ID='your-access-key-id'
export AWS_SECRET_ACCESS_KEY='your-secret-access-key'
```

## Python Script for S3 to ClickHouse Data Migration

This section provides a Python script for migrating data from an S3 bucket to a ClickHouse database using PySpark and the ClickHouse JDBC driver.

### Prerequisites

- Ensure you have the following JAR files:
  - `clickhouse-jdbc-0.4.0-all.jar`
  - `hadoop-aws-3.3.2.jar`
  - `aws-java-sdk-bundle-1.11.1026.jar`
  - `snappy-java-1.1.8.4.jar`
- Configure your AWS credentials in the environment variables:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
- Install the `clickhouse-connect` library.

### Script

```python
import os
from pyspark.sql import SparkSession
import clickhouse_connect

# Set AWS credentials
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''

# Initialize SparkSession
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
    # Read data from S3
    s3Data = spark.read.format("csv") \
        .option("header", "true") \
        .load("s3 file path")

    s3Data.printSchema()
    s3Data.show(5, truncate=False)

    # Initialize ClickHouse client
    client = clickhouse_connect.get_client(
        host='',
        port=8443,
        username='default',
        password='',
        secure=True
    )

    # Create ClickHouse table
    create_table_sql = """
    CREATE TABLE default.sample_table
    (
        -- table definition & data compression
    ) ENGINE = MergeTree()
    ORDER BY field;
    """
    client.query(create_table_sql)
    print("ClickHouse table created or already exists.")

    try:
        # Write data to ClickHouse
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
```

### Spark Configuration Options

- **`--master local[*]`**: Specifies that Spark should run in local mode using as many threads as there are cores on your machine.

- **`--deploy-mode client`**: Runs the Spark driver program on the machine where the `spark-submit` command is executed (client mode).

- **`--jars`**: Lists the JAR files required for the Spark job. These include:
  - `hadoop-aws-3.3.2.jar`: AWS S3 support for Hadoop.
  - `aws-java-sdk-bundle-1.11.1026.jar`: AWS Java SDK for interacting with AWS services.
  - `snappy-java-1.1.8.4.jar`: Library for Snappy compression.
  - `clickhouse-jdbc-0.4.0-all.jar`: ClickHouse JDBC driver for connecting Spark to ClickHouse.
  - `clickhouse-spark-runtime-3.4_2.12-0.7.3.jar`: ClickHouse Spark runtime integration.

- **`--conf spark.hadoop.fs.s3a.access.key='your-access-key-id'`**: AWS access key for accessing S3.

- **`--conf spark.hadoop.fs.s3a.secret.key='your-secret-access-key'`**: AWS secret key for accessing S3.

- **`--conf spark.hadoop.fs.s3a.endpoint=s3.amazonaws.com`**: Endpoint for connecting to S3.

- **`--conf spark.driver.extraClassPath`**: Specifies additional JAR files to include in the classpath for the Spark driver.

- **`--conf spark.executor.extraClassPath`**: Specifies additional JAR files to include in the classpath for the Spark executors.

- **`--conf spark.jars.packages`**: Specifies Maven coordinates of additional JARs to download and include in the classpath (Hadoop AWS and AWS SDK).

- **`--conf spark.driver.bindAddress=127.0.0.1`**: Binds the Spark driver to the localhost IP address.

- **`--conf spark.driver.host=localhost`**: Specifies the hostname of the Spark driver.

- **`--conf spark.driver.port=4040`**: Sets the port number for the Spark driver web UI.

### Running the Migration Script

To execute the migration script, use the following command:
```bash
spark-submit \
  --master local[*] \
  --deploy-mode client \
  --jars /home/mohamed-fazan2/clickhouse-jdbc-bridge/hadoop-aws-3.3.2.jar,\
/home/mohamed-fazan2/clickhouse-jdbc-bridge/aws-java-sdk-bundle-1.11.1026.jar,\
/home/mohamed-fazan2/clickhouse-jdbc-bridge/snappy-java-1.1.8.4.jar,\
/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar,\
/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-spark-runtime-3.4_2.12-0.7.3.jar \
  --conf spark.hadoop.fs.s3a.access.key='your-access-key-id' \
  --conf spark.hadoop.fs.s3a.secret.key='your-secret-access-key' \
  --conf spark.hadoop.fs.s3a.endpoint=s3.amazonaws.com \
  --conf spark.driver.extraClassPath=/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar:/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-spark-runtime-3.4_2.12-0.7.3.jar \
  --conf spark.executor.extraClassPath=/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-jdbc-0.4.0-all.jar:/home/mohamed-fazan2/clickhouse-jdbc-bridge/clickhouse-spark-runtime-3.4_2.12-0.7.3.jar \
  --conf spark.jars.packages=org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.1026 \
  --conf spark.driver.bindAddress=127.0.0.1 \
  --conf spark.driver.host=localhost \
  --conf spark.driver.port=4040 \
  new_migration.py
```

The provided Python script demonstrates how to migrate data from an S3 bucket to a ClickHouse database using PySpark and the ClickHouse JDBC driver. It reads data from an S3 bucket, creates a ClickHouse table if it doesn't exist, and writes the data to ClickHouse. To run the script, ensure that you have the necessary JAR files, configure your AWS credentials, and provide the appropriate ClickHouse connection details. The spark-submit command includes various configuration options to specify the JAR files, AWS credentials, and other settings required for the migration process. By following this approach, you can efficiently migrate data from S3 to ClickHouse for analysis purposes, reducing cloud costs and optimizing resource utilization.





