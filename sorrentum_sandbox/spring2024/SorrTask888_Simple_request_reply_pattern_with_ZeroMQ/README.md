# Simple Request Reply Pattern With ZeroMQ

## Author info

- Author: Dev Karan Suresh
- GitHub account: kev-daran
- UMD email: devk@umd.edu
- Personal email: devkaran7501@gmail.com

## Description

This project is an advanced implementation of a request/reply pattern using ZeroMQ in Python with the pyzmq library. The aim is to build a robust client-server architecture where clients can send requests to a server and receive responses efficiently. The project extends the basic request/reply pattern to include features such as error handling, load balancing, and asynchronous communication.

## Technologies

### ZeroMQ: Advanced Messaging Library

- ZeroMQ, also known as zmq, is a high-performance asynchronous messaging library that provides scalable, distributed communication for building distributed or concurrent applications.
- ZeroMQ facilitates communication between multiple nodes in a distributed system, enabling them to exchange messages in various patterns such as request/reply, publish/subscribe, and push/pull.
- It abstracts the complexities of network communication, allowing developers to focus on application logic rather than low-level socket programming.
- ZeroMQ provides built-in support for fault tolerance and reliability, with features like message queuing, message buffering, and automatic reconnection mechanisms.
- This helps ensure that messages are delivered reliably even in the presence of network failures or node crashes.
- ZeroMQ supports asynchronous messaging, allowing processes to send and receive messages independently without blocking. This enables efficient communication and coordination between components of a distributed system. It is a powerful tool for building distributed and concurrent applications, offering a simple yet powerful messaging infrastructure that can handle a wide range of communication scenarios.
- ZeroMQ stands out from traditional messaging systems like RabbitMQ and ActiveMQ due to its lightweight nature and minimalistic design. Unlike these systems, which often rely on centralized brokers for message routing, ZeroMQ uses a broker less architecture, reducing overhead and improving scalability. This design choice makes ZeroMQ particularly suitable for high-throughput, low-latency scenarios.
- ZeroMQ is designed to be lightweight and efficient, making it suitable for resource-constrained environments.
- It supports various messaging patterns and can be easily integrated into existing applications.
- ZeroMQ offers high throughput and low latency, making it ideal for demanding real-time applications.
- The absence of a centralized broker simplifies deployment and reduces single points of failure.
- Unlike some traditional messaging systems, ZeroMQ does not provide built-in message persistence, which may be a limitation for certain use cases.
- It is universal, high speed, multi-socket and backed by a large and active open-source community. 

### Docker: Containerization

-  Docker is a containerization platform that allows developers to package applications and their dependencies into lightweight, portable containers.
-  Docker containers provide a high level of isolation, allowing applications to run independently of the underlying host system.
-  Docker simplifies dependency management by allowing developers to specify the exact environment needed for their applications. This reduces compatibility issues and ensures that applications run consistently across different development machines and servers.
-   Docker encourages a modular approach to application development, where applications are broken down into smaller, independent services running in separate containers. This facilitates the adoption of microservices architecture, allowing for easier maintenance, updates, and scaling of individual components.

## Docker System Overview

### Components of the Docker System

- Server Container:
</t><br>•	Hosts the server-side logic implemented in server.py.
</t></br>•	Utilizes ZeroMQ sockets to listen for incoming requests from clients.
</t></br>•	Handles request processing and sends back responses.

- Client Container:
</t><br>•	Contains the client-side logic implemented in client.py.
</t></br>•	Sends requests to the server container using ZeroMQ sockets.
</t></br>•	Processes responses received from the server.

- Nginx Container:
</t></br>•	Acts as a reverse proxy and load balancer for the server containers.
</t></br>•	Receives incoming requests from clients.
</t></br>•	Distributes these requests among multiple server instances for load balancing.

### Mock Workflow of the docker system

- The Docker system is initialized by running docker-compose up command.
- Docker Compose creates containers for the server, client, and Nginx components based on the specifications in the docker-compose.yml file.
- Multiple client instances are spawned using the run_clients.py script.
- Each client instance sends requests to the Nginx container, specifying the endpoint for the desired service.
- Nginx receives incoming requests from the client instances.
- It distributes these requests among multiple server instances based on load balancing algorithms such as round-robin or least connections.
- The server instances receive requests forwarded by Nginx.
- They process these requests asynchronously, handling multiple concurrent requests efficiently using asyncio in the server-side code.
- Upon processing, the servers send back HTTP responses to Nginx.
- Nginx receives responses from the server instances.
- It aggregates these responses and forwards them back to the respective client instances that originated the requests.
- Each client instance receives responses from Nginx.
- Once all client requests have been processed and responses received, the Docker system remains active and ready to handle subsequent requests.

- The following diagram shows the workflow of the project.

