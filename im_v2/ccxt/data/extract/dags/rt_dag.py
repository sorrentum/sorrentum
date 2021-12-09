import datetime

import airflow
from airflow.providers.docker.operators.docker import DockerOperator

# Pass default parameters for the DAG.
default_args = {
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),
    "email": ["d.tikhomirov@crypto-kaizen.com"],
    "email_on_failure": True,
    "owner": "test",
}

with airflow.DAG(
    dag_id="realtime_ccxt",
    description="Realtime download of CCXT OHLCV data",
    max_active_runs=1,
    default_args=default_args,
    # TODO(Danya): Improve the runtime of the script to fit into 1 minute.
    schedule_interval="*/3 * * * *",
    catchup=False,
    start_date=datetime.datetime.now(),
) as dag:
    # Pass default parameters for the script.
    # Build a bash command to execute.
    bash_command = [
        "python im_v2/ccxt/data/extract/download_realtime.py ",
        "--to_datetime {{ data_interval_start }} ",
        "--from_datetime {{ data_interval_end - macros.timedelta(5) }} "
        # TODO(Danya): Set a shared directory for the DAG (#675).
        "--dst_dir 'ccxt/ohlcv/' ",
        "--data_type 'ohlcv' ",
        "--api_keys 'API_keys.json' ",
        "--universe 'v03' ",
        "--v DEBUG",
    ]
    # Run the script.
    downloading_task = DockerOperator(
        task_id="run_ccxt_realtime",
        image="665840871993.dkr.ecr.us-east-1.amazonaws.com/cmamp:dev",
        command=bash_command,
        default_args=default_args,
    )
