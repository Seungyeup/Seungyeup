from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retry_delay': timedelta(minutes=5),
    'retries': 3,
}

with DAG(
    dag_id='sparkapp_kafka_to_postgres',
    default_args=default_args,
    start_date=datetime(2025, 5, 19),
    schedule_interval=None,
    catchup=False,
) as dag:

    submit_sparkapp = SparkKubernetesOperator(
        task_id='submit_spark_application',
        namespace='spark',
        application_file='kafka-to-postgres-batch.yaml',
        kubernetes_conn_id='kubernetes_default',
        do_xcom_push=False,              # CR 상태를 XCom으로 받아올 수 있음
    )

    submit_sparkapp
