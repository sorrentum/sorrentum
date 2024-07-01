from elasticsearch import Elasticsearch
from faker import Faker
import os
import random
import numpy as np
from datetime import datetime, timedelta

es_host = os.getenv("ELASTICSEARCH_HOST")
es_username = os.getenv("ELASTICSEARCH_USERNAME")
es_password = os.getenv("ELASTICSEARCH_PASSWORD")
es_ca_certs = os.getenv("ELASTICSEARCH_SSL_CERTIFICATEAUTHORITIES")

fake = Faker()

try:
    es = Elasticsearch(
        es_host,
        basic_auth=(es_username, es_password),
        ca_certs=es_ca_certs,
        verify_certs=True
    )
    
    current_time = datetime.now()
    num_samples = 10000

    def generate_log_entry():
        
        # Generate a time offset from a normal distribution
        mean = 10 * 3600  # Mean time in seconds (6 hours)
        std = 4 * 3600  # Standard deviation in seconds (2 hours)
        offset_seconds = np.random.normal(mean, std)
        offset_seconds = int(np.clip(offset_seconds, 0, 24 * 3600))  # Clip to range of 0 to 12 hours

        # Calculate the entry time
        entry_time = current_time - timedelta(seconds=offset_seconds)
        # Introduce a chance for high response times
        if random.random() < 0.005:  # 0.5% chance to have high response time
            response_time = random.randint(2000, 5000)
        else:
            response_time = fake.random_int(min=5, max=1000)

        entry = {
            "timestamp": entry_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "ip": fake.ipv4(),
            "method": random.choices(["GET", "POST", "DELETE", "PUT"], weights=[65, 22, 8, 5], k=1)[0],
            "endpoint": fake.uri_path(),
            "response_code": random.choices([200, 201, 404, 500], weights=[50, 30, 15, 5], k=1)[0],
            "response_time": response_time
        }
        return entry

    def ingest_data():
        for _ in range(num_samples):
            entry = generate_log_entry()
            response = es.index(index="web-logs", document=entry)
            print(response)

    ingest_data()

except Exception as e:
    print(f"An error occurred: {e}")
