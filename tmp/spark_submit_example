from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 11),
}

with DAG(
    dag_id='spark_submit_example',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    spark_submit_task = SparkSubmitOperator(
        task_id='submit_spark_job',
        application='/opt/bitnami/spark/jobs/consume_kafka_to_postgres_batch.py',
        conn_id='spark-default',
        conf={
            'spark.master': 'spark://spark-master:7077',
        },
        jars=','.join([
            '/opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.5.4.jar',
            '/opt/bitnami/spark/jars/kafka-clients-3.6.1.jar',
            '/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.4.jar',
            '/opt/bitnami/spark/jars/commons-pool2-2.11.1.jar',
            '/opt/bitnami/spark/jars/postgresql-42.7.1.jar',
        ]),
        verbose=True,
    )
