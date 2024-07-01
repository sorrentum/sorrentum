# Hadoop
# Data Aggregation using Apache Hadoop

- Author: Teddy Thomas
- GitHub account: littishya21
- UMD email: tedthom1@umd.edu
- Personal email: teddylittishyathomas@gmail.com

## Project Methodology

                     +-------------------------------------+
                     |             Docker Host             |
                     +-------------------------------------+
                              |                |
                    +---------+--------------------------+
                    |                                  |
       +-----------------------------+    +-----------------------------+
       |          Docker           |    |          Docker           |
       |     Container: Hadoop    |    |     Container: Python    |
       +-----------------------------+    +-----------------------------+
                    |                                  |
       +----------------------------------+   +----------------------------------+
       |               Hadoop             |   |               Python             |
       |      - HDFS                      |   |      - Data Processing          |
       |      - MapReduce                 |   |      - MapReduce Scripts        |
       |      - YARN                      |   |      - Data Analysis            |
       +----------------------------------+   +----------------------------------+
                    |                                  |
      +------------------------------------------------------------+
      |                        Data Storage                       |
      |                 - Train.csv (BigMart Sales Data)          |
      +------------------------------------------------------------+

## Description

The project, "Data Aggregation with Apache Hadoop using Docker and Python," aims to demonstrate a robust solution for processing and analyzing large-scale datasets efficiently. Leveraging the power of Apache Hadoop, Docker, and Python, we provide a scalable and flexible platform for aggregating and deriving insights from complex data.

The dataset chosen for this project is the "BigMart Sales Data" available on Kaggle, a comprehensive collection of sales data from various BigMart outlets. This dataset offers a real-world scenario, encompassing multiple variables such as product attributes, outlet details, and sales figures, making it ideal for showcasing the capabilities of our solution.

To begin, I utilized Docker to create a containerized environment, ensuring seamless deployment and portability across different systems. Within this Docker container, deployed Apache Hadoop, an open-source framework renowned for its distributed processing capabilities. Apache Hadoop enables parallel processing of data across multiple nodes, facilitating faster analysis and computation of large datasets.

Python serves as the primary programming language for orchestrating data aggregation tasks within the Apache Hadoop ecosystem. Leveraging popular Python libraries such as Hadoop Streaming API, Pandas, and NumPy, we implement data processing pipelines to extract, transform, and aggregate information from the BigMart Sales Data.

The project workflow involves the following key steps:

Data Ingestion: Ingested the BigMart Sales Data into the Hadoop Distributed File System (HDFS), a distributed storage system optimized for handling large volumes of data.
Data Preprocessing: Using Python scripts, preprocessed the raw data to handle missing values, standardize formats, and perform any necessary transformations to prepare it for analysis.
MapReduce Aggregation: Leveraging the MapReduce paradigm, we distribute data processing tasks across multiple nodes in the Hadoop cluster. Map tasks extract relevant information from the dataset, while Reduce tasks aggregate and summarize the extracted data.
Analysis and Insights: After the aggregation process ,analyzed the aggregated data using Python's data analysis tools. Derived valuable insights to understand sales trends, product performance, and other relevant metrics.
Output Generation: Finally, generated output files summarizing the findings of our analysis, providing actionable insights for stakeholders.

## Technologies

### Hadoop: 

--> Hadoop is an open-source framework designed to handle big data processing and storage in distributed computing environments. It provides a scalable, fault-tolerant ecosystem for storing and processing vast amounts of data across clusters of commodity hardware.

--> At its core, Hadoop consists of two primary components: the Hadoop Distributed File System (HDFS) and the MapReduce programming model. HDFS is a distributed file system designed to store large datasets reliably across multiple machines. It divides files into blocks and replicates them across different nodes in the cluster to ensure fault tolerance and data availability.

--> The MapReduce programming model is a parallel processing paradigm for distributed data processing. It divides computational tasks into two phases: the Map phase and the Reduce phase. During the Map phase, input data is processed in parallel across multiple nodes in the cluster, generating intermediate key-value pairs. These intermediate results are then aggregated and processed further during the Reduce phase to produce the final output.

