FROM ubuntu:20.04

# Install python3 and pip3
RUN apt-get update -y && apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install confluent-kafka

ADD transactions_data_generator.py /

CMD ["python", "./transactions_data_generator.py"]
