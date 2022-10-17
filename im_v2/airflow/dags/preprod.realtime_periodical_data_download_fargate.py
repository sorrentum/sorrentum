# This DAG is used to download realtime data to the database.


import airflow
from airflow.contrib.operators.ecs_operator import ECSOperator
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
import copy
import datetime
from itertools import product
import os

_FILENAME = os.path.basename(__file__)

# This variable will be propagated throughout DAG definition as a prefix to
# names of Airflow configuration variables, allow to switch from test to preprod/prod
# in one line (in best case scenario).
_STAGE = _FILENAME.split(".")[0]
assert _STAGE in ["prod", "preprod", "test"]

# Used for seperations of deployment environments
# ignored when executing on prod/preprod.
_USERNAME = ""

# Deployment type, if the task should be run via fargate (serverless execution)
# or EC2 (machines deployed in our auto-scaling group)
_LAUNCH_TYPE = "fargate"
assert _LAUNCH_TYPE in ["ec2", "fargate"]

_DAG_ID = _FILENAME.rsplit(".", 1)[0]
_EXCHANGES = ["binance"]
_PROVIDERS = ["ccxt"]
_UNIVERSES = {"ccxt": "v7"}
#_CONTRACTS = ["spot", "futures"]
_CONTRACTS = ["spot", "futures"]
#_DATA_TYPES = ["ohlcv", "bid_ask"]
_DATA_TYPES = ["ohlcv"]
# How many levels deep in to order book
# to downlaod per iteration per symbol
_BID_ASK_DEPTH = 10
# How often should a downloader within a single container run.
# TODO{Juraj): change to seconds after # CmTask2817.
# (In minutes)
_DOWNLOAD_INTERVAL = {"ohlcv": 1, "bid_ask": 1}
# Specify how long should the DAG be running for (in minutes).
_RUN_FOR = 60
# Specify how much in advance should the DAG be scheduled (in minutes).
# We leave a couple minutes to account for delay in container setup
# such that the download can start at a precise point in time.
_DAG_STANDBY = 6
_DAG_DESCRIPTION = f"Realtime {_DATA_TYPES} data download, contracts:" \
                + f"{_CONTRACTS}, using {_PROVIDERS} from {_EXCHANGES}."
# Specify when/how often to execute the DAG.
_SCHEDULE = Variable.get(f'{_DAG_ID}_schedule')

# Used for container overrides inside DAG task definition.
# If this is a test DAG don't forget to add your username to container suffix.
# i.e. cmamp-test-juraj since we try to follow the convention of container having
# the same name as task-definition if applicable
# Set to the name your task definition is suffixed with i.e. cmamp-test-juraj,
_CONTAINER_SUFFIX = f"-{_STAGE}" if _STAGE in ["preprod", "test"] else ""
_CONTAINER_SUFFIX += f"-{_USERNAME}" if _STAGE == "test" else ""
_CONTAINER_NAME = f"cmamp{_CONTAINER_SUFFIX}"

# E.g. DB table ccxt_ohlcv -> has an equivalent for testing ccxt_ohlcv_test
# but production is ccxt_ohlcv.
_TABLE_SUFFIX = f"_{_STAGE}" if _STAGE in ["test", "preprod"] else ""

ecs_cluster = Variable.get(f'{_STAGE}_ecs_cluster')
# The naming convention is set such that this value is then reused
# in log groups, stream prefixes and container names to minimize
# convolution and maximize simplicity.
ecs_task_definition = _CONTAINER_NAME

# Subnets and security group is not needed for EC2 deployment but
# we keep the configuration header unified for convenience/reusability.
ecs_subnets = [Variable.get("ecs_subnet1")]
ecs_security_group = [Variable.get("ecs_security_group")]
ecs_awslogs_group = f"/ecs/{ecs_task_definition}"
ecs_awslogs_stream_prefix = f"ecs/{ecs_task_definition}"