-->Hadoop also includes a variety of other components and modules that extend its functionality, such as:

  - YARN (Yet Another Resource Negotiator): YARN is a resource management layer that enables efficient resource allocation and job scheduling in Hadoop clusters. It allows multiple processing frameworks, such as MapReduce, Apache Spark, and Apache Flink, to run concurrently on the same cluster.
  - Hadoop Common: Hadoop Common provides the essential libraries and utilities required by other Hadoop modules. It includes tools for managing Hadoop clusters, interacting with HDFS, and performing administrative tasks.
  - Hadoop Ecosystem Projects: The Hadoop ecosystem consists of a vast array of projects and tools that integrate with Hadoop to extend its capabilities. These include Apache Hive for data warehousing, Apache Pig for data processing, Apache HBase for real-time NoSQL databases, and Apache Spark for in-memory data processing, among others.
## Docker System Overview

-> Docker is a platform that enables developers to package applications and their dependencies into containers, providing an isolated environment for seamless deployment across different systems.The Docker system is designed to set up a Hadoop environment within Docker containers to run MapReduce jobs in a distributed manner. 

Description of Files:

1. core-site.xml: Configuration file for Hadoop's core services, specifying parameters like the default file system and Hadoop's internal directories.
2. Dockerfile: This text file containing instructions for building a Docker image, including the base image, dependencies, and commands to run when the container starts.
3. execut.sh: Shell script used for executing tasks within the Docker container, often containing commands to start Hadoop services or run MapReduce jobs.
4. framework.py: Python script implementing the data processing framework, defining tasks such as data aggregation, analysis, or visualization.
5. hdfs-site.xml: Configuration file for Hadoop Distributed File System (HDFS), specifying parameters related to data replication, block size, and other storage settings.
6. mapper.py: Python script defining the mapping function for a MapReduce job, responsible for processing input data and emitting intermediate key-value pairs.
7. mapred-site.xml: Configuration file for MapReduce job execution, specifying parameters like the number of map and reduce tasks, memory allocation, and job scheduling.
8. reducer.py: Python script defining the reducing function for a MapReduce job, responsible for aggregating and processing intermediate key-value pairs to produce the final output.
9. Train.csv: The dataset file containing BigMart Sales Data, which serves as input for data processing tasks.
10. yarn-site.xml: Configuration file for Yet Another Resource Negotiator (YARN), specifying parameters for resource management, job scheduling, and application execution in Hadoop clusters.

#### References for hadoop technology deescription
    [1] https://www.oreilly.com/library/view/hadoop-the-definitive/9780596521974/

Below, I'll discuss the decisions made, the containers involved, and how they communicate.

#### --> Decisions Made

[1] Base Image

The system uses Ubuntu as the base image, upon which Java and Hadoop are installed. Ubuntu is chosen for its widespread use and ease of customization.

[2] Java and Hadoop Installation

OpenJDK 8 and Hadoop 3.3.1 are installed within the Docker image. These versions are selected based on compatibility and stability considerations.

[3] Configuration

Environment variables are set to configure Hadoop paths and other settings. Configuration files such as core-site.xml, hdfs-site.xml, mapred-site.xml, and yarn-site.xml are copied into the container to customize Hadoop's behavior.

[4] SSH Configuration

SSH is configured within the container to allow passwordless SSH connections, which are necessary for Hadoop's internal communication between nodes.

[5] Mapper and Reducer Scripts

Python scripts for Mapper and Reducer tasks, along with sample data (Train.csv), are copied into the container. These scripts are used for processing data in MapReduce jobs.

[6] Dockerfile Structure

The Dockerfile is structured to ensure efficient layer caching and readability. Each step is documented to explain its purpose and rationale.

#### --> Containers Involved:

-->The main Docker container hosts the Hadoop environment.
It includes HDFS, YARN, MapReduce, and other Hadoop components necessary for distributed data processing.

#### --> Communication Between Containers:

[1] Inter-Container Communication

Containers communicate internally through Hadoop's native communication protocols. HDFS handles storage and retrieval of data, while YARN manages resource allocation and job scheduling. MapReduce jobs are submitted to YARN, which distributes tasks to individual containers running Mapper and Reducer tasks.

[2] SSH

SSH is configured within the container to allow communication between nodes in the Hadoop cluster. This enables tasks to be executed on different nodes and for nodes to exchange data during MapReduce job execution.

