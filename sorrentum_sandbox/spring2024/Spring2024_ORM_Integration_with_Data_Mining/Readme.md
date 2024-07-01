# ORM Integration with Data Mining
## Author info
* Author : Muyan Cheng
* GitHub account : MuyanCheng
* UMD email : mycheng9@umd.edu
* UID : 120429798
* Video link: https://drive.google.com/file/d/1c5HWmsrFqcGLMJdIPAoGWnP_xoq40-AV/view?usp=drive_link
## Description
Analyze Lending Club's data on people who received loans in 2018. Use SQLAlchemy to acquire data from the relational database SQLite, transform the data into a Pandas DataFrame for analysis, perform data exploration tasks, and visualize the results using the matplotlib/seaborn library, as well as constructing three predictive models for default risk and evaluating their performance. This project demonstrates the integration of ORM with data mining and visualization techniques.
## Technologies
### Jupyter
* Introduction:
    - Jupyter Notebook is an open source web application that provides an interactive computing environment with a wide range of applications in the field of data analysis.
    - Jupyter supports Python programming while enabling seamless integration of code, visualization, and explanatory text.
    - Jupyter Notebook serves as a versatile platform for exploring, manipulating, and visualizing complex data sets. It not only performs various analyses on the data, but also visualizes it to reveal patterns, trends, and correlations in the data.

* Features:
    - Unlike traditional statistical analysis software, Jupyter Notebook requires very little configuration, making it very suitable for individual researchers.
    - It has support for a wide range of programming languages, which allows users to leverage their existing skills and libraries to promote productivity and innovation.
    - The notebook format makes it possible to not only run code, but also to add text descriptions and introductions, enabling users to document the use of the code, analyze the results, and share their findings with others.

* Pros and Cons:
    - Pros:
        - Using Jupyter Notebook is economical as it is an open source project and can be used for free.
        - Due to the lightweight and portable nature of Jupyter Notebook, it can be deployed in a variety of environments so that users can choose the most affordable deployment option as needed without having to invest a lot of money.
        - Jupyter Notebook is easy to use as it does not require complex configuration.
        - Jupyter Notebook supports interactive computing.
    - Cons:
        - Jupyter's flexibility can sometimes lead to challenges in managing code complexity and version control.
        - Without proper rules, notebooks can become disorganized and difficult to maintain over time.
        - Jupyter may not be the most effective tool for large-scale data processing or production-level deployments.

### SQLite
* Introduction:
    - SQLite is a lightweight relational database management system that plays an important role in organizing and querying small data. 
    - Unlike client-server database engines, SQLite operates as a standalone, serverless database and is well suited for embedded systems, mobile applications, and on-the-fly data analysis tasks.

* Features:
    - SQLite's unique strengths are its simplicity, portability, and zero-configuration setup.
    - Unlike heavyweight database systems such as MySQL or PostgreSQL, SQLite requires no installation or administration, making it suitable for users with varying skill levels.
    - SQLite's single-file database format facilitates seamless data exchange and collaboration, eliminating the need for complex server setups or network configurations.

* Pros and Cons:
    - Pros:
        - SQLite does not require a separate server process or operating system (serverless).
        - SQLite does not require configuration, which means there is no installation or administration required.
        - A complete SQLite database is stored in a single cross-platform disk file.
        - SQLite is very small and lightweight, less than 400KiB when fully configured and less than 250KiB when configured with optional features omitted.
        - SQLite supports the functionality of the SQL query language.

    - Cons:
        - The design of SQLite limits its concurrency performance. Since it is a single-user database engine, only one process can access the database at a time. Therefore, performance bottlenecks may occur in highly concurrent environments. 
        - SQLite's scalability is limited when the amount of data increases or the application needs to scale horizontally.
* Relevance to Class: 
    - The class was introduced to relational databases, and SQLite is a type of relational database.


### Docker
* Introduction:
    - Docker is an open-source containerization platform that packages applications and their dependencies into a separate, lightweight container through containerization technology. 
    - These containers can run in any Docker-enabled environment, be it a developer's laptop, a server in a data center, or a virtual machine instance in the cloud.

