#test git

# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget tar && \
    apt-get install -y gcc python3-dev libc-dev && \
    apt-get install -y python3-distutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and setup Apache Spark
RUN wget https://downloads.apache.org/spark/spark-3.5.1/spark-3.5.1.tgz && \
    tar xzf spark-3.5.1.tgz && \
    mv spark-3.5.1 /spark && \
    rm spark-3.5.1.tgz

# Set environment variables for Spark
ENV PYSPARK_PYTHON python3
ENV SPARK_HOME /spark
ENV PATH $PATH:$SPARK_HOME/bin

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pyspark numpy matplotlib notebook

# Set up Jupyter configuration
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py

# Expose port for Jupyter Notebook
EXPOSE 8888

#Update file

# Command to run Jupyter Notebook
CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--no-browser", "--allow-root"]








