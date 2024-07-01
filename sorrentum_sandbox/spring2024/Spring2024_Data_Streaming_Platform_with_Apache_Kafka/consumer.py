import json
import logging
from confluent_kafka import KafkaError, Consumer
import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Env:
    """
    This class is used to store the Kafka configuration and the Consumer instance.
    """

    def __init__(self, conf):
        self.conf = conf
        self.consumer = Consumer(conf)


def create_database(conn_params, dbname):
    """
    Creates a new database in the PostgreSQL server.

    Parameters:
    conn_params (dict): A dictionary containing the connection parameters.
    dbname (str): The name of the database.
    """
    conn_params_default = conn_params.copy()
    conn_params_default["dbname"] = "postgres"

    # Connect to the default database (postgres) to issue commands
    conn = psycopg2.connect(**conn_params_default)

    # Set the connection to autocommit mode
    conn.autocommit = True
    cur = conn.cursor()

    # Check if the database already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
    exists = cur.fetchone()

    # Create the database if it does not exist
    if exists:
        logging.warning(f"Database '{dbname}' already exists.")
    else:
        # Execute the command to create a new database
        try:
            cur.execute(
                f"CREATE DATABASE {dbname};"
            )  # Using f-string for database name in SQL statement
            logging.info(f"Database '{dbname}' created successfully.")
        except psycopg2.Error as e:
            logging.error(f"An error occurred: {e}")

    # Close the cursor and connection
    cur.close()
    conn.close()


def create_table(conn_params, table_name):
    """
    Creates a table in the PostgreSQL database with a predefined schema.

    Parameters:
    conn_params (dict): A dictionary containing the connection parameters.
    table_name (str): The name of the table to create.
    """
    try:
        # Establish the connection using the connection parameters
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # SQL command to create a table
                create_table_command = f"""
					CREATE TABLE IF NOT EXISTS {table_name} (
						event_type TEXT,
						event_time BIGINT,
						symbol TEXT,
						trade_id BIGINT,
						price NUMERIC,
						quantity NUMERIC,
						buyer_order_id BIGINT,
						seller_order_id BIGINT,
						trade_time BIGINT,
						is_buyer_maker BOOLEAN,
						ignore_in_price BOOLEAN
					);
				"""
                # Execute the create table command
                cur.execute(create_table_command)
                # Commit the transaction
                conn.commit()
                logging.info(f"Table '{table_name}' created successfully")

    except psycopg2.Error as e:
        # Handle exceptions that occur during the creation of the table
        logging.error(f"Failed to create table: {e}")


def validate_trade(trade):
    """
    This function validates trade record.

    Parameters:
    trade (dict): A dictionary containing a trader record.
    """
    required_keys = {"e", "E", "s", "t", "p", "q", "b", "a", "T", "m", "M"}

    # Check for missing keys
    if not required_keys.issubset(trade.keys()):
        return False, "Missing required fields"

    # Check event type
    if trade["e"] != "trade":
        return False, "Invalid event type, must be 'trade'"

    # Validate timestamps and IDs
    for key in ["E", "t", "b", "a", "T"]:
        if not isinstance(trade[key], int) or trade[key] <= 0:
            return False, f"Field {key} must be a positive integer"

    # Validate price and quantity to be positive numbers
    for key in ["p", "q"]:
        try:
            val = float(trade[key])
            if val <= 0:
                return False, f"Field {key} must be a positive number"
        except ValueError:
            return False, f"Field {key} must be a numeric value"

    # Check boolean fields
    if not isinstance(trade["m"], bool) or not isinstance(trade["M"], bool):
        return False, "Fields 'm' and 'M' must be boolean values"

    return True, "Valid trade"


def consume_from_kafka(env, topic_name):
    """
    This function consumes messages from a Kafka topic, validate, and inserts them into a PostgreSQL database.

    Parameters:
    env (Env): An instance of the Env class containing the Kafka configuration and the Consumer instance.
    topic_name (str): The name of the Kafka topic to consume messages from.
    """
    try:
        # Get the Consumer instance from the Env object
        consumer = env.consumer

        # Subscribe to the topic
        consumer.subscribe([topic_name])

        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                logging.info("Starting the consumer loop.")
                # Consumer loop
                while True:
                    # Poll for a new message
                    msg = consumer.poll(timeout=1.0)  # Poll timeout in seconds

                    if msg is None:
                        continue  # No message available within the timeout period

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            # End of partition event
                            logging.info(
                                f"Reached end of {msg.partition()} at offset {msg.offset()}"
                            )
                        else:
                            logging.error(f"Error: {msg.error()}")
                        continue

                    # process_message
                    message_data = json.loads(msg.value().decode("utf-8"))
                    logging.info(
                        f"Received message: {message_data} from partition {msg.partition()}"
                    )

                    # Validate the trade message
                    valid, message = validate_trade(message_data)

                    # Insert the trade message into the database if it is valid
                    if valid:
                        logging.info("Trade is valid. Inserting into database.")
                        insert_query = """
                            INSERT INTO binance 
                                (
                                    event_type, event_time, symbol, trade_id, price, quantity, buyer_order_id, 
                                    seller_order_id, trade_time, is_buyer_maker, ignore_in_price
                                )
                            VALUES (%(e)s, %(E)s, %(s)s, %(t)s, %(p)s, %(q)s, %(b)s, %(a)s, %(T)s, %(m)s, %(M)s);
                        """
                        cursor.execute(insert_query, message_data)
                        logging.info("Record inserted")
                        conn.commit()
                    else:
                        logging.info(f"Validation failed: {message}")

    except Exception as e:
        # Handle exceptions that occur during the consumption of messages
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        # Close the consumer when the loop ends
        logging.error("Closing the consumer.")
        consumer.close()


if __name__ == "__main__":

    # Kafka configuration
    conf = {
        "bootstrap.servers": "broker:9092",
        "group.id": "group1",
        "auto.offset.reset": "earliest",
    }

    # Create an instance of the Env class
    env = Env(conf)

    # Kafka topic name
    topic_name = "trades"

    # Connection parameters for PostgreSQL
    conn_params = {
        "dbname": "trades",
        "user": "postgres",
        "password": "postgres",
        "host": "pgdatabase",
        "port": "5432",
    }

    # Create 'trades' database
    create_database(conn_params, "trades")

    # Create 'binance' table in the database
    create_table(conn_params, "binance")

    # Consume messages from Kafka
    consume_from_kafka(env, topic_name)
