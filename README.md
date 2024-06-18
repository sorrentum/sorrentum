605 Final Project - Data Analysis with RethinkDB and Python
Xueyan Geng
May 10, 2024

### Descirption
Perform basic data analysis using RethinkDB and Python where data stored in a RethinkDB database is analyzed and visualized. Develop Python scripts to retrieve data from RethinkDB, perform analysis using Python libraries (e.g., pandas), and visualize the results (e.g., matplotlib). Utilize the rethinkdb library to interact with RethinkDB, showcasing basic data analysis techniques.

The link of video demonstration: https://drive.google.com/file/d/16bcDQW5CC89N0vpTVspaNYojWK0QVDTe/view?usp=drive_link

### Technology used
##### Rethinkdb:
​	RethinkDB is an open source distributed document-based database designed forreal-time applications. It stores data in the form of JSON documents , providing developers with real-time update capabilities , so that applications can immediately access the data  changes . This real-time is achieved through RethinkDB's built-in "change subscription"  (change feeds) feature , developers can monitor the query result set changes and immediately respond . In addition, RethinkDB has a distributed architecture with built-in replication and sharding support, so it can handle large-scale data and high-load applications. Its JSON data model is so flexible that developers can easily store and retrieve complex data structures without having to map to tables and columns in a relational database. Through the SQL-like query language ReQL , RethinkDB provides a rich set of operations , including filtering , mapping , aggregation , joins , etc. , as well as special query operations for real-time updates . As an open source project, RethinkDB has active community support and continuous development, and developers are free to contribute code, report problems and make suggestions.
​	At its core, RethinkDB allows developers to store, query and manipulate JSON documents in a distributed environment. This means that developers can easily store and retrieve complex data structures without having to worry about table and column constraints. This flexibility makes RethinkDB better suited for working with unstructured or semi-structured data, as well as applications with more frequently changing data schema requirements. Second, RethinkDB has the ability to update in real-time, a feature lacking in many traditional databases. Through the "change subscription" feature, RethinkDB allows applications to get immediate access to changes in data without having to poll the database on a regular basis. This makes RethinkDB ideal for building real-time applications such as real-time analytics, collaborative applications, and instant messaging platforms.RethinkDB's query language, ReQL (RethinkDB Query Language), is highly expressive and intuitive, providing a powerful set of operators for filtering, transforming, and aggregating data. In addition, RethinkDB natively supports changefeeds, which notify database changes in real-time, making it easy to build reactive applications without complex event processing. Unlike traditional databases that focus on static data, RethinkDB was built from the ground up to handle dynamic and ever-changing data streams, making it particularly well-suited for applications that require real-time updates.

###### Advantages:
1. Real-Time Performance: RethinkDB provides the ability to update and query in real-time, making it ideal for real-time applications such as real-time analytics and collaborative applications.
2. Ease of Use: It has an easy-to-use API and query language that allows developers to get started quickly, and supports data storage in JSON format.
3. Distributed: RethinkDB is a distributed database that can easily scale to multiple nodes for high availability and horizontal scaling.
4. Automatic Data Replication: Data is automatically replicated in the cluster, ensuring data reliability and high availability.
5. Real-time monitoring and management: RethinkDB provides real-time monitoring and management tools that allow administrators to easily monitor the health of the database cluster and perform necessary management operations.
###### Disadvantages:
1. Ecosystem: Compared to some of the more established databases, such as MongoDB or PostgreSQL, RethinkDB has a relatively small ecosystem and may lack some of the established third-party tools and libraries.
2. Community Support: While RethinkDB has an active development team, it may have relatively little community support compared to some of the more widely used databases, leading to potential challenges in resolving issues and obtaining support.
3. Maturity: While RethinkDB performs well in some areas, it may lack some of the features and optimizations of some mature databases in others, and therefore may not be as good as other options in some specific usage scenarios.
4. Performance: Although RethinkDB offers real-time performance, there may be performance limitations in some scenarios, especially when working with large amounts of data or complex queries.

​	In class we learned that various types of databases have different characteristics and scenarios of application. Common database types include relational databases, NoSQL databases, and NewSQL databases. The choice of database depends on the needs and constraints of the application and requires a combination of factors such as data model, consistency needs, performance and scalability needs, cost, and future expansion and changes in requirements.

##### Docker

