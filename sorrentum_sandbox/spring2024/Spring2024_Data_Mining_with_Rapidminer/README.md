# Data Mining With Rapidminer

## Author info

- Author: Lichen Zhang
- GitHub account: Xzluv
- UMD email: lzhang33@umd.edu
- Personal email: z478671360@gmail.com

## Description

Explore RapidMiner for data mining and analysis. Choose the Bank Market  Dataset (from UCI Machine Learning Repository) and perform data preprocessing, transformation, and visualization using RapidMiner's visual interface. Apply a machine learning algorithm for classification. Analyze and interpret the results. Explore different techniques and create a complex project.

## Technologies

### Rapidminer: 

- RapidMiner is a comprehensive data science platform known for its extensive capabilities in |machine learning, predictive analytics, and data mining. 
- RapidMiner excels in providing an end-to-end environment for data science tasks. It integrates various stages of the data science lifecycle, from data preparation and exploration to model building and deployment.
- Support for major scripting languages such as Python and R, allowing for advanced customizability​.
- Unlike many other data science platforms, RapidMiner provides a holistic solution that is highly automated, reducing the need for manual coding. This makes it particularly appealing to non-technical users, termed "citizen data scientists," who can leverage its powerful capabilities without a deep programming background.
- RapidMiner also differentiates itself by integrating seamlessly with a wide array of data sources and providing capabilities for handling big data through its extension, RapidMiner Radoop
- User-friendly with a strong emphasis on GUI-based workflow design.
- Broad compatibility with various data types and extensive integration options.
- Strong community support and a marketplace for sharing extensions and plugins.
- In our study of big data systems, we have discussed the importance of versatile tools that
  can handle the analytical and operational aspects of data science projects.RapidMiner's 
  capabilities are closely related to these topics, particularly its handling of data, support
  for model validation techniques such as automated machine learning (AutoML),
  cross-validation, and the use of supervised and unsupervised learning methods。

### Docker: 

- Docker is a platform designed to make it easier to create, deploy, and run applications by
  using containers.
- Docker streamlines the development process by allowing developers to work in standardized 
  environments using local containers which provide your applications and services. 
-  Docker can use Dockerfile to build images automatically by reading the instructions from a 
  Dockerfile, a text document that contains all the commands a user could call on the command line to assemble an image.
- The Dockerfile specifies the use of an official Python runtime as the base image, and copies 
  the Python script into the container. The resulting Docker image encapsulates the entire project, making it easily deployable and scalable.
- Docker provides Docker Compose, a tool for defining and running multi-container Docker
 applications. With Compose, you use a YAML file to configure your application's services, networks, and volumes, and then with a single command, you create and start all the services from your configuration​ 

## Docker implementation

- The Docker system designed for this project follows a logical sequence to
  ensure a smooth and consistent environment for both development and deployment

- Let's delve into the intricacies of the Docker system logic:

- Project Setup:
  - Begin with organizing your project files within a directory structure. The
    main files include:
    - `605_pro.py`: Contains the python
      code for fetching user profiles with Redis caching.
    - `Dockerfile`: Includes instructions for building a Docker image for the
      project.
    - `Docker-compose.yaml`: Defines services, networks, and volumes for Docker
      containers.

- Dockerfile Configuration:
  - Start by setting up the Dockerfile with the following steps:
    - **FROM**: Utilize an official Python runtime as the base image `python:3.7`
    - **WORKDIR**: Set the working directory in the container to `/app`.
    - **COPY**: Copy the project files into the container.
    - **RUN**: Install necessary dependencies (scikit-learn,pandas,matplotlib and seaborn) using pip.
    - **VOLUMN**: Mounting a data volume `/input` and `/output`
    - **CMD**: Specify the default command to run the Python script.
  
- Docker-compose.yaml Configuration:
  - Configure the docker-compose.yaml file to define the services required for
    the project:
    - Define service: Python.
    - Configure the Python service:
      - `version: '3'`: This specifies the version of the Docker Compose file format.
      - `services`: This section defines the services that make up the application. In this  case,there is only one service named server.
      - `build: src`This tells Docker Compose to build the Docker image for the service using   
        the Dockerfile located in the `src` directory relative to the Docker Compose file. 
        This is useful for creating custom images tailored to specific services
      - `volumes` This part of the configuration mounts volumes into the container:
        - `./input:/input`: This mounts the input directory from the host machine to the /input directory inside the container. This is useful for providing input data to the application running in the container.
        - `./output:/output`: Similarly, this mounts the output directory from the host machine to the /output directory inside the container. This setup allows the application to write output data back to the host.

- Building the Docker Image And Running the Docker Containers:
  - Execute `docker-compose up --build`. It is a very useful command when working with Docker Compose, as it both builds (or rebuilds) images for services that have a build configuration specified in the docker-compose.yml file and then starts the containers. 
    - Building Images: The `--build` option forces Docker Compose to build the images for the services defined in the docker-compose.yml file before starting the containers.
    - Starting Containers: After building the images, Docker Compose proceeds to create and start the containers based on the configurations specified in the docker-compose.yml file.
    - This includes setting up volumes and other settings that are defined for the services before.
    - The container then runs my python script and outputs the results to the location where I previously mounted it `/output`.


## Rapidminer Process

I have used Rapidminer to build a process to explore and process the data and apply its own machine learning algorithm and different algorithms in python for binary classification respectively. The dataset I used is Bank Marketing Dataset from UCI Machine Learning Repository.Here is the flowchart of my Process

![Process](/plots/Process.png)
- **Statistics** : In this step, the data is first analyzed statistically in order to understand 
  the basic characteristics and distribution of the data. Then the missing values in the data are processed using the Replace Missing Values operator, which is done with mean padding.