## Running the Docker system by starting the container 

To run the Docker system  follow these steps:

[1] Build Docker Image
First, build the Docker image using the provided Dockerfile. Navigate to the directory containing the Dockerfile and run the following command:

 > docker build -t hadoop-cluster .

[2] Start Docker Container

Once the image is built, start a Docker container using the following command:

 > docker run -it --name hadoop-container hadoop-cluster

[3] Verify Hadoop Installation
Once inside the container, verify that Hadoop is installed and configured correctly by running Hadoop commands.

> cd /home/hadoop/data
> pwd
> hadoop fs -ls

[4] Prepare Input Data
If needed, upload input data to HDFS using the following commands:

> hadoop fs -mkdir -p input
> hdfs dfs -put Train.csv input

[5] Run MapReduce Job
After uploading input data, execute a MapReduce job using the provided scripts. 

> hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar -D mapreduce.job.reduces=5 -file mapper.py -mapper "python3 mapper.py" -file reducer.py -reducer "python3 reducer.py" -input input -output output

[6] Retrieve Output
Once the MapReduce job completes, retrieve the output from HDFS and examine the results. 

> hadoop fs -copyToLocal output .

[7] Inspect Output
Finally, inspect the output files to view the results of the MapReduce job. 

> cd output
> ls
> cat part-00001

[8] OUTPUT OBTAINED

> Breads  2204.132226294819

> Dairy   2232.5425970674455

> Frozen Foods    2132.8677436915887

> Health and Hygiene      2010.000265000001

> Soft Drinks     2006.5117348314602

The output provided represents the data aggregated value calculated for each category based on the input data processed by the MapReduce job. Each line consists of a category name followed by its corresponding average value. 

==> Category Name

The category names listed (Breads, Dairy, Frozen Foods, Health and Hygiene, Soft Drinks) represent different product categories.

==> Average Value

The average value associated with each category represents some metric or measure related to the products in that category. However, it represent various metrics such as sales volume, revenue, quantity sold, or any other numerical attribute associated with the products in each category.

==> Comparison

By comparing the average values across different categories, we can identify patterns or trends in the data.That is, if Dairy has a significantly higher average value compared to Soft Drinks, it could indicate that dairy products are more popular or more profitable than soft drinks.

==> Insights

The average values provide insights into the distribution or characteristics of products within each category. For instance, a higher average value might suggest that products in that category are more expensive or have higher sales volumes on average.

==> Decision Making

These average values can inform decision-making processes for businesses. For example, based on the average values, businesses can adjust pricing strategies, allocate resources to different product categories, or identify areas for improvement or investment.


# Project Documentation

#### [1] Dockerfile

This text file containing instructions for building a Docker image, including the base image, dependencies, and commands to run when the container starts.

##### -->  Docker file system architecture used in a diagram 
                    +----------------------------------------------------+
                    |                   Docker Host                      |
                    +----------------------------------------------------+
                              |
                              |
                              v
                    +----------------------------------------------------+
                    |                  Docker Engine                    |
                    +----------------------------------------------------+
                              |
                              |
                    +----------------------------------------------------+
                    |                  Hadoop Container                 |
                    |          (HDFS, YARN, MapReduce, SSH)             |
                    |                  Ubuntu:latest                    |
                    |            OpenJDK 8, Hadoop 3.3.1                |
                    +----------------------------------------------------+
                              |
                              |
                    +----------------------------------------------------+
                    |                Data and Scripts                   |
                    |    (mapper.py, reducer.py, Train.csv, execut.sh)  |
                    +----------------------------------------------------+

1. Use a base image with Java installed
Here, we're starting with the latest Ubuntu image as the base, and setting up the Java environment variables.

> FROM ubuntu:latest
> 
> ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64

2. Set environment variables
These lines set up environment variables related to Hadoop, like version, installation directory, and paths.

