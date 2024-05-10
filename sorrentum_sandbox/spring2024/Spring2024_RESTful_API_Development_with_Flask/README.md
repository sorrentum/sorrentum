# Restful API Development with Flask

## Author Info

- Author: Joseph Sketl
- Github Account: jsketl
- UMD Email: jsketl@umd.edu

## Description

- This is a python based project that implements a Flask API to manage a MySQL employee database. The goal of this project is to leverage Flask's minimalist design to create endpoints for performing CRUD operations on a dynamic employee data model. The project uses the MySQL employees sample database for implementing the API endpoints.

## Technologies

### Flask: Web Framework for Python

- Flask is a lightweight and flexible web framework for Python. It provides tools, libraries, and patterns to build web applications quickly and efficiently. Flask follows the Web Server Gateway Interface (WSGI) standard, making it compatible with various web servers and deployment options.
- Flask simplifies web development by providing features such as routing, request handling, and templating. It allows developers to create web applications with minimal boilerplate code, focusing on the logic specific to their application.
- Flask is different from other web frameworks like Django in that it is more lightweight and minimalist. It does not impose strict conventions or include built-in components for features like ORM (Object-Relational Mapping) or authentication. Instead, Flask follows a "micro-framework" approach, providing only the essential tools needed for web development. This gives developers more flexibility to choose their preferred libraries and tools for different aspects of their application.
- Pros
	- Flask is lightweight and has minimal dependencies, making it easy to learn and use for both small and large projects.
	- Flask's minimalist design allows developers to choose the libraries and tools that best fit their project requirements, leading to more tailored and efficient solutions.
	- Flask can be easily extended with third-party extensions and libraries to add additional functionality such as authentication, database integration, and API development.
- Cons
	- Flask requires developers to manually configure and integrate additional libraries for features like database access, authentication, and validation, which can add complexity to larger projects.
	- While the flexibility of Flask is a strength, it can also be a drawback for developers who prefer a more opinionated framework with built-in conventions and components.
	- Flask's minimalist design may require additional effort to scale and maintain for large and complex applications compared to more comprehensive frameworks like Django.
- Flask-JWT Extended
	- Flask-JWT-Extended is a Flask extension that adds support for JSON Web Tokens (JWT) authentication to Flask applications. It provides tools for generating and verifying JWT tokens, managing user authentication, and protecting routes with JWT-based access control.
	- Pros
		- It provides flexibility in configuring JWT authentication settings, such as token expiration time, token refreshing, token encoding and decoding functions, and custom claims.
		- Flask-JWT-Extended supports token revocation and token blacklisting, which enhances security by allowing tokens to be invalidated before their expiration time
		- It supports token refreshing, which allows clients to obtain a new JWT token without requiring users to re-authenticate with their credentials.
	- Cons
		- Flask-JWT-Extended relies on external dependencies such as PyJWT for JWT token encoding and decoding, which may lead to version compatibility issues or dependency conflicts in complex Flask applications.
		- Using JWT tokens for authentication introduces some performance overhead compared to session-based authentication, as the server needs to validate and decode JWT tokens for each request.
		- While Flask-JWT-Extended offers token refreshing and blacklisting features, developers need to implement token management logic manually, which may require additional effort and attention to security.

## Docker Implementation

- The docker system for this project creates two containers: one to host the MySQL database and one to contain the API script and other python files.
- Project Setup:
	- The project files are held in the Spring2024_Restful_API_Development_With_Flask directory. It includes:
		- 'App': Directory containing the python file for setting up the Flask API, the Jupyter Notebook to test the various endpoints of the API, and the models python file to establish the data structure of the database for SQLAlchemy
		- 'docker-entrypoint--initdb.d': Directory the SQL script to create the MySQL database, as well as all the .dump files containing the information to populate the database. The directory initializes the database when the container is created.
		- Data: Directory to store the database when the container stops running or crashes.
		- 'docker-compose.yml': Defines services, volumes, ports, and other necessary information to create the containers
		- 'restful_api.dockerfile': Includes instructions for building the Flask API docker image for the project.
