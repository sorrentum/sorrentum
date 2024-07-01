## Streaming Word Count with Apache Spark Streaming

### Author Info
Author: Meghana Kolanu
GitHub account: meghanakolanu
UMD email: mkolanu@umd.edu

### Introduction
In this project, we leverage Apache Spark Streaming, a real-time processing framework, to implement a streaming word count application. The application processes continuous streams of text data, conducts word count aggregation within micro-batch intervals, and visualizes real-time insights. Apache Spark Streaming offers scalability, fault-tolerance, and integration with the Apache Spark system, making it an ideal choice for processing large-scale data streams in real-time. 

### Technology Used: Apache Spark Streaming
Apache Spark Streaming represents a prominent foundation in the domain of real-time data processing, fundamentally altering the landscape by extending the core Apache Spark API to facilitate scalable, fault-tolerant stream processing of live data streams. Traditional batch processing frameworks, with their emphasis on static datasets, are overshadowed by the dynamic capabilities of Apache Spark Streaming, which empowers organizations to engage in real-time processing and analysis with minimal latency. The standout features of this technology, which include robust scalability, fault tolerance mechanisms, and seamless integration capabilities, indicate a model shift in the approach to data streaming and utilization.

At its core, Apache Spark Streaming derives its exceptional scalability from tapping into the innate scalability of Apache Spark. This capability enables distributed processing of large-scale data streams across multiple nodes, ensuring that organizations can effectively navigate escalating data volumes and processing demands without compromising performance or reliability. The fault tolerance mechanisms embedded within Apache Spark Streaming, such as lineage information and resilient distributed datasets (RDDs), serve as steadfast safeguards against disruptions, ensuring the consistent processing of data streams even in the face of failures or network disturbances.

Furthermore, the seamless integration of Apache Spark Streaming with other components of the Apache Spark ecosystem, including Spark SQL, MLlib, and GraphX, amplifies its appeal and utility. This integration fosters the development of comprehensive stream processing pipelines encompassing a diverse array of data processing and analytics functionalities. By leveraging these integrated components, Apache Spark Streaming furnishes organizations with a unified platform for real-time data processing and analysis, streamlining both the development and deployment processes.

Nevertheless, Apache Spark Streaming presents certain challenges as well. Among these is the inherent complexity associated with setting up and managing a Spark cluster tailored for streaming processing. This complexity manifests in the meticulous configuration and optimization of cluster resources, navigation of dependencies, and adept management of infrastructure requirements. Additionally, achieving proficiency in Apache Spark Streaming necessitates a deep understanding of distributed computing concepts and adept navigation of Spark's programming model, thereby presenting a learning curve for developers.

From an educational standpoint in relation to the class material, Apache Spark Streaming serves as a channel for deeper exploration into distributed computing and stream processing, embodying the principles and techniques explained in academic curriculum. It serves as a practical phenomenon of real-time data processing pipelines, providing students with invaluable insights into scalable, fault-tolerant stream processing methodologies and equipping them with the requisite skills to conceive, develop, and deploy real-time analytics applications in distributed environments.

References:
1. *Spark Streaming Programming Guide- Spark 3.5.1 Documentation.* Available at https://spark.apache.org/docs/latest/streaming-programming-guide.html
2. *Apache spark- Streaming- Word Count hands on CloudXLab.* Available at https://cloudxlab.com/assessment/displayslide/458/apache-spark-streaming-wordcount-hands-on


### Docker System Architecture**
**Dockerfile**	

The Docker system created for this project facilitates the execution of a Python script for streaming word count with Apache Spark Streaming. Within the Dockerfile, the foundation is laid with the selection of the official Python runtime image, specifically version 3.8-slim, chosen for its lightweight nature, which fosters an efficient Python environment ideal for script execution. 

