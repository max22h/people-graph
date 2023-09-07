from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

# Define your Neo4j credentials and connection URI
uri = "bolt://localhost:7687"  # Replace with your Neo4j URI
username = "neo4j"  # Replace with your Neo4j username
password = "neo4jtest"  # Replace with your Neo4j password

# Create a Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to retrieve the graph data from Neo4j
def get_graph_data(tx):
    query = (
        "MATCH (p1:Person)-[r]->(p2:Person) "
        "RETURN p1.name AS source, type(r) AS relation, p2.name AS target"
    )
    result = tx.run(query)
    return [(record["source"], record["relation"], record["target"]) for record in result]

# Function to add a new node to Neo4j
def add_node(tx, name):
    query = "CREATE (p:Person {name: $name})"
    tx.run(query, name=name)

# Create a NetworkX graph
G = nx.Graph()

# Retrieve data from Neo4j and populate the NetworkX graph
with driver.session() as session:
    data = session.read_transaction(get_graph_data)
    for source, relation, target in data:
        G.add_node(source)
        G.add_node(target)
        G.add_edge(source, target, relation=relation)

# Function to handle node creation by clicking and dragging
def on_node_drag(event):
    if event.inaxes is not None and event.inaxes.get_navigate():
        if event.button == 1:
            # Left mouse button clicked
            new_node_data = create_new_node_dialog()
            if new_node_data:
                new_node_name, relation = new_node_data
                nearest_node = nearest_node_to_click(event.xdata, event.ydata)
                G.add_node(new_node_name)
                G.add_edge(nearest_node, new_node_name, relation=relation)
                update_plot()

# Function to create a dialog for entering the new node's name and relation
def create_new_node_dialog():
    fig, ax = plt.subplots()
    text_box1 = TextBox(ax, "Enter new node name:", initial="")
    text_box2 = TextBox(ax, "Enter relation:", initial="")
    plt.show()

    name = text_box1.text.strip()
    relation = text_box2.text.strip()
    
    return name, relation

# Find the nearest node to the click event
def nearest_node_to_click(x, y):
    pos = nx.spring_layout(G, seed=42)
    min_distance = float('inf')
    nearest_node = None
    for node, coordinates in pos.items():
        distance = ((coordinates[0] - x)**2 + (coordinates[1] - y)**2)**0.5
        if distance < min_distance:
            min_distance = distance
            nearest_node = node
    return nearest_node

# Function to update the plot
def update_plot():
    plt.clf()
    pos = nx.spring_layout(G, seed=42)
    labels = {node: node for node in G.nodes()}

    nx.draw(G, pos, with_labels=True, labels=labels, node_size=500, node_color="skyblue", font_size=10, font_color="black")
    edge_labels = nx.get_edge_attributes(G, 'relation')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color="red")
    plt.title("Neo4j Graph Visualization")
    plt.axis("off")
    plt.draw()

# Connect the interactive event handler
plt.gcf().canvas.mpl_connect("button_release_event", on_node_drag)

# Initial plot
update_plot()
plt.show()

# Close the Neo4j driver
driver.close()
