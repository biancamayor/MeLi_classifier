from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime


product_id = "{{ dag_run.conf.get('product_id', 'MLB-TESTE-DEFAULT') }}"

S3_BUCKET = "s3-raw-bianca"
S3_PATH_PREFIX = "reviews_mercadolivre" 

s3_raw_output_path = f"s3://{S3_BUCKET}/{S3_PATH_PREFIX}/{product_id}/raw/reviews.csv"
s3_processed_output_path = f"s3://{S3_BUCKET}/{S3_PATH_PREFIX}/{product_id}/processed/results.json"


def workflow():
    task_scraper = DockerOperator(
        task_id="run_scraper_task",
        image="scraper-app:latest",
        container_name="task_scraper_{{ ds_nodash }}",
        command=[
            "--product-id", product_id,
            "--output-uri", s3_raw_output_path
        ],
        environment={
            'AWS_ACCESS_KEY_ID': '{{ var.value.AWS_ACCESS_KEY_ID }}',
            'AWS_SECRET_ACCESS_KEY': '{{ var.value.AWS_SECRET_ACCESS_KEY }}'
        },
        auto_remove=True,
    )


    task_analyzer = DockerOperator(
        task_id="run_analyzer_task",
        image="analyzer-app:latest",
        container_name="task_analyzer_{{ ds_nodash }}",
        command=[
            "--input-uri", s3_raw_output_path,   
            "--output-uri", s3_processed_output_path 
        ],
        environment={
            'AWS_ACCESS_KEY_ID': '{{ var.value.AWS_ACCESS_KEY_ID }}',
            'AWS_SECRET_ACCESS_KEY': '{{ var.value.AWS_SECRET_ACCESS_KEY }}'
        },
        auto_remove=True,
    )


    task_scraper >> task_analyzer




with DAG (
    dag_id="meli_orchestrator",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    _workflow = workflow()

    _workflow