The subsequent directive WORKDIR /app establishes /app as the working directory within the container. This strategic decision facilitates organizational coherence, ensuring that all subsequent commands execute within this designated workspace. The COPY . /app command copies all files and directories from the host machine's current directory to the /app directory within the container. This inclusive approach ensures that the Docker image encapsulates all necessary project components, including the Python script for streaming word count, along with any supplementary files or resources. By incorporating the project files into the container, the Dockerized environment becomes self-contained, enabling seamless deployment and execution. 

The Dockerfile proceeds with the installation of system dependencies essential for subsequent operations. This includes executing a series of apt-get commands to update package repositories and install critical utilities such as wget, tar, gcc, python3-dev, libc-dev, and python3-distutils. These utilities lay the groundwork for downloading and extracting the Apache Spark distribution, a pivotal step in provisioning the container with the requisite Spark runtime environment and dependencies. The subsequent series of commands orchestrates the download and setup of Apache Spark within the container. These operations involve fetching the Spark distribution archive from the official Apache Spark repository using wget, followed by extracting the contents and relocating the extracted directory to /spark within the container. This pivotal step furnishes the Dockerized environment with the necessary Spark runtime environment, enabling seamless integration and execution of Spark-related operations. 

The Dockerfile meticulously configures environment variables essential for seamless interaction with the Spark environment. This includes setting PYSPARK_PYTHON to python3, specifying the Python interpreter to be used by Spark, and configuring SPARK_HOME and PATH to point to the Spark installation directory and its binary executables. Such meticulous configuration simplifies access to Spark commands from any location within the container, enhancing operational efficiency and convenience. 

The subsequent directives utilize pip to install Python dependencies crucial for executing the Python script and interfacing with Spark. This includes upgrading pip to the latest version to ensure compatibility and subsequently installing pyspark, numpy, matplotlib, and notebook. These dependencies encompass the necessary Spark bindings, numerical computing capabilities, and visualization libraries, equipping the Dockerized environment with the requisite tools for executing the streaming word count Python script seamlessly.

The Dockerfile concludes with the setup of Jupyter Notebook configuration to facilitate interactive computing and visualization. This involves generating the Jupyter configuration file using jupyter notebook --generate-config and appending a configuration parameter to disable token authentication, thereby simplifying access. By configuring Jupyter in this manner, the Dockerized environment becomes conducive to interactive experimentation and exploration, fostering a collaborative and iterative workflow. Lastly, the Dockerfile exposes port 8888, the default port used by Jupyter Notebook, to enable external access. Additionally, the final CMD directive specifies the command to be executed upon container startup. In this case, it initiates the execution of Jupyter Notebook with specific parameters (--ip, --no-browser, --allow-root) to enable remote access and disable browser auto-launch. This command effectively kickstarts the Jupyter Notebook server, enabling users to interact with the Python script and perform streaming word count operations via a web interface.
    
**Docker-compose.yml**
Meanwhile, the docker-compose.yml file choreographs the deployment of the Docker container, harmonizing the orchestration of resources for Python script execution. Here, the service definition delineates a singular service, aptly named pyspark_app, corresponding to the Docker image crafted from the Dockerfile. The build configuration section orchestrates the build process, defining the build context and the Dockerfile to use for image construction. Volume mounting emerges as a pivotal feature, facilitating the live updates of the Python script directory from the host machine to the /app directory within the container, obviating the need for image rebuilding and expediting development and debugging endeavors. Environment configuration ensures Python 3 compatibility by setting the PYSPARK_PYTHON environment variable. Finally, the command configuration section prescribes the command to trigger the execution of the Python script upon container initiation, thus igniting the streaming word count process with Apache Spark Streaming.

**Container Communication**
In this setup, only one container (‘pyspark_app’) is involved. The container executes the Python script using Apache Spark Streaming to perform streaming word count. There is no explicit communication between containers since all the required functionality is within a single container. 

**Decision Explanation**
The slim version of the official Python runtime image was chosen to minimize the image size and resource footprint, enhancing efficiency and portability. Apache Spark is downloaded and installed within the container to provide the necessary runtime environment for executing Spark jobs seamlessly. Also, by mounting the script directly as a volume allowed live code updates without the need for rebuilding the Docker image, establishing rapid development and debugging. Finally, setting the environment variable ‘PYSPARK_PYTHON’ ensured compatibility with Python 3, which is necessary for executing the Python script. 

