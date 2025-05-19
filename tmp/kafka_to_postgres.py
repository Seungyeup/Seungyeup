from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='kafka_to_postgres_batch',
    default_args=default_args,
    start_date=datetime(2025, 4, 20),
    schedule_interval='@daily',   # 필요에 맞게 바꿔주세요
    catchup=False,
) as dag:

    # 1) Spark-submit 실행
    spark_submit = KubernetesPodOperator(
        task_id='spark_kafka_to_postgres',
        namespace='spark',
        service_account_name='spark',  # driver/executor 권한용
        image='dave126/custom-spark:3.5.4-no-kerb',
        cmds=['/opt/bitnami/spark/bin/spark-submit'],
        arguments=[
            '--master', 'k8s://https://kubernetes.default.svc:443',
            '--deploy-mode', 'cluster',
            # 추가 sparkConf / hadoopConf
            '--conf', 'spark.kubernetes.namespace=spark',
            '--conf', 'spark.hadoop.hadoop.security.authentication=simple',
            '--conf', 'spark.hadoop.hadoop.security.authorization=false',
            # 의존 JAR
            '--jars',
            'local:///opt/bitnami/spark/jars/'
            'spark-sql-kafka-0-10_2.12-3.5.4.jar,'
            'local:///opt/bitnami/spark/jars/kafka-clients-3.6.1.jar,'
            'local:///opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.4.jar,'
            'local:///opt/bitnami/spark/jars/commons-pool2-2.11.1.jar,'
            'local:///opt/bitnami/spark/jars/postgresql-42.7.1.jar',
            # 애플리케이션 파일
            'local:///opt/bitnami/spark/jobs/consume_kafka_to_postgres_batch.py',
        ],
        get_logs=True,
        name='kafka-to-postgres-batch',
        is_delete_operator_pod=True,
    )

    # 2) (선택) PostgreSQL에 정상 쓰여졌는지 검증
    check_postgres = PostgresOperator(
        task_id='verify_postgres',
        postgres_conn_id='postgres_default',
        sql="""
        SELECT COUNT(*) 
          FROM user_events_stream
        """,
    )

    spark_submit >> check_postgres