> ENV HADOOP_VERSION=3.3.1
> 
> ENV HADOOP_HOME=/usr/local/hadoop
> 
> ENV HADOOP_INSTALL=/usr/local/hadoop
> 
> ENV HADOOP_MAPRED_HOME=/usr/local/hadoop
> 
> ENV HADOOP_COMMON_HOME=/usr/local/hadoop
> 
> ENV HADOOP_HDFS_HOME=/usr/local/hadoop
> 
> ENV YARN_HOME=/usr/local/hadoop
> 
> ENV HADOOP_COMMON_LIB_NATIVE_DIR=/usr/local/hadoop/lib/native
> 
> ENV PATH=$PATH:/usr/local/hadoop/sbin:/usr/local/hadoop/bin
> 
> ENV HADOOP_OPTS="-Djava.library.path=/usr/local/hadoop/lib/native"
> 
> ENV PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin
> 
> ENV HDFS_NAMENODE_USER=root
> 
> ENV HDFS_DATANODE_USER=root
> 
> ENV HDFS_SECONDARYNAMENODE_USER=root
> 
> ENV YARN_RESOURCEMANAGER_USER=root
> 
> ENV YARN_NODEMANAGER_USER=root


3. Install dependencies
This part updates the package lists, installs necessary packages like SSH, JDK, etc., and cleans up the package cache to reduce the image size.

> RUN apt-get update && \
> 
    > apt-get install -y wget ufw ssh rsync openjdk-8-jdk openssh-server openssh-client && \
> 
    > apt-get clean && \
