# Use a base image with Java and Python installed
FROM openjdk:8-jdk-slim

# Set environment variables for Hadoop and Java
ENV JAVA_HOME=/usr/local/openjdk-8
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=${HADOOP_HOME}/bin:${PATH}

# Install Hadoop
RUN apt-get update && \
    apt-get install -y wget && \
    wget -qO- https://archive.apache.org/dist/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz | tar xvz -C /usr/local/ && \
    mv /usr/local/hadoop-3.4.0 /usr/local/hadoop

# Install Python, pip, nltk and download punkt and stopwords
RUN apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip3 install nltk && \
    python3 -m nltk.downloader punkt && \
    python3 -m nltk.downloader stopwords

# Install vim 
RUN apt-get install -y vim

# Copy the Python mapper script into the Docker image
COPY scripts/mapper.py /usr/local/hadoop/
COPY scripts/reducer.py /usr/local/hadoop/

# Set the working directory
WORKDIR /usr/local/hadoop

# Set up Hadoop environment variables
ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop

# Run the Hadoop Streaming job when the container starts
CMD ["hadoop", "jar", "/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar", \
     "-files", "/usr/local/hadoop/mapper.py,/usr/local/hadoop/reducer.py", \
     "-input", "/usr/local/hadoop/input.txt", \
     "-output", "/usr/local/hadoop/output", \
     "-mapper", "python3 mapper.py", \
     "-reducer", "python3 reducer.py"]