# using image for python 3.10.12
FROM python:3.10.12

WORKDIR /app
# copying full /docker directory into the container
COPY . .
# opening permissions for the cron and start shell scripts
RUN chmod 777 /app/Sparkov_Data_Generation/datagen_command.sh; chmod 777 /app/start.sh
# installing python packages
RUN pip install -r requirements.txt

RUN apt-get update
# installing java development kit to run spark
RUN apt install -y default-jdk
# copying the spark-neo4j driver into the pyspark directory
RUN cp neo4j-connector-apache-spark_2.12-5.3.0_for_spark_3.jar /usr/local/lib/python3.10/site-packages/pyspark/jars/neo4j-connector-apache-spark_2.12-5.3.0_for_spark_3.jar
# installing the spark-neo4j driver
RUN /usr/local/lib/python3.10/site-packages/pyspark/bin/spark-shell --jars /usr/local/lib/python3.10/site-packages/pyspark/bin/spark-shell/jars/neo4j-connector-apache-spark_2.12-5.3.0_for_spark_3.jar
# installing cron
RUN apt-get -y install cron

COPY cronjob /etc/cron.d/cronjob
# copying over and installing the cron job to auto-generate transaction data
RUN crontab /etc/cron.d/cronjob

# exposing port 8888 for jupyter notebook
EXPOSE 8888
# exposing port 7687 for neo4j db
EXPOSE 7687
# exposing port 4040 for the spark jobs web gui
EXPOSE 4040
# executing the shell script on start
CMD ["/app/start.sh"]
