import json
from typing import Tuple
from pyflink.common import SimpleStringSchema, WatermarkStrategy, Types, Time, Row
from pyflink.datastream import StreamExecutionEnvironment, MapFunction, AggregateFunction
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, KafkaSink, \
    KafkaRecordSerializationSchema
from pyflink.datastream.formats.json import JsonRowSerializationSchema
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.table import *
from pyflink.table.expressions import call, col, lit
from pyflink.table.window import Tumble

# Defining a class to parse JSON data
class ParseMapFunction(MapFunction):

    def map(self, data):
        json_data = json.loads(data)
        return json_data['client'], json_data['amount']

# Defining an aggregate function to sum values
class SumAggregate(AggregateFunction):

    def create_accumulator(self) -> Tuple[int, int]:
        return 0, 0

    def add(self, value: Tuple[int, int], accumulator: Tuple[int, int]) -> Tuple[int, int]:
        return value[0], accumulator[1] + value[1]

    def get_result(self, accumulator: Tuple[int, int]) -> Tuple[int, int]:
        return Row(accumulator[0], accumulator[1])

    def merge(self, a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
        return a[0], a[1] + b[1]

# Function to process JSON data
def process_json_data():
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)
    # ensures that memory management is handled by Flink for Python functions and code execution
    t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)
    
    # Defining DDL for Kafka source and Elasticsearch sink
    create_kafka_source_ddl = """
            CREATE TABLE transaction_msg(
                client INT,
                amount INT,
                ts TIMESTAMP(3),
                WATERMARK FOR ts AS ts
            ) WITH (
              'connector' = 'kafka',
              'topic' = 'client_amount',
              'properties.bootstrap.servers' = 'kafka:9092',
              'properties.group.id' = 'test',
              'scan.startup.mode' = 'latest-offset',
              'format' = 'json'
            )
            """

    create_es_sink_ddl = """
            CREATE TABLE es_sink(
                client INT PRIMARY KEY NOT ENFORCED,
                window_start TIMESTAMP(3),
                window_end TIMESTAMP(3),
                total_amount INT
            ) with (
                'connector' = 'elasticsearch-7',
                'hosts' = 'http://elasticsearch:9200',
                'index' = 'total_amount',
                'document-id.key-delimiter' = '$',
                'format' = 'json'
            )
    """
    # Executing DDL to create Kafka source and Elasticsearch sink
    t_env.execute_sql(create_kafka_source_ddl)
    t_env.execute_sql(create_es_sink_ddl)

    transaction_data = t_env.from_path("transaction_msg") 
    # Sending results to Elasticsearch sink with tumbling window of 1 minute
    results = transaction_data.window(Tumble.over(lit(1).minutes).on(col("ts")).alias("w")) \
        .group_by(col("w"), col("client")) \
        .select(col("client"), col("w").start.alias("window_start"), col("w").end.alias("window_end"), col("amount").sum.alias("total_amount")) \
        .execute_insert("es_sink")
    

if __name__ == '__main__':
    process_json_data()