# Pass default parameters for the DAG.
default_args = {
    "retries": 0,
    "email": [Variable.get(f'{_STAGE}_notification_email')],
    "email_on_failure": True if _STAGE == ["prod", "preprod"] else False,
    "owner": "airflow",
}

# Create a command, leave values to be parametrized.
bash_command = [
    "/app/amp/im_v2/{}/data/extract/download_realtime_for_one_exchange_periodically.py",
    "--exchange_id '{}'",
    "--universe '{}'",
    "--db_table '{}'",
    "--data_type '{}'",
    "--contract_type '{}'",
    "--db_stage 'dev'",
    "--interval_min '{}'",
    # This argument gets ignored for OHLCV data type.
    f"--bid_ask_depth '{_BID_ASK_DEPTH}'",
    "--aws_profile 'ck'",
    # At this point we set up a logic for real time execution
    # Start date is postponed by _DAG_STANDBY minutes and a short
    # few seconds delay to ensure the bars from the nearest minute are finished.
    "--start_time '{{ execution_date + macros.timedelta(minutes=var.value.rt_data_download_run_for_min | int + var.value.rt_data_download_standby_min | int, seconds=5) }}'",
    "--stop_time '{{ execution_date + macros.timedelta(minutes=2*(var.value.rt_data_download_run_for_min | int) + var.value.rt_data_download_standby_min | int, seconds=15) }}'",
]

# Create a DAG.
dag = airflow.DAG(
    dag_id=_DAG_ID,
    description=_DAG_DESCRIPTION,
    max_active_runs=2,
    default_args=default_args,
    schedule_interval=_SCHEDULE,
    catchup=False,
    start_date=datetime.datetime(2022, 7, 1, 0, 0, 0),
)

start_task = DummyOperator(task_id="start", dag=dag)
end_task = DummyOperator(task_id="end", dag=dag)


for provider, exchange, contract, data_type in product(_PROVIDERS, _EXCHANGES, _CONTRACTS, _DATA_TYPES):

    table_name = f"{provider}_{data_type}"
    #TODO(Juraj): CmTask2804.
    if contract == "futures":
        table_name += "_futures"
    table_name += _TABLE_SUFFIX

    # Do a deepcopy of the bash command list so we can reformat params on each iteration.
    curr_bash_command = copy.deepcopy(bash_command)
    curr_bash_command[0] = curr_bash_command[0].format(provider)
    curr_bash_command[1] = curr_bash_command[1].format(exchange)
    curr_bash_command[2] = curr_bash_command[2].format(_UNIVERSES[provider])
    curr_bash_command[3] = curr_bash_command[3].format(table_name)
    curr_bash_command[4] = curr_bash_command[4].format(data_type)
    curr_bash_command[5] = curr_bash_command[5].format(contract)
    curr_bash_command[7] = curr_bash_command[7].format(_DOWNLOAD_INTERVAL[data_type])

    kwargs = {}
    kwargs["network_configuration"] = {
        "awsvpcConfiguration": {
            "securityGroups": ecs_security_group,
            "subnets": ecs_subnets,
        },
    }

    downloading_task = ECSOperator(
        task_id=f"rt_download_{provider}_{exchange}_{data_type}_{contract}",
        dag=dag,
        aws_conn_id=None,
        cluster=ecs_cluster,
        task_definition=ecs_task_definition,
        launch_type=_LAUNCH_TYPE.upper(),
        overrides={
            "containerOverrides": [
                {
                    "name": _CONTAINER_NAME,
                    "command": curr_bash_command,
                }
            ]
        },
        awslogs_group=ecs_awslogs_group,
        awslogs_stream_prefix=ecs_awslogs_stream_prefix,
        # just as a small backup mechanism.
        execution_timeout=datetime.timedelta(minutes=_RUN_FOR + (2 * _DAG_STANDBY)),
        **kwargs
    )
    # Define the sequence of execution of task.
    start_task >> downloading_task >> end_task