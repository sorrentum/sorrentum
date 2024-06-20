# Windowed Streaming Analysis with Apache Spark Streaming

## Author Information
* Author: Jacqueline Yu
* GitHub: jacyu99
* UMD email: jyu12316@umd.edu

## Description
This project uses Python within a notebook environment to orchestrate time-based aggregations, leveraging tumbling windows for granular insights into the data. Due to the fact that publicly available streaming datasets are limited, this project will use a static csv file as the data source.

## Technologies
### Apache Spark:
* Spark is a robust, open-source distributed computing framework typically used for big data workloads.
* It utilizes in-memory caching and optimized query execution for fast analytic queries, making it suitable for a wide range of use cases.
* The in-memory cache significantly speeds up machine learning algorithms that repeatedly call a function for the same set of data.
* Spark natively supports Java, Scala, R, and Python and supports code reuse across multiple workloads such as batch processing, interactive queries, real-time analytics, machine learning, and graph processing.
* The efficiency and scalability of Spark ensures that the application can handle large data volumes and complexity without compromising performance.
* In the context of this project, Spark is utilized for windowed analysis to enable high-speed data processing and analysis on a large dataset.
* Time-based aggregations for the order volume of clothing items on Amazon.in are done for the following windows:
  * Monthly
  * Weekly
  * Daily
* Time based aggregations for the percentage of orders on Amazon.in that were expedited shipping as opposed to standard shipping are done for the following windows:
  * Monthly
  * Weekly

### Docker:
* Docker is a platform designed to streamlline the process of building, testing, and deploying applications efficiently.
* It achieves this by encapsulating software into standardized units known as containers. Containers contain all the necessary components for the software to function seamlessly, including libraries, system tools, code, and runtime environments.
* With Docker, it's possible to simplify the deployment and scaling of applications across various environments while ensuring the reliability of code execution.
* Docker allows the project to be run from anyone's machine without needing to install all the software and systems used.

### Jupyter:
* Jupyter is an open-source web application that allows users to create and share documents called "notebooks" containing code, visualizations, and text. It supports numerous programming languages, including Python, R, and Scala.
* Jupyter provides an interactive computing environment that allows code to be written and executed in a cell-based format. This functionality supports iterative development and experimentation.
* Jupyter notebooks also can display various types of output such as interactive visualizations and tables, making it an excellent choice for compiling and sharing research insights.
* Jupyter is commonly used in data science and machine learning workflows because of its seamless integration with widely used libraries such as NumPy, pandas, Matplotlib, and scikit-learn. These libraries facilitate data manipulation, analysis, and modeling within Jupyter.
* A jupyter notebook is used as the IDE for this project as it provides functionality to write code, use Markdown, and output visualizations all in the same place.

## Docker Implementation
* Using Docker for this project significantly simplies the development and deployment process.

* Working Directory:
  * The folder titled dev_environment within my repository contains all the files needed for the project. It includes:
    * spark_app.ipynb: Jupyter notebook where the code for the application is contained
    * Dockerfile: text document which contains all the steps needed to create a Docker image
    * docker-compose.yml: file used to define and run multi-container Docker applications
    * amazon_report.csv: file containing the data
* Dockerfile Structure:
  * Uses a FROM instruction to specify jupyter/pyspark-notebook:latest as the base image. This image is preconfigured for Pyspark and simplifies the Pyspark installation process.
  * Sets the working directory to /app
  * Uses a COPY instruction to copy the contents of the current directory into the /app directory
  * Installs additional Python packages
  * Uses a EXPOSE instruction to expose port 8888, which is the port Jupyter Notebook runs on
  * Uses a CMD instruction to start a Jupyter Notebook inside the container
* docker-compose.yml Structure:
  * Specifies version 3 as the Docker Compose syntax version
  * Specifies spark-app as the service to be run
  * Specifies that the service should be built using the Dockerfile located in the current directory through the use of '.'
  * Maps port 8888 on the host machine to port 8888 in the container
  * Mounts the current directory as a volume inside the container at /app
    * Enables sharing of files between the host and the container
    * Ensures any changes made to files in the current directory are reflected inside the container
* To build the Docker Image:
  * Run command: docker build -t temp-spark .
  * The image is tagged with name 'temp-spark' and is built from a Dockerfile in the current directory
