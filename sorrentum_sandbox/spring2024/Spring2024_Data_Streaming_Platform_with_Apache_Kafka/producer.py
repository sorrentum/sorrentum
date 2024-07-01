import json
import random
import time
import logging
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer, KafkaException

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Env:
    """
    This class is used to store the Kafka configuration and the Producer and AdminClient instances.
    """

    def __init__(self, conf):
        self.conf = conf
        self.producer = Producer(conf)
        self.admin_client = AdminClient(conf)


def check_kafka_topic_created(env, topic):
    """
    This function checks if a Kafka topic exists in the cluster.

    Parameters:
    env (Env): An instance of the Env class containing the Kafka configuration.
    topic (str): The name of the topic to check.
    """
    # AdminClient instance
    admin_client = env.admin_client

    # Get the list of topics in the cluster
    cluster_metadata = admin_client.list_topics()

    # Check if the topic exists in the cluster
    return topic in cluster_metadata.topics.keys()


def create_kafka_topic(env, topic_name):
    """
    This function creates a Kafka topic in the cluster.

    Parameters:
    env (Env): An instance of the Env class containing the Kafka configuration.
    topic_name (str): The name of the topic to be created.
    """

    # AdminClient instance
    admin_client = env.admin_client
    topic = NewTopic(topic=topic_name, num_partitions=3, replication_factor=1)

    # Check if the topic already exists
    if check_kafka_topic_created(env, topic_name):
        logging.warning(f"Topic {topic_name} already exists")
    else:
        # Create the topic
        logging.info(f"Creating topic {topic_name}")
        admin_client.create_topics([topic])[topic_name].result()

        # Check if the topic was created successfully
        if check_kafka_topic_created(env, topic_name):
            logging.info(f"Topic {topic_name} created")
        else:
            logging.error(f"Topic {topic_name} not created")
            raise Exception(f"Topic {topic_name} not created")


def acked(err, msg):
    """
    Callback to handle message delivery results.

    Parameters:
    err: Error information if the message delivery failed.
    msg: The message that was attempted to be sent.
    """
    if err is not None:
        logging.error(f"Failed to deliver message: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def generate_trade():
    """
    This function simulate a trade record from Binance.

    Description of the fields:
    - e: Event type (trade)
    - E: Event time
    - s: Symbol
    - t: Trade ID
    - p: Price
    - q: Quantity
    - b: Buyer order ID
    - a: Seller order ID
    - T: Trade time
    - m: Is the buyer the market maker?
    - M: Ignore in price
    """
    # Generate a random trade record
    return {
        "e": "trade",
        "E": int(time.time() * 1000),
        "s": random.choice(["BTCUSDT", "BNBUSDT", "BNBBTC"]),
        "t": random.randint(1, 100000),
        "p": "{:.6f}".format(random.uniform(0.0001, 0.01)),
        "q": str(random.randint(1, 10000)),
        "b": random.randint(1, 500),
        "a": random.randint(501, 1000),
        "T": int(time.time() * 1000),
        "m": random.choice([True, False]),
        "M": True,
    }


def send_trade(env, topic):
    """
    This function sends a trade record to a Kafka topic.

    Parameters:
    env (Env): An instance of the Env class containing the Kafka configuration and the Producer instance.
    topic (str): The name of the Kafka topic to send the trade record to.
    """

    producer = env.producer  # Producer instance
    try:
        trade = generate_trade()  # Generate a trade record
        logging.info("Sending trade data to Kafka: %s", trade)
        # Send the trade record to the Kafka topic
        producer.produce(topic, value=json.dumps(trade), callback=acked)
        producer.poll(0)
    except KafkaException as e:
        logging.error(f"An error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Flush the producer to ensure that all messages are delivered to the broker
        producer.flush()


if __name__ == "__main__":

    # Kafka configuration
    conf = {"bootstrap.servers": "broker:9092", "queue.buffering.max.messages": 1000000}
    env = Env(conf)

    # Kafka topic name
    topic_name = "trades"

    # Create a Kafka topic
    create_kafka_topic(env, topic_name)

    while True:
        # Send trade data to Kafka
        send_trade(env, topic_name)
        time.sleep(random.randrange(0, 3))
