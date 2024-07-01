# Access the latest version of jupyter/pyspark
FROM jupyter/pyspark-notebook:latest

# Allowing browser access to notebook via localhost:8888
EXPOSE 8888

# Environment variables
ENV SPARK_HOME=/usr/local/spark

ENV PYSPARK_PYTHON=python3
ENV PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH
ENV PATH=$SPARK_HOME/bin:$PATH

# Install py4j Python package
RUN pip install py4j

# Copy the notebook file into the container directory
COPY main_app.ipynb /home/jovyan/

# Start Jupyter server
CMD ["start-notebook.sh", "--NotebookApp.token=''"]
