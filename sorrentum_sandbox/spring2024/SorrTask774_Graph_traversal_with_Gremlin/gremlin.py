from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import T
from gremlin_python.process.graph_traversal import __

# set the graph traversal from the local machine:
connection = DriverRemoteConnection("ws://gremlin-server:8182/gremlin", "g")  # Connect it to your local server
g = traversal().withRemote(connection)

# Add vertices with properties
v1 = g.addV('person').property('name', 'Alpha').property('age', 22).next()
v2 = g.addV('person').property('name', 'Beta').property('age', 37).next()
v3 = g.addV('person').property('name', 'Gamma').property('age', 28).next()
v4 = g.addV('person').property('name', 'Delta').property('age', 66).next()
v5 = g.addV('person').property('name', 'Epsilon').property('age', 45).next()
v6 = g.addV('dog').property('name', 'Zeta').property('age', 5).next()
v7 = g.addV('dog').property('name', 'Eta').property('age', 2).next()
v8 = g.addV('dog').property('name', 'Theta').property('age', 9).next()

# Add edges with weights
e1 = g.V(v1).addE('knows').to(__.V(v2)).property('weight', 5).next()
e2 = g.V(v1).addE('knows').to(__.V(v3)).property('weight', 3).next()
e3 = g.V(v1).addE('knows').to(__.V(v5)).property('weight', 2).next()
e4 = g.V(v2).addE('knows').to(__.V(v3)).property('weight', 7).next()
e5 = g.V(v4).addE('knows').to(__.V(v5)).property('weight', 4).next()
e6 = g.V(v5).addE('knows').to(__.V(v1)).property('weight', 9).next()
e7 = g.V(v5).addE('knows').to(__.V(v2)).property('weight', 8).next()
e8 = g.V(v5).addE('knows').to(__.V(v3)).property('weight', 6).next()
e9 = g.V(v5).addE('knows').to(__.V(v4)).property('weight', 3).next()
e10 = g.V(v3).addE('owns').to(__.V(v6)).property('weight', 4).next()
e11 = g.V(v3).addE('owns').to(__.V(v7)).property('weight', 1).next()
e12 = g.V(v5).addE('owns').to(__.V(v8)).property('weight', 6).next()

# Traverse the graph to get all vertices
vertices = g.V().toList()
print("Vertices:", vertices)

# Traverse the graph to get all edges
edges = g.E().toList()
print("Edges:", edges)

# Traverse the graph to get the names of all vertices
vertex = g.V().valueMap().toList()
# Print out the name and age of each vertex
for name_age in vertex:
    print(name_age)

# Example traversal: Find all people known by Alpha
result = g.V().has('name', 'Alpha').out('knows').toList()
print("People known by Alpha:", result)

# Example traversal: Find all people known by Beta
result = g.V().has('name', 'Beta').out('knows').toList()
print("People known by Beta:", result)

# Example traversal: Find all people known by Gamma
result = g.V().has('name', 'Gamma').out('knows').toList()
print("People known by Gamma:", result)

# Example traversal: Find all dogs owned by Gamma
result = g.V().has('name', 'Gamma').out('owns').toList()
print("Dogs owned by Gamma:", result)

# Example traversal: Find all people known by Delta
result = g.V().has('name', 'Delta').out('knows').toList()
print("People known by Delta:", result)

# Example traversal: Find all people known by Epsilon
result = g.V().has('name', 'Epsilon').out('knows').toList()
print("People known by Epsilon:", result)

# Example traversal: Find all people who know Epsilon
result = g.V().has('name', 'Epsilon').in_('knows').toList()
print("People who know Epsilon:", result)

# Example traversal: Find all dogs owned by Epsilon
result = g.V().has('name', 'Epsilon').out('owns').toList()
print("Dogs owned by Epsilon:", result)

# Example traversal: Find all vertices of type 'person'
people = g.V().hasLabel('person').toList()
print("List of People:", people)

# Example traversal: Find all vertices of type 'dog'
dogs = g.V().hasLabel('dog').toList()
print("List of Dogs:", dogs)

# Traverse the graph to get all vertices with age = 37
age_37 = g.V().hasLabel('person').has('age', 37).valueMap().toList()
print("Who is 37 years old?", age_37)

# Traverse the graph to get the names and ages of all vertices
names_and_ages = g.V().hasLabel('person').valueMap('name', 'age').toList()

# Filter vertices based on age greater than a certain number
age_threshold = 30
filtered_names_and_ages = [(vertex_data['name'][0], vertex_data['age'][0]) for vertex_data in names_and_ages if int(vertex_data['age'][0]) > age_threshold]

# Print the filtered names and ages
print("Names and Ages above:", age_threshold, ':')
for name, age in filtered_names_and_ages:
    print(f"Name: {name}, Age: {age}")

# Traverse the graph to get the weights of all edges
weights = g.E().valueMap('weight').toList()

# Print the weights of all edges
print("Weights of all edges:")
for weight in weights:
    print(f"Weight: {weight}")

# Close the connection
connection.close()

print('**Code Complete** Close connection to Gremlin Server.')