![image](https://github.com/Kev-Daran/kaizenflow/assets/81677957/699d060d-8e6e-4d15-9585-7f3065af7c6b)



## Running the Docker System

To run the entire system, including the server, client, and NGINX load balancer, follow these steps:

- Build the Docker Images:
  - Navigate to the directory containing the Dockerfiles and the docker-compose.yml file.
  - Run the command `docker-compose up --build`. This will build the Docker images for the server, client, and NGINX load balancer.
- Start the Server:
  - Open a new terminal window or tab.
  - Navigate to the same directory as before.
  - Run the command `docker-compose up server`. This will start the server container.
- Start the Client:
  - Open another terminal window or tab.
  - Navigate to the same directory.
  - Run the command `docker-compose up client`. This will start the client container.
- Run the Clients Script:
  - To simulate multiple clients connecting to the server concurrently, execute the run_clients.py script by running the `python3 run_clients.py` command.

## Expected Output

Upon running the system, you will observe the following outputs:
- The server will start and listen for incoming requests on port 5555.
- The client will connect to the server and send multiple requests sequentially.
- If any request contains malformed data (such as missing address), the server will log an error message but continue processing subsequent requests.
- As the clients script runs, you may notice the outputs of the two clients interleaved in the terminal. This indicates that the server is processing requests asynchronously, handling multiple clients concurrently.

### Example Output
- On running the `python3 run_clients.py` command with 2 client instances, we may observe an output that looks like:

```
Starting sorrtask888_simple_request_reply_pattern_with_zeromq_client_1 ... done
Starting sorrtask888_simple_request_reply_pattern_with_zeromq_client_1 ... done
Attaching to sorrtask888_simple_request_reply_pattern_with_zeromq_client_1
client_1  | Sending request: 0
client_1  | Sending request: 0
client_1  | Received response: Server response
client_1  | Sending request: 1
client_1  | Received response: Server response
client_1  | Sending request: 2
client_1  | Received response: Invalid message
client_1  | Received response: Server response
client_1  | Sending request: 1
client_1  | Sending request: 3
client_1  | Received response: Server response
client_1  | Sending request: 4
client_1  | Received response: Server response
client_1  | Sending request: 2
client_1  | Received response: Server response
client_1  | Sending request: 5
client_1  | Received response: Invalid message
client_1  | Sending request: 3
client_1  | Received response: Server response
client_1  | Received response: Server response
client_1  | Sending request: 6
client_1  | Received response: Server response
client_1  | Sending request: 7
client_1  | Sending request: 4
client_1  | Received response: Server response
client_1  | Sending request: 5
client_1  | Received response: Server response
client_1  | Sending request: 8
client_1  | Received response: Server response
client_1  | Received response: Server response
client_1  | Sending request: 6
client_1  | Received response: Server response
client_1  | Sending request: 9
client_1  | Received response: Server response
client_1  | Sending request: 7
client_1  | Received response: Server response
client_1  | Sending request: 8
client_1  | Received response: Server response
client_1  | Sending request: 9
client_1  | Received response: Server response
sorrtask888_simple_request_reply_pattern_with_zeromq_client_1 exited with code 0
sorrtask888_simple_request_reply_pattern_with_zeromq_client_1 exited with code 0
```
- Output Explanation:
    - 2 clients sends requests to the server at roughly the same time.
    - The server responds to each of these clients asynchronously, thus, we get interleaved outputs.
    - As both instances of the client runs the same command to send erroneous data at request 2, the server responds with `Invalid message` and continues processing the next requests.

## Implementation

### Dockerfiles:
- Dockerfile_server and Dockerfile_client:
  
    - This Dockerfile defines the environment and instructions for building the server/client container.
    - It starts with the Python 3 base image to provide the necessary runtime environment.
    - Copies the server/client.py file into the container's filesystem.
    - Installs the pyzmq library using pip to enable ZeroMQ functionality.  
    - Sets the command to execute when the container starts, which is to run the server/client.py script.

- docker-compose.yaml:

    - It specifies three services: server, client, and nginx.
    - Each service is built using its respective Dockerfile (Dockerfile_server, Dockerfile_client, and Dockerfile_nginx).
    - The server service is connected to the zmq_network bridge network, ensuring communication with other services.
    - The client service depends on the server service, ensuring that the server is started before the client.
    - The nginx service is configured to listen on port 80 and forward requests to the backend servers.
    - All services are connected to the zmq_network bridge network for communication between containers.

- NGINX Dockerfile :

    - This Dockerfile specifies the NGINX configuration for the load balancer.
    - It uses the official NGINX base image.
    - Copies the nginx.conf file from the local filesystem to the NGINX configuration directory within the container.
 
### Python Scripts:

- Server.py
    - This script implements the server-side logic using the ZeroMQ and asyncio libraries.
    - It creates a ZeroMQ REP socket to listen for incoming requests from clients.
    - The server is designed to handle requests asynchronously using asyncio.
    - It registers the socket with a poller to wait for incoming messages and responds to them accordingly.
    - The server checks the format of incoming messages and sends appropriate responses.
    - Error handling is implemented to catch ZeroMQ errors during socket operations.
 
- Client.py
    - This script implements the client-side logic using the ZeroMQ library.
    - It creates a ZeroMQ REQ socket to connect to the server and send requests.
    - In request number 2 we intentionally send data without its address to test the error handling of the server.

- run_clients.py
    - This script is designed to run multiple instances of the client concurrently to simulate multiple clients connecting to the server.
    - It utilizes the subprocess module to execute the client.py script in separate Python processes.
    - The run_client_instance function defines the command to run a single client instance using the subprocess.run() function.
    - In the main block, it iterates twice to run two client instances concurrently.
    - By running multiple client instances concurrently, it simulates concurrent connections to the server and helps test the server's asynchronous capabilities.

## Conclusion
The project showcases the versatility and efficiency of ZeroMQ in building distributed and scalable systems. By incorporating features such as error handling, load balancing, and asynchronous communication, we have created a robust client-server architecture suitable for various real-world applications.

- Demo link: https://drive.google.com/file/d/17nlUTElRDGIZmdLY7SWDoJafAB4mtwTa/view?usp=sharing