​	Docker is an open source platform for developing, deploying and running applications. It allows developers to package an application and all its dependencies into a separate unit called a container. Each container contains everything the application needs: code, runtime, libraries, environment variables, and configuration files. This allows applications to run the same way in any environment, whether it's a developer's laptop, a test server, or a cloud server in a production environment.Docker leverages operating system-level virtualization technologies, such as Linux containers (LXC), as well as kernel-specific features, such as cgroups and namespaces, to provide a lightweight, portable, and scalable containerized solutions. By using Docker, developers can build, test, and deploy applications faster while also utilizing infrastructure resources more efficiently.

###### Advantages:

1. Lightweight and Fast Deployment: Docker containers are very lightweight and fast to launch, allowing applications to be deployed in seconds.
2. Cross-platform: Docker containers can run on any operating system that supports the Docker engine without worrying about environment differences.
3. Resource isolation: Each Docker container has its own filesystem, network and process space, which effectively isolates applications and their dependencies to avoid conflicts and interference.
4. Scalability: Docker containers can quickly scale up and down on demand, allowing applications to better cope with traffic spikes and fluctuations.
5. Version control and replication: Docker images can be versioned and shared, allowing developers to easily replicate, deploy and manage different versions of an application.

###### Disadvantages:

1. Security: While Docker containers provide a degree of isolation, there are still security risks when misconfigured or using insecure images.
2. Performance overhead: In some cases, Docker containers may introduce additional performance overhead, especially in large-scale deployments and high-density environments.
3. Learning curve: For novices, learning the concepts and workings of Docker can take some time and effort.
4. Persistent storage: Docker containers do not save persistent data by default and require additional configuration and management to achieve persistent storage of data.



### Docker Implementation
Based on the nature of this project, the choice was made on the docker side to pull directly from an existing public sight rather than build it. The packages or services used in this project are all included in the existing public image, using the public image can save the time of building the image, easily get the latest software version and security patches, which is more convenient and faster.

- **Pull Images**
1. Download the ```notebook``` file. 
2. Search Docker Hub or other image repositories for images that fit your project and pull them to the folder directory.
jupyter notebook:
```docker pull jupyter/scipy-notebook:latest ```
rethinkdb:
```docker pull rethinkdb```
3. Use ```docker images``` to check if the pull is successful.

- **Run Docker Containers**
1. Create containers on two separate images.
   jupyter notebook:
   ```docker run -itd --name <your_jupyter_container_name> --restart=always -v <your_file_address>:/home/jovyan -p 8888:8888 jupyter/scipy-notebook```
    - Run a container named ```<your_jupyter_container_name>``` in background mode, using the Jupyter Notebook image.
    - Mounting the local directory ```<your_file_address>``` to the ```/home/jovyan``` directory inside the container. The purpose of this is to share a file or directory in the host with a file or directory in the container so that the Jupyter notebook in the container can access the file in the host.
    - Mapping the container's ```port 8888``` to the host's ```port 8888```. The Jupyter notebook service usually runs on port 8888. Doing so allows us to access the Jupyter notebook service through a browser by accessing port 8888 on the host machine.
    - The container is automatically restarted at startup and the Jupyter notebook service can be accessed through a browser.

    rethinkdb:
   ```docker run -d --name <your_rethinkdb_container_name> -p 8080:8080 -p 28015:28015 -p 29015:29015 rethinkdb```
    - Run a RethinkDB container named ```<your_jupyter_container_name>``` in background mode.
    - Maps the container's ```ports 8080, 28015, and 29015``` to the corresponding ports on the host machine for accessing RethinkDB's web console and communicating with client applications through a browser.
2. Use ```docker ps``` to check if the containers are created successfully.

- **Access the project**
1. Navigate to `http://localhost:8888` in a web browser to access the Jupyter Notebook interface.
Navigate to ```http://localhost:8080``` in a web browser to access the RethinkDB interface.
2. Interact with the notebook file (python code.ipynb) to execute code.
    - Use ```docker inspect <your_rethinkdb_container_name>``` to get your IPAddress and fill it to host in the notebook file.

- **End the Containers**

  Use `docker stop <your_container_name>` to end a container in progress.

### Python Script Overvies

This project performs data preprocessing, data analysis, data visualization and modeling on a set of movie dataset with more than 5000 rows of data and 28 features.
The script is divided into four main parts：
1. **Connection to rethinkdb**
- Use `r.connect(host='172.17.0.3', port=28015, db='test')` to make a connection to the RethinkDB database through RethinkDB's Python driver (usually the rethinkdb module). Specify the host address and port number of the RethinkDB server, where `172.17.0.3` is the IP address of the container, which is the default IP address when running the RethinkDB container in Docker, and `28015` is the default client connection port for RethinkDB.
- Import the dataset `file movie.csv` from the same directory into the database.
- Read the data in the table from the Rethink database and store the data in a Pandas DataFrame.
2. **Data preprocessing**
- Remove features that are not relevant to subsequent analysis and modeling, such as movie links, etc.
- Fill missing values with np.nan.
- Adjust features to the appropriate data type for subsequent analysis.
- Check the features and remove outliers.
- Compute statistical metrics.

