# HBase Data Modeling and Querying

- Dakeun Park
- 120462429
- GitHub: dan7kp
- UMD email: dpark37@umd.edu
- Video Demonstration: https://youtu.be/zmbbcPWyPqU

## Description
The project focuses on using the HBase database in a containerized environment with Docker. Jupyter Notebook will be used to demonstrate querying sample data and exploring data modeling with HBase, including denormalization and column family design.

## Technology

### HBase
- HBase is a columnar, NoSQL database where data is stored in columns rather than rows, unlike relational databases.

- A distinctive characteristic of a columnar database is its similarities with both key-value and relational databases:
	- Keys are used to query values similar to key-value stores.
	- Values are grouped into zero or more columns akin to relational stores.

- The advantages of a columnar store include excellent horizontal scalability, the ability to manage sparse tables without extra storage costs, and the inexpensive addition of columns.

- The disadvantages involve the need to design schemas based on anticipated query patterns and the absence of native joins, which requires applications to handle joins themselves.

- In the CAP Taxonomy, the columnar store functions as a CP (Consistent, Partition-Tolerant) system, facing challenges with availability while maintaining data consistency across partitioned nodes.

- Python scripts will be utilized to perform CRUD (Create, Read, Update, Delete) operations on the HBase columnar store.

- The demonstration will show how the columnar store may be modeled using the column family approach and denormalization in a NoSQL database context

*source: DATA605 5.1-NoSQL lecture*

### Docker
- Containerization technique that develops and runs individual applications in each container.

- Fast and portable.

- Does not require a full operating system like virtual machines, which reduces OS licensing costs, including overhead from OS patching and maintenance.

- All containers run on a single host for simplified maintenance.
- The cons include high CPU overhead and a variety of toolchains to learn and master.

- Docker containers and images set up the environment needed to run the required applications, in this case, Jupyter Notebook and HBase database, improving usability and portability.

*source: DATA605 3-Docker DevOps lecture*

## Implementing Docker

- **Project files:**
	- <mark>docker-compose.yml</mark>: Composes the two services, jupyter notebook and HBase with network and volume setup for the containers.

	- <mark>Dockerfile_hbase</mark>: Instruction for building a docker hbase image.

	- <mark>Dockerfile_notebook</mark>: Instruction for building a docker jupyter notebook image.

	- <mark>hbase.ipynb</mark>: Query and Modeling Interaction with HBase using jupyter notebook.

	- <mark>config</mark>: Credit goes to dajobe/hbase image. Had trouble with persistent data configuration using the container when pulling the image. Decided to clone the required files from git for building HBase.
		- hbase-site.xml
		- zoo.cfg
		- hbase-server: configurates the environment and starts HBase.

- **Dockerfile_notebook content:**
	- It starts with quay.io/jupyter/base-notebook as the base image, which includes Jupyter Notebook and a minimal Conda installation. This choice simplifies setup and ensures that Jupyter and Conda are ready to use.

	- The Dockerfile switches to the root user to perform installations that require administrative privileges. This is necessary for steps that go beyond the permissions of the default jovyan user.

	- It installs the happybase package using Conda. This package is specifically for interacting with Apache HBase. The installation commands are run quietly and confirmations are auto-approved for efficiency. Post-installation, it cleans up Conda caches to reduce the image size.

	- The Dockerfile copies the current directory (presumably containing notebook files and other necessary project files) into /home/jovyan/work in the container. This makes these files available within the Jupyter environment.
	- Sets the working directory to the specified path.

	- It exposes port 8888, which is the standard port for Jupyter Notebook servers. This is a documentation practice that indicates which port the container is expected to listen on.

	- Changes the ownership of the files, as the Jupyter Notebook is usually run by the jovyan user



- **Dockerfile_hbase content:**

	- The Dockerfile starts by specifying openjdk:8-jdk as the base image, which provides the Java 8 development kit necessary for running Java applications like HBase.

	- It labels the Docker image with the maintainer's contact information (dave@dajobe.org), which is useful for identification and support. Also to give credit to the maintainer.

	- Sets environment variables to configure the HBase installation.

	- Sets the working directory to the HBase home directory (HBASE_HOME).

	- Sets the working directory to the path specified.

	- Install dependencies and HBase.

	- Copies HBase configuration files (hbase-site.xml and zoo.cfg) into the container's HBase configuration directory. 

	- Copies a custom script (hbase-server) to start the HBase server into the container

	- Makes the hbase-server script executable, which is necessary for starting the HBase server.

	- Defines the command to start the HBase server using the hbase-server script when the container is run.