- Dockerfile Configuration:
	- Uses 'python3:9' official runtime image
	- Sets environment variables 'PYTHONDONTWRITEBYTECODE 1'to ensure python does not compile source data into bytecode and 'PYTHONUNBUFFERED 1' to ensure Python's output is not buffered and provides real-time feedback into the application's behavior.
	- Sets working directory in the container to '/app'.
	- Copies the project files into the container 'COPY ./app'.
	- Installs necessary dependencies listed in the requirements.txt file, as well as installing Jupyter to set up a Jupyter Notebook server
	- 'Expose port 5000' for the Flask app
	- 'Expose port 8888' for the Jupyter Notebook server.
	- 'CMD ["bash", "-c", "jupyter notebook --ip='0.0.0.0' --port=8888 --no-browser --allow-root & python app.py"]' sets the command to start the Jupyter Notebook and Flask API
- Docker-compose.yml Configuration:
	- Defines two services: 'mysql' and 'flask_app'
	- Configure mysql service:
		- Uses the official mysql:8.4 image.
		- Set username to 'Root' and password to 'password'
		- Configure volumes in the container to './docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d' and './data:/var/lib/mysql'.
		- Maps 'port 3306' on the computer to 'port 3306' in the container.
	- Configure flask_app service:
		- Build container using the 'restfulapi_flask.dockerfile'
		- Configures volume in the container to './app' from the directory './app'.
		- Maps 'port 5000' on the computer to 'port 5000' in the container for the Flask app and 'port 8888' to 'port 8888' for the Jupyter Notebook Server
		- Makes the flask_app container dependent on the mysql container so that it does not initialize until after the mysql database is created.
- Starting the Docker Containers:
	- Execute 'docker-compose up' to build the images and start the containers.
	- MySQL image will be pulled (10 layers)
	- flask_app will be built 
		- Will load build definition from 'restful_api.dockerfile'
		- [1/5]: Will pull python image from docker.io
		- [2/5]: Will set the working directory to './app'
		- [3/5]: Copies './app' into the container.
		- [4/5]: Will pip install all packages listed in 'requirements.txt'
		- [5/5]: Runs 'pip install jupyter'
	- Default network 'spring2024_restful_api_development_with_flask_default' for containers to communicate with each other.
	- Creates flask_app and mysql containers.
	- MySQL Server Setup 
		- Initializes a MySQL server connection
		- Initializes InnoDB engine
	- Flask App and Jupyter Notebook server will initialize.
	- MySQL Database Creation:
		- Runs from entrypoint 'docker-entrypoint-initdb.d/employees.sql'
		- Database structure is created, database is named employees.
		- Database info is loaded into the tables.
- Accessing Flask App
	- Navigate to 'http://localhost:5000' in a web browser to access the flask app
	- Navigate to 'http://localhost:8888' in a web browser to access the Jupyter Notebook
	- Interact with notebook file (query_test.ipynb) to execute test code for testing the API's endpoints
- Stoping the Docker Containers:
	- Press 'CTRL + C' in the terminal to stop containers and remove them.
## File Overview

### App.py 

- 'app.py' is the flask app script to set up the API endpoints and establish a connection to the MySQL database. The purpose of this API script is to facilitate easy updates to a dynamic data model, such as an employee database. A growing company will have a constant flow of employees, department assignments and reassignments, new titles, new roles, and different salaries. The API allows for the users to update and change this information without restructuring the data model.All non-read operation endpoints require a JWT token in order to prevent unauthorized individuals from altering information of employees and departments.
	- The app creates a SQLAlchemy engine creating a connection to the MySQL database at 'mysql://root:password@mysql:3306/employees' and a SQLAlchemy session is initialized.
	- A JWTManager instance is created along with an authentication endpoint to facilitate getting a JWT token to interact with certain API endpoints.
	- Various CRUD operation endpoints are created including:
		- Create:
			- Create new employee
			- Create employee title
			- Create employee salary
			- Assign employee department
			- Create new department
			- Assign department manager
		- Read:
			- Get all employees
			- Get employee by employee number
			- Get employee by name
			- Get total employees
			- View Titles table
			- View Titles by employee number
			- View Salaries table
			- View Employee Department Table
			- View department employees by employee ID
			- View Departments table
			- View Department Managers table
		- Update:
			- Update employee information
			- Update titles 
			- Update manager assignment
			- Update department information
			- Update salaries
			- Update employee's department
		- Delete
			- Delete employee
			- Delete employees (batch)
			- Delete department

### Query_testing.ipynb

- 'query_tester.ipynb' is a simple Jupyter Notebook to test the endpoints and ensure they are functioning as expected. The notebook is also a convenient template for performing CRUD operations for the API.
- Query Structure:
	- URL for API endpoint, e.g., 'http://127.0.0.1:5000/titles/9998'
	- New data (if necessary)
	- Send request (PUT, GET, DELETE)
	- Check response and response code

