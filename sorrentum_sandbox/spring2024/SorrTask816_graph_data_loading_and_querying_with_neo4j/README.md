# Report: Graph Data Loading and Querying with Neo4j

## Project Description:

Install and configure Neo4j, and create a Python script to load graph data into the database. Define a simple graph schema and insert sample data representing entities and relationships. Use Neo4j's endpoint to execute basic graph queries and retrieve information from the database. Explore and present an innovative project.

[Watch the project video here](https://youtu.be/2khlbcsMUuQ)

*Please note that this project was changed with the Professor's Permission to use Neo4j rather than Allegrograph as originally intended. The original project description can be found at the end of this report.*
## Technologies Used
This project used 3 primary technologies: Docker, Jupyter Notebook, and Neo4j.
### Docker
Docker provides a containerized environment for running our project. This provides numerous advantages, most notably, it makes the project extremely portable, meaning it can easily be adapted for use in different environments and scales. Moving from a small scale container running on a PC can easily be scaled up to use on a dedicated rack or cloud environment.
### Jupyter Notebooks
Jupyter Notebooks provide a rich interactive environment for multiple programming languages, Python in the case of this project. It allows for mixed programming and presentation in the same document, allowing explanation, code, and output to all be visualized together easily.

Python's immense library of packages allows for flexible usage in production environments, and in this case provides simple means of communicating with the database through the py2neo package.
### Neo4j
Neo4j is a graph database management system (GDBMS) which aims to comply with ACID principles. It is implemented using JAVA and and can be queried using both an HTTP endpoint or through the binary Bolt protocol. Like other GDBMSs, [Neo provides robust and fast structures with numerous advantages over traditional relational databases for data which is hierarchical and/or semi-structured.](https://www.infoq.com/news/2008/06/neo4j/) Neo's HTTP endpoint uses their Cypher declarative query languages, allowing for relatively easy access to databases through a SQL-like language.

Two different Python packages are commonly used for interacting with Neo4j DBs- [the Neo4j created "Neo4j" and the community built "py2neo". Recently, py2neo has moved to being managed directly by Neo4j and the packages are basically interchangeable.](https://neo4j.com/developer-blog/py2neo-end-migration-guide/)In the case of my project I use py2neo. The py2neo python package allows for easy usage of the HTTP endpoint using normal CYPHER queries, as well as pseudo-Cypher which uses traditional elements of coding in Python and converts to CYPHER queries.
## Docker Logic
- Update version in docker compose

The Docker system I constructed is fairly simple. It has two primary components built on top of a base linux environment: Jupyter notebook and Neo4j.
### Jupyter Notebook
Starting in the Dockerfile, the first few lines a pretty intuitive:

``` dockerfile
# Base Jupyter Notebook Docker Image
FROM jupyter/datascience-notebook

# Disable authentication for JupyterLab
RUN echo "c.NotebookApp.token = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.password = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py
```

First, we specify the standard docker image for Jupyter notebook. Then the next two lines create our Jupyter notebook configuration file and specify that no token or password is required to login. Obviously in a production environment requiring either token or password entry would be advisable to keep data secure, however in this case, as no sensitive information is being used, I decided to forgo this protection for ease of use.

Next, I specify some Python packages which will be needed in my analysis which are not part of the default packages installed with Jupyter and I enable Jupyter lab:

``` dockerfile
COPY requirements.txt ./
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

ENV JUPYTER_ENABLE_LAB=yes
```

``` text
# requirements.txt
jupyterlab==3.0.7
neo4j==4.2.1
py2neo==2021.2.4
```

Lastly, in the Dockerfile I load some files which will be needed in the analysis from the project directory into the relevant directories I want them inside the container . I also specify a few other details like allowable IP addresses, which localhost port to use, allowing root access etc.

``` dockerfile
# Copy files into jupyter environment
COPY --chown=${NB_UID}:${NB_GID} ./notebooks /home/jovyan/work/analysis
COPY --chown=${NB_UID}:${NB_GID} ./sh_nw /home/jovyan/work/data

WORKDIR /home/jovyan/work

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/home/jovyan/work", "--allow-root"]
```

The docker compose file basically reiterates these details in the Jupyter section.
### Neo4j
In the docker-compose file I specify various details for building the Neo4j container, first specifying the image and container name:

``` yml
services:
  neo4j:
    image: neo4j:4.2.3-enterprise
    container_name: "neo-gds"
```

The next portion specifying volumes to load into the neo4j container is commented out. This is because an earlier version of the project used a different method for uploading the data into the server, which will be explained later. It is left as context and is instructive as to how to switch to a different method of loading the data.

``` yml
    #Commented out as it is no longer needed, but shows how to specify volumes for Neo4j to access directly
    #volumes: Commented out as is no longer needed
      #- ./sh_nw:/data
      #- ./sh_nw:/var/lib/neo4j/import
```

Lastly, I specify a few important options for the container:

``` yml
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_AUTH=neo4j/1234
      - NEO4JLABS_PLUGINS=["apoc", "graph-data-science"]
      - apoc.import.file.enabled=true
      - apoc.export.file.enabled=true
      - apoc.export.json.all=true
      # Adjust memory settings as needed
    networks:
      - neo_net
```

I specify and open ports for the database, specify authorization information for the database, and load a few plugins- `graph-data-science` provides some analysis tools and `apoc` (Awesome Procedures on Cypher) which allows for better communication between Python and Neo4j.

Lastly, in the docker-compose we give both neo4j and jupyterlab access to the `neo_net` to allow them to communicate.

The full docker system can be visualized simply as:

``` mermaid
flowchart TB;
    subgraph Container
    direction LR
    A[(Neo4j)]<--> |CYPHER| B[Jupyter Notebook]
    end
    C(Docker) --> |CONTAINS| Container
```

## How to run the system

[Watch the project video here](https://youtu.be/2khlbcsMUuQ)

- Let's start by navigating to the directory for the project:

``` shell
> cd $GIT_ROOT/sorrentum_sandbox/spring2024/SorrTask816_graph_data_loading_and_querying_with_neo4j
```

- Now lets build the container- this could take a minute or two:

``` shell
> docker-compose build

[+] Building 0.0s (0/0)  docker:default
2024/05/08 18:43:08 http2: server: error reading preface from client //./pipe/docker_engine: file has already been close[+] Building 1.0s (15/15) FINISHED                                                                       docker:default
 => [jupyterlab internal] load build definition from Dockerfile                                                    0.0s
 => => transferring dockerfile: 747B                                                                               0.0s
 => [jupyterlab internal] load metadata for docker.io/jupyter/datascience-notebook:latest                          0.8s
 => [jupyterlab auth] jupyter/datascience-notebook:pull token for registry-1.docker.io                             0.0s
 => [jupyterlab internal] load .dockerignore                                                                       0.0s
 => => transferring context: 2B                                                                                    0.0s
 => [jupyterlab 1/9] FROM docker.io/jupyter/datascience-notebook:latest@sha256:476c6e673e7d5d8b5059f8680b1c6a9889  0.0s
 => [jupyterlab internal] load build context                                                                       0.0s
 => => transferring context: 1.32MB                                                                                0.0s
 => CACHED [jupyterlab 2/9] RUN echo "c.NotebookApp.token = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.  0.0s
 => CACHED [jupyterlab 3/9] RUN echo "c.NotebookApp.password = ''" >> /home/jovyan/.jupyter/jupyter_notebook_conf  0.0s
 => CACHED [jupyterlab 4/9] COPY requirements.txt ./                                                               0.0s
 => CACHED [jupyterlab 5/9] RUN pip install -U pip                                                                 0.0s
 => CACHED [jupyterlab 6/9] RUN pip install --no-cache-dir -r requirements.txt                                     0.0s
 => [jupyterlab 7/9] COPY --chown=1000:100 ./notebooks /home/jovyan/work/analysis                                  0.0s
 => [jupyterlab 8/9] COPY --chown=1000:100 ./sh_nw /home/jovyan/work/data                                          0.0s
 => [jupyterlab 9/9] WORKDIR /home/jovyan/work                                                                     0.0s
 => [jupyterlab] exporting to image                                                                                0.0s
 => => exporting layers                                                                                            0.0s
 => => writing image sha256:9385c2749566ea684f94080c4faa5704ff23680a3919861fb889fe85859a83bb                       0.0s
 => => naming to docker.io/library/sorrtask816_graph_data_loading_and_querying_with_neo4j-jupyterlab               0.0s
```

- Now let's start the containers in the background:

``` shell
> docker-compose up -d
[+] Running 3/0
 ✔ Network sorrtask816_graph_data_loading_and_querying_with_neo4j_neo_net         Created                          0.0s
 ✔ Container neo-gds                                                              Created                          0.0s
 ✔ Container sorrtask816_graph_data_loading_and_querying_with_neo4j-jupyterlab-1  Created                          0.0s
```

- You can take a look at the containers which are running:

``` shell
> docker ps
CONTAINER ID   IMAGE                                                               COMMAND                  CREATED              STATUS                        PORTS                                                      NAMES
f46aca6eb164   sorrtask816_graph_data_loading_and_querying_with_neo4j-jupyterlab   "tini -g -- jupyter …"   About a minute ago   Up About a minute (healthy)   0.0.0.0:8888->8888/tcp                                     sorrtask816_graph_data_loading_and_querying_with_neo4j-jupyterlab-1
6da806df6f13   neo4j:4.2.3-enterprise                                              "/sbin/tini -g -- /d…"   About a minute ago   Up About a minute             0.0.0.0:7474->7474/tcp, 7473/tcp, 0.0.0.0:7687->7687/tcp   neo-gds
```

- Okay, now that everything is up and running, navigate to the Jupyter Notebook environment at <http://localhost:8888/>
- Once there, navigate to the sidebar and open the notebook `analysis/upload_data.ipynb`
- Take a quick look at the information at the top of the notebook-
  - *The Marvel Comics character collaboration graph:*
    - For this demonstrative project, we will be using graph data from *The Marvel Comics character collaboration graph* originally constructed by Cesc Rosselló, Ricardo Alberich, and Joe Miro from the University of the Balearic Islands. The data pulls from Marvel's superhero comic books, linking hero's to the stories they appear in. While this is obviosuly a non-serious use, it is still demonstraive of the capabilties of a dockerized environment for doing data analysis on graph data.
  - *The Uploading Code*
    - We use the py2neo python package to interact with the server. In the code below we define and then call functions to read our relevant data into python, then use py2neo to communicate with the server, making queries to create our intended graph structure. Also notice that before calling the nodes or relationships function, that we first create index specifications for the server. We do this because index values can be matched much more efficiently, helping speed up the uploading process.
- Now let's start uploading our data to the Neo4j server. Again, keep in mind this will take around 5 minutes or so, depending on the capabilities of your system.
- *Optional:* If you'd like to interact directly with the Neo4j interface, you can navigate to http://localhost:7474/ and sign in with username: neo4j and password: 1234
- Now, with the data loaded into the Neo4j database, we can do some analysis. In jupyter notebook open the data analysis notebook at `analysis/data_analysis.ipynb`
- You can go through the notebook, running each of the cells and describing what they do. In short, we complete some basic data analysis and visualization using CYPHER queries of the database and python analysis tools. Findings include:
  - Number of nodes and edges broken down by type
  - Which heroes appear most commonly
  - Captain America's social network
  - Which heroes appear together most commonly
- And that's it! We've demonstrated a functional system for uploading to and interacting with a Neo4j database in a Dockerized environment. To shut down the environment, navigate back to your terminal and execute:

``` shell
> docker-compose down
[+] Running 3/3
 ✔ Container sorrtask816_graph_data_loading_and_querying_with_neo4j-jupyterlab-1  Removed                                                                                                                   1.3s
 ✔ Container neo-gds                                                              Removed                                                                                                                   5.5s
 ✔ Network sorrtask816_graph_data_loading_and_querying_with_neo4j_neo_net         Removed                                                                                                                   0.2s
```

## Detailed Project Description

Now let's get into a little more detail into how our Python scripts are working.

### The Dataset

For the project we use *The Marvel Comics character collaboration graph* originally constructed by Cesc Rosselló, Ricardo Alberich, and Joe Miro-Julia from the University of the Balearic Islands, for the writing of their paper *[Marvel Universe looks almost like a real social network](https://arxiv.org/abs/cond-mat/0202174)* which demonstrates that the Marvel Universe collaboration network shares many commonalities with real-life networks. They pulled the data from [The Marvel Chronology Project](https://www.chronologyproject.com/) which is a project cataloging all appearances of significant Marvel characters in chronological order.

The dataset is composed of all Marvel comic published since November 1961 and the heroes which appear in them. The dataset can be modeled by a graph in 1 of two ways:
1. Nodes composed solely of hero's with edges connecting them representing comics in which both heroes appear. 2 different nodes may have numerous edges (comics) connecting them.
2. Heroes and Comics are both nodes, with edges connecting heroes to the comics they appeared in. Thus, co-appearances between heroes are now path's of length 2, going through some comic node.

I chose to use the latter as I was interested in looking at both networks of comics and heroes.

### Uploading the data

*Please note that the code below is ordered slightly differently than the actual script for sake of clarity in writing*

There are 2 approaches we could use to upload our data to the database. Either we can read our data into Python and have Python communicate with Neo4j instructions as to how to use that Python data. The option is to communicate with Python to the database where to access the relevant data from the file system available to the database and read in the data directly. I chose the former approach because after testing both, initially reading into Python led to faster upload times.

We start by setting our CD correctly, importing a few necessary packages, and connecting to out Neo4j database:

``` python
%cd /home/jovyan/work
from py2neo import Graph, Node, Relationship, NodeMatcher
import csv
import time

# Connect to the Neo4j database
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "1234"))
```

Uploading data into the Neo4j database is composed of essentially 3 steps:
1. First, we initialize indexes for both comic and hero nodes. We do this because using indexes rather than attribute matching greatly increases the efficiency uploading nodes later:

``` python
# Create indexes
start_time = time.time()
graph.run("CREATE INDEX ON :hero(name)")
graph.run("CREATE INDEX ON :comic(name)")
index_creation_time = time.time() - start_time
print(f"Index creation time: {index_creation_time:.2f} seconds")
```

2.  Next, we upload our node data, of both `type = comic` and `type = hero` to the database. To do so we read the relevant `nodes.csv` into python and run through each row, using the py2neo package to communicate with the database to create new nodes of either type comic or hero and name it corresponding to the columns in the csv:

``` python
# Function to create nodes
def create_nodes_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            node = Node(row['type'], name=row['node'])
            graph.create(node)

# Upload nodes from nodes.csv
start_time = time.time()
create_nodes_from_csv("data/nodes.csv")
node_creation_time = time.time() - start_time
print(f"Node creation time: {node_creation_time:.2f} seconds")
```

3.  Lastly, we connect nodes based off the data in `edges.csv`. Again, we read the data into python, iterate row by row and communicate with Neo4j to create an edge by matching a comic node in the database by index `name = comic_name` from the CSV column 'comic' to a hero node in the database by index with `name = hero_name` from the csv column 'hero'.

``` python
# Function to create relationships
def create_relationships_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hero_name = row['hero']
            comic_name = row['comic']
            hero = NodeMatcher(graph).match("hero", name=hero_name).first()
            comic = NodeMatcher(graph).match("comic", name=comic_name).first()
            if hero and comic:
                relationship = Relationship(hero, "APPEARS_IN", comic)
                graph.create(relationship)

# Upload relationships from edges.csv
start_time = time.time()
create_relationships_from_csv("data/edges.csv")
relationship_creation_time = time.time() - start_time
print(f"Relationship creation time: {relationship_creation_time:.2f} seconds")
```

Reiterating the schema described earlier, the database now has loaded our network data like:

``` mermaid
graph LR;
    A(Hero) -->|APPEARS_IN| B(Comic)
    C(Comic) -->|STARS| D(Hero)
```

Nodes of the same time are never connected, so graphs like:

``` mermaid
graph LR;
    A(Hero) --> B(Hero)
    C(Comic) -->D(Comic)
```

are not possible. Technically, within Neo4j all edges are stored as directed edges, so in our case all edges are like:

``` mermaid
graph LR;
    A(Hero) -->|APPEARS_IN| B(Comic)
```

however they can easily be treated as undirected when querying the database.

*For reference, note the output of the code above in my system:*

``` output
/home/jovyan/work 
Index creation time: 0.08 seconds 
Node creation time: 31.44 seconds 
Relationship creation time: 246.91 seconds
```

### Data Analysis

#### Setup and Overview

We start by importing some packages and setting our connection to the database:

``` python
from py2neo import Graph
import time
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import itertools

# Connect to the Neo4j database
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "1234"))
```

Next, we do some simple CYPHER queries which retrieve some basic overview of our data: how many edges we have, how many nodes, and how many of each type:

``` python
# Count nodes
total_nodes_count = graph.evaluate("MATCH (n) RETURN count(n)")
hero_nodes_count = graph.evaluate("MATCH (n:hero) RETURN count(n)")
comic_nodes_count = graph.evaluate("MATCH (n:comic) RETURN count(n)")

print(f"Total nodes count: {total_nodes_count}")
print(f"Hero nodes count: {hero_nodes_count}")
print(f"Comic nodes count: {comic_nodes_count}")

# Count edges
total_edges_count = graph.evaluate("MATCH ()-[r]->() RETURN count(r)")
print(f"Total edges count: {total_edges_count}")
```

We'll also quickly create a simple function which runs our CYPHER queries and times them, as a demonstration of the speed of doing such queries.

``` python
# Function to execute a Cypher query and measure execution time
def execute_query(query):
    start_time = time.time()
    result = graph.run(query).data()
    end_time = time.time()
    completion_time = end_time - start_time
    return result, completion_time
```

#### Graph Analysis

*Please note that in this section code is abbreviated for brevity, showing queries and new code only.*

First we'll take a look at which heroes appeared in the most comics. This is a pretty simply CYPHER query, just counting the number of relationships each node has and returning the 20 highest. Then we print the results:

``` python
# Find the nodes of type 'hero' with the most connections
query = """
MATCH (hero:hero)--(connected)
RETURN hero.name AS hero_name, COUNT(connected) AS connection_count
ORDER BY connection_count DESC
LIMIT 20
"""
```

``` output
Heroes with the most comic book appearances:
   1. Hero: CAPTAIN AMERICA, Comic Count: 1334
   2. Hero: IRON MAN/TONY STARK, Comic Count: 1150
   3. Hero: THING/BENJAMIN J. GR, Comic Count: 963
   4. Hero: THOR/DR. DONALD BLAK, Comic Count: 956
   5. Hero: HUMAN TORCH/JOHNNY S, Comic Count: 886
   6. Hero: MR. FANTASTIC/REED R, Comic Count: 854
   7. Hero: HULK/DR. ROBERT BRUC, Comic Count: 835
   8. Hero: WOLVERINE/LOGAN, Comic Count: 819
   9. Hero: INVISIBLE WOMAN/SUE, Comic Count: 762
   10. Hero: SCARLET WITCH/WANDA, Comic Count: 643
   11. Hero: BEAST/HENRY &HANK& P, Comic Count: 635
   12. Hero: DR. STRANGE/STEPHEN, Comic Count: 631
   13. Hero: WATSON-PARKER, MARY, Comic Count: 622
   14. Hero: DAREDEVIL/MATT MURDO, Comic Count: 619
   15. Hero: HAWK, Comic Count: 605
   16. Hero: VISION, Comic Count: 603
   17. Hero: CYCLOPS/SCOTT SUMMER, Comic Count: 585
   18. Hero: WASP/JANET VAN DYNE, Comic Count: 581
   19. Hero: JAMESON, J. JONAH, Comic Count: 577
   20. Hero: ANT-MAN/DR. HENRY J., Comic Count: 561
Execution time: 0.13 seconds
```

Next, we'll do some deeper investigation into the most popular hero by total appearances: Captain America. Looking again at how many appearances he has, how many different hero's he's appeared with, and which hero's he's appeared with most often. The new queries involve finding second-order connections but otherwise don't require any new techniques:

1.  How many nodes is 'CAPTAIN AMERICA' connected to

``` python
query1 = """
MATCH (ca:hero {name: 'CAPTAIN AMERICA'})--(connected)
RETURN count(DISTINCT connected) AS connected_nodes_count
"""
```

``` output
1. 'CAPTAIN AMERICA' is appears in 1334 comics
   Execution time: 0.04 seconds
```

2.  How many unique nodes are connected to nodes which are connected to 'CAPTAIN AMERICA'

``` python
query2 = """
MATCH (ca:hero {name: 'CAPTAIN AMERICA'})--(connected)--(connected_to_connected)
WHERE connected <> connected_to_connected
RETURN count(DISTINCT connected_to_connected) AS unique_connected_nodes_count
"""
```

``` output
2. There are 1918 unique heroes which have appeared in the same comic as Captain America.
   Execution time: 0.08 seconds
```

3.  What nodes appear most frequently in the second order connections

``` python
query3 = """
MATCH (ca:hero {name: 'CAPTAIN AMERICA'})--(connected)--(connected_to_connected)
WHERE connected <> connected_to_connected
WITH connected_to_connected, COUNT(connected_to_connected) AS freq
RETURN connected_to_connected.name AS node, freq
ORDER BY freq DESC
LIMIT 20
"""
```

``` output
3. Captain America's Most Frequent Collaborators:
   1. Hero: IRON MAN/TONY STARK, Co-Appearances: 440
   2. Hero: VISION, Co-Appearances: 385
   3. Hero: THOR/DR. DONALD BLAK, Co-Appearances: 380
   4. Hero: WASP/JANET VAN DYNE, Co-Appearances: 376
   5. Hero: SCARLET WITCH/WANDA, Co-Appearances: 373
   6. Hero: HAWK, Co-Appearances: 319
   7. Hero: ANT-MAN/DR. HENRY J., Co-Appearances: 289
   8. Hero: JARVIS, EDWIN, Co-Appearances: 246
   9. Hero: WONDER MAN/SIMON WIL, Co-Appearances: 215
   10. Hero: FALCON/SAM WILSON, Co-Appearances: 189
   11. Hero: HERCULES [GREEK GOD], Co-Appearances: 183
   12. Hero: SHE-HULK/JENNIFER WA, Co-Appearances: 172
   13. Hero: THING/BENJAMIN J. GR, Co-Appearances: 170
   14. Hero: BEAST/HENRY &HANK& P, Co-Appearances: 169
   15. Hero: MR. FANTASTIC/REED R, Co-Appearances: 167
   16. Hero: QUICKSILVER/PIETRO M, Co-Appearances: 164
   17. Hero: HUMAN TORCH/JOHNNY S, Co-Appearances: 162
   18. Hero: SUB-MARINER/NAMOR MA, Co-Appearances: 159
   19. Hero: FURY, COL. NICHOLAS, Co-Appearances: 156
   20. Hero: INVISIBLE WOMAN/SUE, Co-Appearances: 151
   Execution time: 0.06 seconds
```

#### Graph visualization

Finally, to demonstrate pulling data from the database for visualization, we'll do a couple more examples. First, let's just make an example of what a small portion of the network looks like. To do so, we'll look again at Captain America, a few comics he appears in, and all the other heroes he appears with in those comics. To do so, we'll query the database for 3 random primary connections with Captain America and all the node those three are connected to. Then we'll use the NetworkX to do some visualization in Python:

    query_random_nodes = """
    MATCH (ca:hero {name: 'CAPTAIN AMERICA'})--(connected)
    WITH connected, rand() AS random
    ORDER BY random
    LIMIT 3
    MATCH (connected)--(connected_to_connected)
    RETURN connected.name AS node, connected_to_connected.name AS connected_node
    """
    G = execute_query(query_random_nodes)

    pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_edges(G, pos)
    plt.show()

*Please see actual resulting visualization in the data_analysis.ibynb*

``` mermaid
mindmap
  root(Captain America)
    ((Comic_1))
        [Hero_1]
        [Hero_2]
        [Hero_3]
    ((Comic_2))
        [Hero_4]
        [Hero_5]
        [Hero_6]
        [Hero_7]
    ((Comic_3))
        [Hero_8]
        [Hero_9]
```

As another example for visualization we'll look at the 20 most common heroes again, investigating which of them are in the same comics most often.

``` python
# Retrieve the top heroes
top_heroes = [record['hero_name'] for record in result]

# Count connections between pairs of heroes through intermediate nodes
hero_pairs_connections = {}

for hero1, hero2 in itertools.combinations(top_heroes, 2):
    query_connections_between_heroes = f"""
    MATCH path = (hero1:hero {{name: '{hero1}'}})-[*2]-(hero2:hero {{name: '{hero2}'}})
    WHERE length(path) = 2
    RETURN count(path) AS connection_count
    """

G = execute_query(query_connections_between_heroes)

# Visualize the graph with node labels smaller and weights distinguished by color
# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, node_size=500)
nx.draw_networkx_edges(G, pos)

# Draw edges with colors based on weights
for edge, weight in nx.get_edge_attributes(G, 'weight').items():
    nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=cmap(weight / 10), width=2)

plt.axis('off')
plt.show()

# Find the top 5 pairs by weight
top_pairs = sorted(hero_pairs_connections.items(), key=lambda x: x[1], reverse=True)[:5]
```

*Please see resulting visualization in the data_analysis.ibynb*

``` output
Top 5 Hero Pairs by Connection Count:
THING/BENJAMIN J. GR - HUMAN TORCH/JOHNNY S: 724 connections
HUMAN TORCH/JOHNNY S - MR. FANTASTIC/REED R: 694 connections
THING/BENJAMIN J. GR - MR. FANTASTIC/REED R: 690 connections
MR. FANTASTIC/REED R - INVISIBLE WOMAN/SUE: 682 connections
HUMAN TORCH/JOHNNY S - INVISIBLE WOMAN/SUE: 675 connections
```

This concludes my project on using Neo4j and Jupyter Notebook in a Dockerized environment.

## Original Project Description

Install and configure AllegroGraph, and create a Python script to load graph data into the database. Define a simple graph schema and insert sample data representing entities and relationships. Use AllegroGraph's SPARQL endpoint to execute basic graph queries and retrieve information from the database. Explore and present an innovative project.
## Works Cited

<?xml version="1.0"?>
<div class="csl-bib-body" style="line-height: 2; padding-left: 1em; text-indent:-1em;">
  <div class="csl-entry">Alberich, R., et al. <i>Marvel Universe Looks Almost like a Real Social Network</i>. 2002, https://doi.org/10.48550/ARXIV.COND-MAT/0202174.</div>
  <div class="csl-entry">Conjeaud, Marius. &#x201C;Py2neo Is End-of-Life &#x2013; A Basic Migration Guide.&#x201D; <i>Graph Database &amp; Analytics</i>, 3 Nov. 2023, https://neo4j.com/developer-blog/py2neo-end-migration-guide/.</div>
  <div class="csl-entry">Jensen, Daron. <i>Marvel Chronology Project</i>. https://www.chronologyproject.com/. Accessed 10 May 2024.</div>
  <div class="csl-entry">Terrill, Gavin. &#x201C;Neo4j - an Embedded, Network Database.&#x201D; <i>InfoQ</i>, 5 June 2008, https://www.infoq.com/news/2008/06/neo4j/.</div>
</div>