* Features:
    - Docker is unique because of its lightweight, portability, and scalability.
    - Compared to traditional virtualization technologies, Docker containers are more resource-efficient, start up faster, and are able to maintain consistent operational behavior across different environments.
    - Docker's image and container model makes it easier and more flexible to deploy, scale, and manage applications without focusing on the underlying hardware or operating system.

* Pros and Cons:
    - Pros:
        - The main benefits of using Docker to build containerized applications include its portability, repeatability, and resource utilization.
        - By packaging an application and its dependencies into a separate container, developers can avoid inconsistent environment configurations and reduce problems due to conflicting dependencies.
        - Docker's image and container model provides a lightweight virtualization solution that allows for rapid deployment and scaling of applications across different deployment environments.
    - Cons:
        - While Docker simplifies the deployment and management of applications, learning and mastering Docker's concepts and toolsets can take some learning time for beginners. 
        - As the number of containers increases, container management and monitoring becomes more complex.


* Relevance to Class:
    - We learned in class about the principles and applications of virtualization technologies, including virtual machines and containers. Docker provides us with a lighter-weight, more flexible virtualization solution as a containerization platform.

## Docker System Design
* The Docker system designed for this project implements a combination of Jupyter and SQlite services to read data across containers using shared volumes, and to analyze and mine the data.

* Let's take a deeper look at the design structure of this Docker system:

* Project Setup:

    Start by organizing the project files in a directory structure. The main files include:
    - `Dockerfile`: Contains instructions for building a Docker image for the Jupyter service.
    - `Docker-compose.yaml`: Defines services, network ports, and shared volumes for Docker containers.
    - `notebooks` folder: holds the Jupyter NoteBook files `Lending_Club_Data_Analysis_and_Mining.ipynb`used for reading and analyzing data
    - `data` folder: holds the original csv data file called `loan_data.csv` and the SQLite database file called `mydatabase.db`.

* `Dockerfile` Configuration:

    To start setting up Dockerfile, follow these steps:
    - Use the latest version of the official Python image as your base image.
    - Install Jupyter Notebook and JupyterLab.
    - Install the required Python libraries, including numpy, pandas, matplotlib, seaborn, wordcloud, plotly, scikit-learn, lightgbm, and sqlalchemy.
    - Set the container's working directory to `/app`.
    - Expose port `8888` for the Jupyter Notebook server.
    - Install the IPython kernel for Python and name it `myenv`.
    - Specify that the default command when the container starts is to run JupyterLab, listen on all network interfaces, and allow the root user to log in.

* `Docker-compose.yml` configuration:

    Configure the docker-compose.yaml file to define the services required by the project:
    - Define two services: `jupyter` and `sqlite`.
    - Configure the `jupyter` service:
        - Build using the Dockerfile in the current directory.
        - Map the host's port `8888` to the container's port `8888`.
        - Maps `. /notebooks` and `. /data` directories to `/app/notebooks` and `/app/data` in the container.
        - Set the environment variable `DATABASE_URL` to `sqlite:///mydatabase.db` and enable JupyterLab.
    - Configure the `sqlite` service:
        - Use the Alpine Linux image.
        - Map the `. /data` directory to `/app/data` in the container.
        - Execute commands in the container to install SQLite and initialize a database file, `mydatabase.db`, and keep the container running.
    - Define the volumes: 
        - Two volumes are defined: `notebooks` and `data`.
* Data sharing between containers
    - Shared volumes are used to enable data sharing between containers.
    - Mount the `data` folder under both `jupyter` and `sqlite` services so that they can use the `data` folder for data sharing.
## Docker Implementation and System Operation
* Build Docker Compose:
    - Open the folder where the project is located using `cd`
    - Execute `docker-compose build` and invoke `Docker compose.yml` and `Dockerfile` to build the container, this builds the corresponding containers for Jupyter Notebook and SQLite as well as their shared volumes.