- **Set Role**: Set the role of each column in the data, in this data set y is the label.
![Process](/plots/y.png)
- It can be seen that there is a large gap between the number of samples labeled `yes` and `no`. 
- In a binary classification problem, if the number of samples for one label is much larger than the other, this situation is known as class imbalance (CLASS IMBALANCE). Class imbalance can have a significant impact on the training and performance of the model. 
- So next I resampled the data of `no`.

- **Filter Examples**: Use the “Filter Examples” action to select the labeled data that I want to sample.
- **Sample (Bootstrapping)**: Connect the filtered data to the “Sample (Bootstrapping)” operation. Set the parameter of “Sample (Bootstrapping)” operation, the sample size is 5200, which is equivalent to the number of yes samples.

- **Append**: Append: Once the sampling is complete, the sampled data needs to 
  be re-merged with the unsampled data to maintain the integrity of the dataset.Use the “Append” operation to merge the unsampled data (using the complement of the first “Filter Examples” operation) with the sampled data.

- **Generate Attributes**: I used this operator to construct a derived attribute of `total_loan`, calculated from Personal `loan` + `housing` , to combine to enhance the predictive power of the model.

- **Discretize**: use this operator to bin (Binning) age to discretize it, allowing the data to 
  focus on a certain type of age group, rather than a characteristic age value, which is more in line with realistic behavioral traits such as youth, middle age, and old age.

- **Nominal to Numerical**: Converts nominal features (category variables) to numerical values so that they can be used later in the model.

- **Normalize**: I chose to pair `duration` and `bbalance`, which statistically show that their scales span a relatively large range, and normalizing them to ensure that the scales of the different features are consistent will help the model learn and predict better.
![bar](/plots/Balance_and_Duration_about_Job.png)
- After regularization, balances and durations are shown together, and it can be seen that there is a correlation between occupations and balances, with most occupations having lower balances, but a few occupational categories (e.g., those labeled 3 and 4) show higher average account balances, which may indicate that customers in these occupations have higher financial strengths, and that they are more likely to subscribe to a bank's time deposit product, i.e. may be categorized as `yes`.

- **Select Attributes**: select important features to be used for model training, I have removed 
  the individual date day, contact and defaul as they have very little impact on whether or not a customer will subscribe to a bank's time deposit product.
![Heatmap](/plots/Heatmap.png)
- As can be seen on the heat map, most of the rows marked `yes` in the upper part of the heat map show light yellow and darker colors, indicating higher eigenvalues (duration) in these rows. In the lower rows marked `no`, the color is generally closer to blue, indicating lower eigenvalues.
-  This may mean that the results tend to be `yes` when the duration increases, and `no` when the duration is lower, suggesting that duration can be a good choice for attributes.

- **Split Data**: Split the data into a training set and a test set according to 8:2, which is used 
  to evaluate the generalization ability of the model.。

- The following section is about binary classification using machine learning algorithms, on 
  Rapidminer my algorithm of choice is neural networks.

- **Neural Net**: model training using a neural network with a learning rate set to 0.01 and a 
  training period of 200, with two hidden layers, the first with 30 neurons and the second with 10 neurons.
- **Apply Model**: Apply the trained model to new data, make predictions, and then evaluate the model's performance using Performance
![NN](/plots/accuracy.png)
- It can be seen that there is a good performance in terms of accuracy good recall, which 
  indicates that the characteristics of the data have been analyzed using rapidminer, 
  and the data has been processed appropriately to better sample the category, i.e., whether or not the customer will subscribe to the bank's time deposit product.

## Python Script Overview

The Python script (605_pro.py) is designed to perform a complete machine learning process on top of the data processed in Rapidminer, using a different algorithm than the one in Rapidminer, the Random Forest Classifier, to solve a binary classification problem. To differentiate the performance on the model.

- It first loads the dataset in CSV format processed by Rapidminer to save the trouble of data processing. Then it splits the data into training set and test set according to a certain ratio (8:2).

- Next, the script is trained using a random forest model with parameters that are preset or can be adjusted as needed. After training, the script evaluates the performance of the model using the test set data, calculates metrics such as accuracy, precision, recall, and F1 score, and generates a confusion matrix and ROC curve to further analyze the model performance.

```
# Instantiate the model
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_classifier.fit(X_train, y_train)

# Predict on the test set
y_pred = rf_classifier.predict(X_test)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
```

- In addition, the script includes a feature importance analysis to help understand which features have a greater impact on the prediction results. This script builds on Rapidminer's processing of data to provide a comprehensive solution to the binary classification problem of machine learning for scenarios that require precise control over data processing and model evaluation steps.


![Confusion_Matrix](/plots/Confusion_Matrix.png)
- This is the confusion matrix for the model output. It shows the relationship between the true categories and the model-predicted categories.

![ROC](/plots/ROC%20Curve.png)
- It is the receiver operating characteristic (ROC) curve of the model, and the area under the curve (AUC) is 0.90, indicating that the model has a good ability to distinguish between positive and negative samples.

![Weight](/plots/Feature_Importance.png)
- This figure shows the importance of each feature in the Random Forest model, in such a way that it is possible to see which features are more critical to the prediction results.
- It can be seen that the duraion feature has the highest importance and has a large impact on the prediction results, which matches the results shown in the previous heat map.

## Conclusion

The Data Mining with Rapidminer project effectively combines the strengths of RapidMiner,Python, and Docker to create a robust data mining solution that is both efficient and scalable. By leveraging RapidMiner's powerful data analysis capabilities, the project significantly enhances our ability to uncover insights and patterns from complex datasets. Python scripts facilitate the automation of data processing and analysis tasks, ensuring seamless data flow and integration. Docker's containerization providing a consistent and portable environment across various platforms which simplifies the implementation and maintenance of the application.