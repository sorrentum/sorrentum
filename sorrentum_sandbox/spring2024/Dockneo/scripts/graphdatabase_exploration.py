from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

# Function to connect to Neo4j
def connect_to_neo4j(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver.session()

# Function to load data from CSV file into Neo4j
def load_data(session):
    df = pd.read_csv(r'data.csv', sep=',(?=\S)', engine='python')
    
    for index, row in df.iterrows():
        user_id = str(row['id'])
        screen_name = row['screenName']
        tags = row['tags'].split(',')
        
        # Create user node
        session.run("MERGE (u:User {id: $user_id}) "
                    "SET u.screenName = $screen_name", 
                    user_id=user_id, screen_name=screen_name)
        
        # Create tag nodes and connect them to the user
        for tag in tags:
            session.run("MERGE (t:Tag {name: $tag}) "
                        "MERGE (u)-[:POSTED]->(t)", 
                        tag=tag)

# Function to perform social network analysis
def social_network_analysis(session):
    # Find friends of friends for all users
    result = session.run("MATCH (u1:User)-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(fof:User) "
                         "RETURN DISTINCT u1, fof")

    print("Friends of Friends for All Users:")
    for record in result:
        print(record['u1']['screenName'], "->", record['fof']['screenName'])

    # Find common connections between all users
    result = session.run("MATCH (u1:User)-[:FRIENDS_WITH]-(common)-[:FRIENDS_WITH]-(u2:User) "
                         "WHERE id(u1) < id(u2) "
                         "RETURN DISTINCT u1, u2, common")

    print("\nCommon Connections Between All Users:")
    for record in result:
        print(record['u1']['screenName'], "-", record['common']['screenName'], "-", record['u2']['screenName'])

# Main function
def main():
    # Connect to Neo4j
    with connect_to_neo4j(uri, username, password) as session:
        # Load data from CSV
        load_data(session)
        
        # Perform social network analysis
        social_network_analysis(session)

if __name__ == "__main__":
    main()