* Run Docker Compose:
    - Start the Docker container using `docker-compose up`.
    - Docker Compose will start the corresponding containers for Jupyter and SQLite.
    - Access SQLite server via Docker Desktop.
    - Access the Jupyter Notebook server using a web browser.

* Access SQLite server and build the database:
    - Go to the Container section of Docker Desktop to see the running containers, click into the `sqlite` service and go to the Exec section.
    - Use `sqlite3` to create and open a SQLite database file named `mydatabase.db` and enter SQLite command line interactive mode.
    - Use the `CREATE TABLE IF NOT EXISTS` statement to create a table named `loan_data`
    - Set `.mode csv` to set the SQLite input mode to CSV format for importing CSV files.
    - Use the `.import` command to import the CSV file named `loan_data.csv` into the table named `loan_data`.
![alt text](https://github.com/MuyanCheng/text/blob/main/%E5%9B%BE%E7%89%871.png?raw=true)

* Access Jupyter Notebook server:
    - Access the Jupyter Notebook interface by following the Jupyter Notebook URL provided in the docker compose run process displayed in the terminal. The access link is very similar to the one shown below, but the token will be different each time.
        ```
        jupyter_1  |         http://127.0.0.1:8888/lab?token=65aeffd4d8f638112dd11b415099b94916649f0bff8077d5
        ```
    - The container fetches the `.ipynb` file in the notebooks, which can be edited on the web side of Jupyter Notebook.
    - Write Python code in Jupyter Notebook to connect to SQLite database and perform data analysis and mining.
* Database Connection:
    - Using `SQLAlchemy` library to connect and manipulate SQLite databases in Jupyter Notebook
    - Use `create_engine` to create a SQLite database engine and specify the path `sqlite:////app/data/mydatabase.db` to the database file. 
    - The database engine is used to interact with the database and perform SQL queries and operations.

* Stop the Docker container:
    - To stop the container, press `Ctrl + C` in the terminal running `docker-compose up`.

## Database Schema
* I used loan data from people who received personal loans from Lending Club in 2018, retained basic lender information and loan information, and obtained a total of 426,257 instances and 17 features.
* I imported them into a SQLite database called `mydatabase.db`.
* The data schema of `mydatabase.db` is shown below. It can be seen that it contains a table called `loan_data` and contains 17 features:
    ```
    CREATE TABLE loan_data (
        addr_state TEXT,
        annual_inc FLOAT,
        application_type TEXT,
        emp_length TEXT,
        emp_title TEXT,
        fico_range_high INTEGER,
        fico_range_low INTEGER,
        grade TEXT,
        home_ownership TEXT,
        installment FLOAT,
        int_rate FLOAT,
        issue_d TEXT,
        loan_amnt FLOAT,
        loan_status TEXT,
        purpose TEXT,
        term TEXT,
        verification_status TEXT
    );
    ```

## Lending Club Data Analysis and Mining
I analyzed and mined Lending Club's loan data for a series of visualizations. In addition, I constructed three default prediction models based on Logistic Regression, Random Forest and Light-GBM algorithms. The specific data analysis and mining is shown below.
### Data Analysis
* Analysis of the loan status
    ![alt text](https://github.com/MuyanCheng/text/blob/main/1.png?raw=true)<br>
    According to the Loan Status Distribution plot, it can be seen that the Current status accounts for the most, and the Fully Paid status is much higher compared to the Default status, reaching about 9.8%, which shows that the repayment of those who have obtained loans is still relatively optimistic.
* Analysis of the distribution of loan amounts
    ![alt text](https://github.com/MuyanCheng/text/blob/main/2.png?raw=true)<br>
    It can be seen that the loan amounts are concentrated between 5,000 and 20,000, with a maximum ofIt can be seen that the percentage of loans with a term of 36 months reaches more than 70%, so the majority of the loans are 3 years. 40,000. Also, most of the loans are in multiples of 5,000. The highest number of loans were made in the amount of 10,000 dollars.
* Analysis of the distribution of loan terms
    ![alt text](https://github.com/MuyanCheng/text/blob/main/3.png?raw=true)<br>
    It can be seen that the percentage of loans with a term of 36 months reaches more than 70%, so the majority of the loans are 3 years.
* Analysis of the distribution of loan purposes
    ![alt text](https://github.com/MuyanCheng/text/blob/main/4.png?raw=true)<br>
    As can be seen from the graph, the percentage of loans with the purpose of debt_consolidation is more than 50% and the percentage of loans with the purpose of credit_card is more than 25%. It is evident that most of the loans are taken to deal with their debt problems and credit card repayment.
* Word cloud of job titles
    ![alt text](https://github.com/MuyanCheng/text/blob/main/5.png?raw=true)<br>
    According to the word cloud of occupational titles, the most frequent titles are Director, Supervisor and Registered Nurse, while Teacher and Project Manager are also very frequent.
* Analysis of the distribution of work length
    ![alt text](https://github.com/MuyanCheng/text/blob/main/6.png?raw=true)<br>

    According to the distribution chart of working hours, it can be seen that the number of people who have worked for more than 10 years reaches 35%. In addition, there is a large number of people who have worked for less than or equal to 3 years.
* Analysis of Lending Club grade
     ![alt text](https://github.com/MuyanCheng/text/blob/main/7.png?raw=true)<br>
    It can be seen that those who received loans had high Lending Club ratings, with the percentage of people with grades of A,B,and C combined exceeding 80%. And only 0.1% of those who received loans had a G rating. This suggests that Lending Club ratings are an important indicator of whether an applicant can get a loan.
* Analysis of annual income    
     ![alt text](https://github.com/MuyanCheng/text/blob/main/8.png?raw=true)<br>
     As it can be seen based on the annual income distribution graph, the majority of borrowers are concentrated in the income range of less than \$150,000. The largest number of them have incomes in the range of \$50,000 to \$100,000.
* Analysis of the distribution of verification status
     ![alt text](https://github.com/MuyanCheng/text/blob/main/9.png?raw=true)<br>
    As it can be seen, Source Verified and Verified together amount to almost 60%, meaning that more than half of the people who received loans had their information verified.
* Analysis of the distribution of home ownership
     ![alt text](https://github.com/MuyanCheng/text/blob/main/10.png?raw=true)<br>
    It can be seen that not many people own their own homes, and most of them rent or take out mortgages, which also shows that their financial situation is not particularly good, which is why they need to apply for a loan.
* Analysis of the distribution of interest rate
     ![alt text](https://github.com/MuyanCheng/text/blob/main/11.png?raw=true)<br>
    As can be seen, the interest rates are concentrated between 5% and 15%, with the highest rate exceeding 30%. The interest rates are relatively high.
* Analysis of the proportional distribution of annual installments and annual income
     ![alt text](https://github.com/MuyanCheng/text/blob/main/12.png?raw=true)<br>
    The distribution of installments as a percentage of annual income shows that the installment to annual income ratio is concentrated at less than 15%, which indicates that borrowers are able to repay their debts.
* Analysis of FICO Score Distribution
     ![alt text](https://github.com/MuyanCheng/text/blob/main/13.png?raw=true)<br>
    It can be seen that the average FICO score of the borrowers is basically above 670, which means that their credit is relatively good.
*  Analyzing the relationship between Interest Rate and FICO Mean
     ![alt text](https://github.com/MuyanCheng/text/blob/main/14.png?raw=true)<br>
    As can be seen from the figure, the interest rate and the average FICO score are negatively correlated and have a coefficient of -0.442, indicating that the interest rate on the loan that borrowers receive is correlated with their FICO credit score.
* Geographical distribution of the number of loans
     ![alt text](https://github.com/MuyanCheng/text/blob/main/newplot.png?raw=true)<br>
    It can be seen that California has the highest number of loans, plus Texas, Florida, and New York have a higher number of loans.
* Geographical distribution of average loan amount
     ![alt text](https://github.com/MuyanCheng/text/blob/main/newplot(1).png?raw=true)<br>
    It can be seen that the state of Alaska has the highest average loan amount. The average loan amount is also on the high side on the East and West coasts, which corresponds to the well-developed economies of these regions.
* Geographical distribution of average annual income
     ![alt text](https://github.com/MuyanCheng/text/blob/main/newplot(2).png?raw=true)<br>
    The figure shows that borrowers on the East and West Coasts have higher average annual incomes, further validating the higher economic levels in these areas.
* Geographical distribution of average FICO score
     ![alt text](https://github.com/MuyanCheng/text/blob/main/newplot(5).png?raw=true)<br>
    As shown in the figure, borrowers in the central U.S. have higher average FICO scores, especially in Wyoming, at 712.9.
* Geographical distribution of Default Rate
     ![alt text](https://github.com/MuyanCheng/text/blob/main/newplot(4).png?raw=true)<br>
    As shown in the graph, loan default rates are higher on the east and west coasts of the U.S. and also in states in the southern U.S., but the highest default rate is in South Dakota.

### Construction of Default Prediction Models
* Data preprocessing
    - Data cleaning
      - Because `Current` status does not indicate whether the borrower will default in the future so it needs to be removed. 
      - Filter out the loan data from the loan data whose status is not `Current` and save it in `data _processed` variable.
      - Create a new column called `label`, where `1` means the loan status is `Fully Paid` and `0` means any other status.
    - Select features
        - Select the feature columns to keep, including `addr_state`, `annual_inc`, `emp_length`, `grade`, `home_ownership`, `int_rate`, `loan_amnt`, `term`, `verification_status`, `fico_mean`, and `installation_annual_inc_ratio`.
    - Missing value processing
        - Clear lines containing missing values
    - Processing nominal features
      - Numerical coding of the `addr_state`, `emp_length`, `grade`, `home_ownership`, `term`, and `verification_status` columns converts categorical variables to numerical types.
    - Normalize the data
        - Use StandardScaler to normalize selected features so that the data has zero mean and unit variance.
* Model training and results
    - Three default prediction models, Logistic Regression, Random Forest and Light-GBM were trained using `sklearn` package and `lightgmb` package.   And output the prediction results of the models as follows:

        |  Algorithms   | Logistic Regression  |  Random Forest  |   Light-GBM |
        |  :----:  | :----:  | :----:  | :----:  |
        | Accuracy | 0.7168 |  0.7129    |   0.6480   |
        | F1 Score | 0.8238 |  0.8196   |  0.7192   |
        | AUC  | 0.7084 |  0.6984   |   0.7138  |
    
    - It can be seen that Logistic Regression performs well, outperforming the other two algorithms in both accuracy and F1 Score.



## Project Diagram
![alt text](https://github.com/MuyanCheng/text/blob/main/Project-structure.png?raw=true)



## Conclusion
This project successfully combined ORM (Object-Relational Mapping) technology with data mining to deeply analyze and mine LendingClub's data by utilizing tools such as Docker, Jupyter Notebook, and SQLite. Throughout the project, I achieved the following key objectives and outcomes:

- Technology integration and application: a stable and easy-to-deploy development environment was built through Docker containerization technology, while the interactive features of Jupyter Notebook were fully utilized for exploratory data analysis and model development. The SQLAlchemy library was used to realize the ORM operation on SQLite database, which improved the efficiency and flexibility of data access and processing.

- Data analysis and mining: through the interactive computing environment provided by Jupyter Notebook, I conducted extensive exploration of Lending Club's data. To better communicate the analysis results, I used various data visualization techniques, including pie charts, bar charts, heat maps, and so on. These visualizations not only provide an intuitive presentation of the data, but also help stakeholders better understand the analysis results and decision-making recommendations.

- Model construction: three default prediction models are established, and after model training and testing, models with certain prediction ability are obtained.

In summary, through the in-depth analysis of LendingClub data, I not only increased my understanding of borrowers' personal information and default status, but also provided a data foundation and guidance for building default prediction models.
