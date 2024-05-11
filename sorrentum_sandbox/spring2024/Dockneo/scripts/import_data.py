from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

driver = GraphDatabase.driver(uri, auth=(user, password))

import pandas as pd

# Read CSV file into a DataFrame
df = pd.read_csv('data.csv', sep=',(?=\S)', engine='python')

def import_data_from_dataframe(tx):
    for index, row in df.iterrows():
        # Create user node
        tx.run("CREATE (:User {id: $id, name: $name})", id=row['id'], name=row['friendName'])
        # Create friendships
        for friend_id in row['friends'].split(','):  # Assuming 'friends' column is comma-separated
            tx.run("MATCH (u:User {id: $user_id}), (f:User {id: $friend_id}) "
                   "CREATE (u)-[:FOLLOWS]->(f)", user_id=row['id'], friend_id=friend_id.strip())

with driver.session() as session:
    session.write_transaction(import_data_from_dataframe)