3. **Data visualization**
- Groups of two or two features were used for data visualization to see trends in their interactions.

- The python packages used: matplotlib, plotly, wordcloud, seaborn, numpy, etc.

- Visualization forms: scatterplot, bar chart, pie chart, line graph, word cloud, 3D chart, etc.

  ![](https://drive.google.com/uc?id=1rRwuYPFOilsfhIToh7pmYmeBJw6umY9J 'Average Gross Over Years')

  ![p2](https://drive.google.com/uc?id=1c-1W-idkqSeluqKoX1OzuYCqxGp5BKUl 'Gross Earning VS IMDB Score')

  ![p3](https://drive.google.com/uc?id=1YpyC8TPoBrfjhTcow89xxHLmyIHv1Zz7 'Top 10 Direcotors by Average IMDB Score')

  ![p4](https://drive.google.com/uc?id=1jamJJ449Ombm9wB5jOHjXpJ92QV865UQ 'Wordcloud of Movies with IDBM over 8')


4. **Data modeling**

According to the results of the previous part of the analysis, the IMDB score of the movie is significantly related to most of the features. So it is possible to predict the IMDB score of the movie based on some of the features, in this section we tried various machine learning models to make predictions and compare their effectiveness.

- Selected features: gross, budget, duration, num_user_for_reviews, num_critic_for_reviews, title_year, One-Hot encoded content_rating.

- Machine learning algorithms: Linear Regression, Random Forest, Support Vertor Machine, Decision Tree, Neural Network

- Evaluation method: Root Mean Squared Error (RMSE)

- Result: Collectively, Random Forest performs best on this dataset.

  |  LR   |  RF   |  SVM  |  DT  |  NN   |
  | :---: | :---: | :---: | :--: | :---: |
  | 0.933 | 0.845 | 0.877 | 1.17 | 0.918 |



### Database Schema

The database follows a simple JSON structure where each movie is represented as a dictionary. The schema includes 28 features such as movie title, year, budget, gross, country, language, duration, etc. 

```
{
'actor_1_facebook_likes': '8000', 
'actor_1_name': 'Julia Roberts', 
'actor_2_facebook_likes': '698', 
'actor_2_name': "Jack O'Connell", 
'actor_3_facebook_likes': '638', 
'actor_3_name': 'Chris Bauer', 
'aspect_ratio': '2.35', 
'budget': '27000000', 
'cast_total_facebook_likes': '10894', 
'color': 'Color', 
'content_rating': 'R', 
'country': 'USA', 
'director_facebook_likes': '0', 
'director_name': 'Jodie Foster', 
'duration': '98', 
'facenumber_in_poster': '1', 
'genres': 'Crime|Drama|Thriller', 
'gross': '41008532', 
'id': '004788ac-a7b2-4336-847a-a296cdf02f37', 
'imdb_score': '6.7', 
'language': 'English', 
'movie_facebook_likes': '0', 
'movie_imdb_link': 'http://www.imdb.com/title/tt2241351/?ref_=fn_tt_tt_1', 
'movie_title': 'Money Monster\xa0', 
'num_critic_for_reviews': '268', 
'num_user_for_reviews': '103', 
'num_voted_users': '19611', 
'plot_keywords': 'death|hostage|money|shot in the chest|shot in the heart', 
'title_year': '2016'
}
```



### Conlusion

This data analysis project aims to explore movie data and extract valuable insights as well as predictions from it. First, we used the RethinkDB driver in Python to connect to the RethinkDB database to store and retrieve our movie dataset of interest. We load the movie data into a Pandas DataFrame by executing a query and use Pandas functions to clean the data, handle missing values, and compute statistical metrics such as average ratings, most popular movie genres, and so on. Next, data visualization tools such as Matplotlib are used to generate charts and graphs to provide a more intuitive view of the distribution and trends in the data. By creating visual charts such as histograms, scatter plots, or box-and-line plots, we can better understand the characteristics and relationships of movie data. Finally, various machine learning algorithms are constructed and their predictions are evaluated based on the results of the analysis. Overall, a movie data analysis project using Python and RethinkDB can help us gain a deeper understanding of the movie market, identify business opportunities, and make effective business decisions.