**Run the System**

To run the system, you first need to build a Docker image containing the necessary dependencies and configuration. This is achieved using the docker build command. Upon executing docker build -t my-pyspark-app ., Docker begins the build process defined in the Dockerfile located in the current directory (.). The output provides a step-by-step log of each action taken during the build, including downloading dependencies, installing packages, and configuring the environment. Once the build completes successfully, Docker creates the image named my-pyspark-app.

Next, you start a Docker container using the built image with the docker run command: docker compose up. 

By specifying -p 8888:8888, you map port 8888 on the host to port 8888 in the container, allowing access to the Jupyter Notebook server running inside the container. As the container starts, Jupyter Notebook server extensions and configurations are initialized, and the server starts running. The output displays information about the running Jupyter server, including the URL where it is accessible. docker run -p 8888:8888 my-pyspark-app

To access the Jupyter Notebook server, you can use the provided URL (http://localhost:8888/?token=<token>) in a web browser. This URL allows you to interact with the Jupyter Notebook interface and execute the Python code for streaming word count with Apache Spark Streaming.
jupyter server list
Currently running servers:
http://localhost:8888/?token=f00f86ffa25501992974d7ece829fead05023d3c4f5b90d5 :: 
http://localhost:8890/ :: 

Copy the files into the docker container: 
docker cp /Users/meghanakolanu/src/sorrentum1/sorrentum_sandbox/projects/Spring2024_Streaming_Word_Count_with_Apache_Spark_Streaming/. 574596761e9104f9702fdc1d2654dbccba0a0b1d96d73763d2158dc638a91331:/app

Execute the container: 
docker exec -it 574596761e9104f9702fdc1d2654dbccba0a0b1d96d73763d2158dc638a91331 bash

If you need to stop and restart the container later, you can use the docker stop and docker start commands, respectively, followed by the container ID or name. Additionally, you can list all running containers using docker ps, which provides information such as the container ID, image used, command running inside the container, and port mappings.

Overall, these commands and outputs demonstrate how to set up and run the system using Docker, enabling easy deployment and execution of the streaming word count application with Apache Spark Streaming.

### Python Script Overview
The Real-Time Word Count with Apache Spark Streaming application is designed to process streaming data, specifically text files containing song lyrics, and generate word counts in near real-time. Let's break down the script's functionality into several sections:

1. Initialization and Setup:
The script begins by importing necessary libraries such as pyspark, matplotlib, and pandas.
It then initializes the SparkContext (sc) and StreamingContext (ssc) objects, sets up the SparkSession (spark), and defines the function process_stream for processing streaming data.

2. Data Loading and Preprocessing:
The script reads CSV data containing Billboard song lyrics using Spark's DataFrame API. The dataset includes fields like "Rank" and "Lyrics."
It tokenizes the lyrics using Spark's Tokenizer and removes stop words using StopWordsRemover, producing a DataFrame with cleaned words.

3. Real-Time Word Count:
Within the process_stream function, streaming data is processed in micro-batches of 5 seconds.
Each RDD (Resilient Distributed Dataset) in the stream is processed to extract individual words, group them by count, and sort them in descending order.
The top 10 words along with their counts are displayed and visualized using Matplotlib, providing insights into the most frequently occurring words in the streaming data.

4. Streaming Execution:
The script sets up a DStream (Discretized Stream) by reading text files from the specified directory (data_dir).
It defines the processing logic (process_stream) to be applied to each RDD in the stream using foreachRDD.
Finally, it starts the streaming process (ssc.start()) and waits for it to finish (ssc.awaitTermination()).

Example Output:
The script outputs the top 10 words in the Billboard song lyrics dataset, along with their respective counts, in near real-time.
It visualizes the word counts using a bar plot, providing a clear representation of the most common words. In addition, it prints out the results including total word count, average word length, most common word, its count, and the number of unique words and shows the visualization. 

**Database Scheme**
The database schema employed by the application offers a structured framework for organizing song-related data, facilitating efficient storage and retrieval of information. It encompasses essential fields such as "Rank," denoting a song's position in the Billboard chart, providing a metric for popularity. "Song" serves as a repository for song titles, enabling easy identification and reference. "Artist" stores the names of musicians or bands responsible for performing the songs, ensuring proper attribution and categorization. "Year" captures the release year of each song, aiding in chronological analysis and historical context. The "Lyrics" field holds the textual content of the songs, allowing for textual analysis and sentiment assessment. Lastly, the "Source" field indicates the origin of the lyrics, providing insights into data provenance and quality. Together, these schema components form a cohesive framework that supports comprehensive song data management and analysis within the application.

The mock database follows a simple JSON structure: 
{
  "1": {
    "Rank": 1,
    "Song": "Wooly Bully",
    "Artist": "Sam the Sham and the Pharaohs",
    "Year": 1965,
    "Lyrics": "Sam the Sham miscellaneous Wooly Bullywooly"
  }
}


### Project Diagram
[Link](https://mermaid.live/view#pako:eNplkU1ugzAQha9iedVKyQVYVGogJCRdVIWmC8hiBJPECtjIjPsTxN1rjJU2rTf2vO_N-Fnueakq5AE_1OqjPIEmlkWFZHY95hEQsFQZXWLAwnTHYlHjns3nD2xxl7agzyl2nVCSJVKQgFpcgGx5Pw1YOGfYZ-qMUlxQD5MeOj3KU1Ltm9JVx16wUe9Q7yceOb7MR8ZCZSR5sHQgzneiM9fLPIsdW9mhGqER8mg7JeEn_cnm7StnX1v7-ORrk6drR5P8WavSvtBzDxMHN__jbRzY3sZjr20FhN6ynQb7Yjw__Uqcobb7T0w-442VQFT2g_pRKTidsMGCB_ZY4QFMTQUv5GCtYEilX7LkAWmDM27cxZGAo4ZmEodvvxOd_g)
![image](https://github.com/kaizen-ai/kaizenflow/assets/99992251/05cd32fe-687e-4dde-85f7-10b774386084)

flowchart TD
    A[Data Source: CSV File] --> B(SparkSession Initialization)
    B --> C{Tokenizer}
    C --> D[StopWords Removal]
    D --> E[Word Count]
    E --> F[Visualization]
    F --> G[Streaming Context Initialization]
    G --> H[Start Streaming]
    H --> I[Process Stream]
    I --> J[Word Count]
    J --> K[Visualization Update]
    K --> I
    K--> L[Streaming Termination]


### Conclusion
The Streaming Word Count with Apache Spark Streaming project demonstrates the effectiveness of real-time data processing using Apache Spark Streaming in conjunction with Python. By ingesting streaming text data, tokenizing, filtering, and conducting word count aggregation within micro-batch intervals, the project showcases the capability of Spark Streaming to handle continuous streams of data efficiently. Through clear logical structure, practical examples, and illustrated diagrams, the project provides a comprehensive understanding of real-time processing concepts and their implementation using Spark Streaming.

The seamless integration of Spark Streaming with other Python libraries such as Matplotlib and scikit-learn enhances the project's functionality, allowing for real-time visualization and machine learning-based analysis. By leveraging Docker containers, the project ensures consistency and portability of the development environment, facilitating deployment across different platforms. With its focus on optimizing data processing, minimizing latency, and improving system responsiveness, the project serves as a valuable resource for developers seeking to implement real-time analytics solutions. Furthermore, it provides a foundation for exploring advanced features of Spark Streaming, scalability considerations, and integration with external systems for enhanced functionality.

Overall, the Streaming Word Count with Apache Spark Streaming project offers a practical and insightful approach to real-time data processing, empowering developers to build robust and scalable streaming applications. It lays the groundwork for further exploration and experimentation in the realm of real-time analytics and streaming data processing.