> 
    > rm -rf /var/lib/apt/lists/*
> 


4. Allow SSH connections through the firewall

>RUN ufw allow ssh

> RUN wget -qO- https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz | tar xvz -C /opt && \
> 
    > mv /opt/hadoop-$HADOOP_VERSION $HADOOP_HOME && \
> 
    > mkdir $HADOOP_HOME/logs && \
> 
    > chown -R root:root $HADOOP_HOME


> RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
> 
> RUN echo "export HADOOP_CLASSPATH+=\" \$HADOOP_HOME/lib/*.jar\"" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

5. Generate SSH keys and set up passwordless SSH
> RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    > cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    > chmod 700 ~/.ssh && \
    > chmod 600 ~/.ssh/authorized_keys

6. Create HDFS directories and adjust ownership
   
> RUN mkdir -p /home/hadoop/hdfs/namenode && \
> 
    > mkdir -p /home/hadoop/hdfs/datanode && \
> 
    > mkdir -p /home/hadoop/data && \
> 
    > chown -R root:root /home/hadoop/hdfs
    
7. Add Hadoop configuration files
   
> COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
> 
> COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml

> COPY mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml
> 
> COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml

> COPY mapper.py /home/hadoop/data/mapper.py
> 
> COPY reducer.py /home/hadoop/data/reducer.py
> 
> COPY framework.py /home/hadoop/data/framework.py
> 
> COPY Train.csv /home/hadoop/data/Train.csv
> 
> COPY execut.sh /home/hadoop/data/execut.sh


8. Format HDFS
   
> RUN hdfs namenode -format

9. Expose Hadoop ports
    
> EXPOSE  9870 8088

10. Start Hadoop services
> CMD [ "sh", "-c", "$HADOOP_HOME/sbin/start-all.sh && tail -f /dev/null" ]
> 
> CMD service ssh start && \
> 
    > $HADOOP_HOME/sbin/start-all.sh && \
> 
    > chmod +x /home/hadoop/data/execut.sh && \
> 
    > ./home/hadoop/data/execut.sh && \
> 
    tail -f /dev/null


### Python Scripts

#### [1] mapper.py

Python script defining the mapping function for a MapReduce job, responsible for processing input data and emitting intermediate key-value pairs fro the BigMart sales data.

                +----------------------------------------------------+
                |                 Python MapReduce System             |
                +----------------------------------------------------+
                         |
                         |  Input Data (Train.csv) & Python Scripts
                         |
                +----------------------------------------------------+
                |                  Mapper Script                     |
                |              (AggMapper class)                     |
                +----------------------------------------------------+
                         |
                         |  Inter-process Communication (stdin/stdout)
                         |
                +----------------------------------------------------+
                |                Reducer Script                      |
                |               (AggReducer class)                    |
                +----------------------------------------------------+


--> Input Data Parsing

The mapper script reads the input data line by line and parses it to extract relevant information. In the provided dataset, each line contains a label and count associated with it, representing some category and its count.

--> Key-Value Pair Emission
For each line of input data, the mapper script emits a key-value pair. The key represents the category (e.g., "Breads", "Dairy", "Frozen Foods", etc.), and the value represents the count associated with that category.

--> Intermediate Output Format

The emitted key-value pairs are separated by a tab (\t) delimiter to conform to the intermediate output format expected by the MapReduce framework.
Handling Irregular Data: The mapper script may include logic to handle irregularities or exceptions in the input data. For example, it may skip lines that cannot be parsed correctly or emit special keys for handling such cases.

##### Examples of  mapper.py Output

For the given input data, the mapper script would emit key-value pairs based on the label and count provided. For instance:

Breads\t1543: Represents the key-value pair emitted for the category "Breads" with a count of 1543.

Dairy\t21.4: Represents the key-value pair emitted for the category "Dairy" with a count of 21.4.

Other (4436)\t267: Represents the key-value pair emitted for the category "Other (4436)" with a count of 267.

The intermediate output generated by the mapper script is consumed by the reducer script for further processing, such as aggregation or analysis.

#### reducer.py
                    +----------------------------------------------------+
                    |                Reducer Script                        |
                    +----------------------------------------------------+
                                 |
                     Input (Intermediate Key-Value Pairs)
                                 |
                    +----------------------------------------------------+
                    |                  AggReducer Class                   |
                    +----------------------------------------------------+
                                 |
               Grouping by Key & Aggregation Process
                                 |
                    +----------------------------------------------------+
                    |                Output (Aggregated Results)           |
                    +----------------------------------------------------+
--> Python Reducer Script

Reduces intermediate key-value pairs generated by the Mapper script.

--> Intermediate Key-Value Pairs (stdin)

The Reducer script consumes intermediate key-value pairs emitted by the Mapper script through standard input (stdin). Each key-value pair represents a category (key) and its associated count (value).

--> Aggregation Operation (AggReducer class)

The Reducer script performs the reduce operation, which typically involves aggregating values associated with each key. In this case, the AggReducer class calculates the average value for each category by aggregating counts and dividing by the total count.

--> Final Output (stdout)

The result of the reduce operation, i.e., the aggregated values for each category, is written to standard output (stdout). Each line of output contains a category and its corresponding aggregated value.

##### Examples of reducer.py output

The reducer output represents the aggregated values for each category after processing the intermediate key-value pairs generated by the mapper script. Each line of output contains a category (key) and its corresponding aggregated value.


--> Breads 2204.132226294819

Indicates fter processing the input data, the aggregated value for the category "Breads" is 2204.132226294819.

--> Dairy 2232.5425970674455

Indicates that after processing the input data, the aggregated value for the category "Dairy" is 2232.5425970674455.

--> Frozen Foods 2132.8677436915887

Indicates that after processing the input data, the aggregated value for the category "Frozen Foods" is 2132.8677436915887.

--> Health and Hygiene 2010.000265000001

Indicates that after processing the input data, the aggregated value for the category "Health and Hygiene" is 2010.000265000001.

--> Soft Drinks 2006.5117348314602

This line indicates that after processing the input data, the aggregated value for the category "Soft Drinks" is 2006.5117348314602.


## 6. Conclusion

In conclusion, this project successfully implemented a MapReduce architecture using Python scripts and Hadoop to process and analyze a dataset. The project involved the development of Mapper and Reducer scripts to handle the data processing tasks efficiently.

The Mapper script parsed the input dataset, extracted relevant information, and emitted intermediate key-value pairs. These intermediate results were then aggregated by the Reducer script to produce final output, providing insights into the dataset's characteristics.

Throughout the project, key concepts of distributed computing, such as parallel processing and data aggregation, were effectively utilized to handle large-scale datasets. Hadoop provided the infrastructure for distributed storage and processing, enabling scalable and efficient data analysis.

The final output of the project, as demonstrated by the example provided, offered valuable insights into the dataset's categories, such as the average values or counts for each category. This information can be further utilized for various purposes, such as decision-making, trend analysis, or predictive modeling.

Overall, the project showcased the power and versatility of MapReduce programming paradigm in handling big data tasks, and demonstrated how Hadoop ecosystem can be leveraged to build scalable and robust data processing pipelines.

## Reference


[1] https://www.oreilly.com/library/view/hadoop-the-definitive/9780596521974/