* To run the Docker Containers
  * Run command: docker-compose up
  * Creates a container that will run Jupyter Notebook and Spark
* To launch the Jupyter Notebook
  * Paste in the url provided by the command line interface
  * It will look similar to http://127.0.0.1:8888/tree?token=<string_of_num_and_letters>
* To stop and remove the Docker Container
  * Run command: docker-compose down

## Project Objective
The dataset used for this project contains sales made on Amazon.in for the time period 3/31/22-6/29/22. The product category column contains only clothing items such as Set, Kurta, Western Top, etc. It is known that people will buy new clothes in preparation for holidays and festivals. As the project guidelines involve leveraging tumbling windows to provide insights into the data, my research questions are as follows:
* Does order volume increase before major holidays/festivals?
* Does the percentage of orders which have expedited shipping instead of standard shipping increase before major holidays/festivals?

### Major Holidays/Festivals Which Fall Within the Window
* April
  * Ram Navami: April 10 2022
  * Mahavir Jayanti: April 14 2022
* May
  * Eid-Ul-Fitr: May 2-3 2022
  * Buddha Purnima: May 16 2022

Monthly, weekly, and daily time-based aggregations were done for order volume on all the data available. Visualizations were created using Matplotlib to analyze the results of the aggregated order volume.

### Monthly Order Volume
![image](https://github.com/kaizen-ai/kaizenflow/assets/158385289/f216718d-d11c-4735-9075-293e334cff06)


### Weekly Order Volume
![image](https://github.com/kaizen-ai/kaizenflow/assets/158385289/6c5ef258-0991-4304-a051-c93379602625)


### Daily Order Volume
![image](https://github.com/kaizen-ai/kaizenflow/assets/158385289/bd906d45-b95a-454c-a712-a5e8cc05cd75)


Monthly and weekly time-based aggregations were done for percentage of expedited shipping on all the data available. Visualization were created using Matplotlib to analyze the results of the percent expedited shipping.

### Monthly Percentage of Expedited Orders
![image](https://github.com/kaizen-ai/kaizenflow/assets/158385289/395e2fa5-f950-4ead-a544-54d09f64e410)


### Weekly Percentage of Expedited Orders
![image](https://github.com/kaizen-ai/kaizenflow/assets/158385289/0ba4a06e-62b0-486d-b90e-df244ff00f82)

## Drawing Conclusions from Visualizations
* Days leading up to April 10-14, 2022
  * The daily order volume plot shows the order volume is steadily increasing leading up to Ram Navami and Mahavir Jayant.
    * This trend is within our expectations, because people will buy new clothes in preparation for upcoming events.
  * The weekly percentage of expedited orders plot shows that the percentage of expedited orders is decreasing leading up to the holidays.
    * This trend is contrary to our expectations, because we would expect people to want their clothing orders ASAP in preparation for upcoming events.
* Days leading up to May 2-3, 2022
  * The daily order volume plot shows the order volume spiking to its maximum (in the observation window) right before Eid-Ul-Fitr.
    * This trend is within our expectations
  * The weekly percentage of expedited orders plot shows that the percentage of expedited orders spikes right before this holiday.
    * This trend is within expectations.
* Days leading up to May 16, 2022
  * The daily order volume plot shows the order volume is steadily decreasing before Buddha Purnima.
    * This trend is contrary to our expectations.
  * The weekly percentage of expedited orders plot shows that the percentage of expedited orders is decreasing before this holiday
    * This trend is again contrary to our expectations.
   
 ## Closing Conclusions
 This project utilizes Python within a notebook environment to conduct time-based aggregations for insights into the data. It leveraged Apache Spark, Docker, and Jupyter Notebook to provide a robust framework for data analysis and visualizations. Spark's scalability and efficiency allowed for high-speed processing and Docker simplified the deployment process, ensuring portability across differerent environments. Jupyter notebook served as the interactive IDE and facilitated writing code, documentation via markdown, and creating visualizations. Through the analysis of order volumes and shipping methods before major holidays and festivals, the project makes meaningful conclusions regarding consumer behavior patterns. This process can be scaled up to potentially inform marketing strategies and decisions in the retail industry. 