Example:
```
# Check for an employee

    base_url = 'http://127.0.0.1:5000/'
    # Send a GET request to retrieve employee number

    response = requests.get(f'{base_url}employees/6000')
    try:

    # Check if the request was successful (status code 200)

    response.raise_for_status()

    # Try to decode the JSON response

    employee_data = response.json()

    # Print the employee data

    print(employee_data)

    except requests.exceptions.HTTPError as err:

    # Print the HTTP error message

    print(f"HTTP error occurred: {err}")

    except ValueError:

    # Handle the case where the response is not valid JSON

    print("Invalid JSON response from the server")

    except Exception as e:

    # Handle any other exceptions

    print(f"An error occurred: {e}")
```

Output:
```
{'birth_date': '2001-09-02', 'emp_no': 6000, 'first_name': 'Joseph', 'gender': 'M', 'hire_date': '2024-04-29', 'last_name': 'Smithy'}
```

Example:
```
    # Create a new title for employee

    url = 'http://127.0.0.1:5000/titles'

    new_title_data = {

    "emp_no": 6000,

    "title": "Senior Stacker",

    "from_date": "2024-06-11",

    "to_date": "9999-01-01"

}

# Send POST request

    response = requests.post(url, json=new_title_data, headers=headers)

    # Print response

    print(response.status_code)

    print(response.json())
    ```
    Output:
    ```
    201 {'message': 'Title created successfully'}
```
### Employees.sql

- 'employees.sql' is a SQL script for creating the employees database and loading the information.
- Defines model schema for each table.
- Defines sources for .dump files containing database data.

### Models.py

- 'models.py' is a python script with the same model schema for SQLAlchemy to use in the flask app.
- Includes a serialization function for each table to present information in JSON format.

# Database Schema

- The database defines 6 tables: employees, departments, dept_manager, dept_emp, titles, salaries. This schema was defined in the MySQL sample employees database. The structure was retained for this project as it supports a dynamic data model for employees and departments. Separating employee personal information from titles, salaries, and departments allows for changing employee info while accounting for future changes in the company's structure.
- Employees Table:
	- emp_no = Column(Integer, primary key)
	- birth_date = Column(Date, non-nullable)
	- first_name = Column(String(14), non-nullable)
	- last_name = Column(String(16), non-nullable)
	- gender = Column(Enum('M','F'), non-nullable)
	- hire_date = Column(Date, non-nullable)
- Departments table:
	- dept_no = Column(String(4), primary key)
	- dept_name = Column(String(40), non-nullable)
- Dept_Manager table:
	- emp_no = Column(Integer, foreign key = (employees.emp_no), primary key)
	- dept_no = Column(String(4), foreign key = departments.dept_no), primary key)
	- from_date = Column(Date, nullable=False)
	- to_date = Column(Date, nullable=False)
	- employee = relationships('Employee')
	- department = relationship('Department')
- Dept_emp Table:
	- emp_no = Column(Integer, foreign key = (employees.emp_no), primary key)
	- dept_no = Column(String(4), foreign key = departments.dept_no, primary key)
	- from_date = Column(Date, non-nullable)
	- to_date = Column(Date, non-nullable)
    - employee = relationship('Employee')
    - department = relationship('Department')
- Title Table:
    - emp_no = Column(Integer, foreign key = ('employees.emp_no'), primary_key)
    - title = Column(String(50), non-nullable)
    - from_date = Column(Date, primary_key)
    - to_date = Column(Date, non-nullable)
- Salary Table:
    - emp_no = Column(Integer, ForeignKey('employees.emp_no'), primary_key=True)
    - salary = Column(Integer, nullable=False)
    - from_date = Column(Date, primary_key=True)
    - to_date = Column(Date, nullable=False)

## Project Diagram
```mermaid

    sequenceDiagram

    participant User

    participant Docker-compose

    participant Query Script

    participant Flask

    participant Database

    User->> Docker-compose: Initialize containers

    Docker-compose->> Flask: Create API server
    Docker-compose->> Database: Create database server

    User-->> Query Script: Perform CRUD request

    Query Script-->> Flask: Send request to Flask endpoint

    Flask-->> Database: Perform CRUD operation request and update database

    Database-->> Flask: Operation successful

    Flask-->> Query Script: Operation successful

    Query Script-->> User: Operation successful

    else Entry not found/entry already exists

```