- **docker-compose.yml content:**

	 - Configuration is a Docker Compose file that orchestrates two services, hbase and notebook, facilitating their deployment and interaction within a Docker-managed network environment.

	 - HBase Service:

		- Specifies the directory (.) and Dockerfile (Dockerfile_hbase) to build the HBase Docker image

		- Defines the Docker image name as hbase-image:latest and sets the container name to hbase-docker.

		-  Assigns hbase-docker as the hostname within the network.

		- Ports:

			- 2181: ZooKeeper, used for managing the distributed configuration and providing distributed synchronization.

			- 8080: HBase REST API, allowing HTTP-based interactions with HBase.

			- 8085: HBase REST Web UI, which provides a web interface to the REST API.

			- 9090: HBase Thrift API, offering a service for programming languages to interact with HBase.

			- 9095: Thrift Web UI, a user interface for the Thrift API.

			- 16010: Master UI, the web UI for HBase's master server.

		- Mounts a named volume (hbase-data) at /data in the container for persistent data storage.

		- Connects the container to a custom network named app-network.

		- Uses unless-stopped, meaning the container will restart if it exits for any reason unless it has been manually stopped.

	 - Notebook Service:

	 	- Specifies the local directory as the context for building the Docker image using a Dockerfile. This allows for the customization of the notebook environment.

		- Uses the current directory (.) and a specific Dockerfile (Dockerfile_notebook) to build the Jupyter Notebook image.

		- Sets the image as notebook-image:latest and names the container notebook-server.

		- Runs the container as root (0:0), which is often necessary for certain administrative permissions within the container.

		- Exposes port 8888, commonly used for Jupyter Notebook servers.

		- Mounts the current directory to /home/jovyan/work in the container, providing access to necessary files within the notebook server.

		- Sets HBASE_HOST to hbase-docker, configuring the notebook server to connect to the HBase service using the internal network hostname.

		- Specifies that it depends on the hbase service, ensuring that HBase is running before the notebook server starts.

		- Also connected to app-network, enabling direct communication with the HBase service.

		- Overrides the default command to start the Jupyter Notebook server without requiring a token or password for access.

	 - Networks:

	 	-  Configured with a bridge driver, creating a private internal network for the services to communicate. This isolates them from other network traffic, enhancing security and performance.

	 - Volumes:

		- hbase-data: Utilizes a local driver for storing HBase data persistently.



### Using the Docker Image:

- <mark> docker compose up --build </mark> Command executes the compose file and build necessary image using the configuration in Dockerfile specified. Should be exectued only once for building the images.

- <mark> docker compose up </mark> To start/ compose the containers again.

- Once the containers are running, access the Jupyter Notebook <mark> http://localhost:8888 </mark> in the web browser.  Open hbase.ipynb file.

- <mark> Ctrl + C </mark> Command to stop the running containers in the terminal.

- <mark> docker compose down </mark> To terminate and remove containers.


## Python Script

- Use the URL <mark>http://localhost:8888</mark> to access the Jupyter Notebook interface. Once there, navigate to find the "hbase.ipynb" file.

- We will use the Python environment configured in the notebook to interact with HBase.

- Interaction with HBase is facilitated by the Happybase Python library. The Docker Compose setup has already installed this package, so you simply need to import Happybase in the notebook.

- The connection to HBase is made using the Thrift API on its exposed port, 9090, which was specified in the Docker Compose file.

- For precise implementation details, refer to the "hbase.ipynb" notebook. This document contains a step-by-step guide on how to execute operations using Happybase.

- Video demontration availabe at <mark>https://youtu.be/zmbbcPWyPqU</mark>



**Designing the schema**

Creating a database for a simple bookstore. We need tables for Books and Authors.

- Books Table

	- Row Key: ISBN (International Standard Book Number)

	- Column Families:
		- details: General information about the book.
			- details: title: The title of the book.
			- details: author: Author ID (link to Authors table).
		- stock: Information about book availability.
			- stock: quantity: Number of copies available.

- Authors Table
	- Row Key: Author ID
	- Column Families:
		- info: Information about the author.
			- info: name: Author name.
			- info: birthdate: Author birth date.

**Creating Tables in HBase**

- Once connection is made, <mark> .tables() </mark> function gets existing tables.

- <mark> .create_table() </mark> function creates table.

**Populating Tables with Sample Data**

- <mark> .put() </mark> function creates data.

**Implementing Queries**

- <mark> .row() </mark> function gets a row of data.

- <mark> .scan() </mark>function gets multiple row from range of key values.

- <mark> .scan(filter) </mark> filter argument can be given to get data based on condition.

**Class in python**

In python, we can implement CRUD operations using class.

- Initialization:

	- The init method establishes a connection to the HBase server using the provided host and port.

- Create or Update:
	- The create_or_update method allows inserting or updating data in the specified table and row key.

- Read:
	- The read method fetches data for a specific row key from the given table, returning the data in a readable format or a message if no data is found.

- Delete:
	- The delete method removes a row from the specified table.

- Scan Table:
	- The scan_table method scans for rows within an optional key range and can apply a filter to the scan. It's used for broad queries across your data.

- Scan Filtered Table:
	- The scan_filtered_table method adds specific column filters to the scanning process, which is useful for more targeted queries based on specific column values.

- Close Connection:
	- The close_connection method properly closes the connection to the HBase server.

### Experiment with Data Modeling

- Data modeling in HBase can significantly affect performance. It's crucial to decide whether to normalize data, which may require multiple cross-table queries, or to denormalize it, which increases storage but may reduce the number of queries.

- **Denormalization approach:**
	- A new table named "denormalized" will be created to demonstrate this approach.
- Two column families:
	- book_details: Stores information related to books, such as title and quantity.
	- author_details: Stores information related to authors, such as name and birthdate.

- As observed in the denormalized table, it is straightforward to add additional columns to either the book_details or author_details column families for attributes such as book price, genre, or author address and phone number.

- Utilizing all this information in one table can lead to data redundancy. Therefore, the choice of how to model the database should be based on the specific needs of different stakeholders.

## Conclusion

HBase, as a columnar database, has its pros and cons as a NoSQL system and possesses the distinctive property of sharing similarities with both key-value and relational databases. This feature is particularly useful in applications involving the storage of web pages, where each row represents one website, each column family represents a webpage, and different columns represent the attributes of the webpage. With its distinctive features, HBase is most useful when applied correctly, but it is not a universally optimal choice. This project demonstrated the portability of a Docker container and how it can be used in developing, testing, and deploying environments, showcasing how simple the process can be. It also shows how HBase can be utilized as a simple database and provides a glimpse of how denormalization and column family design can be implemented as opposed to a relational database. The project can serve as a foundation to explore more complex data modeling involving a columnar database and offers a good understanding of how NoSQL differs from standard SQL.


