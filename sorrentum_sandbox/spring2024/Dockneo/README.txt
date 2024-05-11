Project Title: Graph Database Exploration with Neo4j

Description:
This project performs Graph Database Exploration using Neo4j technology. The system models users, friendships, and tags, with users represented as nodes, friendships as relationships between nodes, and tags as additional nodes connected to users. The analysis includes essential insights such as finding friends of friends, common connections, and influential users.

Project Structure:
- `data.csv`: CSV file containing user data including user IDs, screen names, tags and other columns.
- `scripts/graphdatabase_exploration.py`: Python script implementing the project. This script connects to a Neo4j database, loads data from the CSV file, and performs social network analysis using Cypher queries.
- `cypherqueries.txt`: Text file containing Cypher queries for social network analysis.
- `README.txt`: This file, providing an overview of the project and instructions for running the code.

Instructions:
1. Docker Method:
   - Run the Docker container provided in the repository.
   - Open a web browser and navigate to `localhost:7474`.
   - Enter Cypher queries to interact with the Neo4j database and perform social network analysis.

2. Python Script Method:
   - Execute the `graphdatabase_exploration.py` script located in the `scripts` folder.
   - Follow the on-screen prompts to run the code and perform social network analysis.

Dependencies:
- Neo4j: Ensure Neo4j is installed and running locally.
- Python 3: Install Python 3 along with the `neo4j` and `pandas` libraries.

