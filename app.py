from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)


uri = "bolt://localhost:7687"
username = "neo4j"
password = "neo4jtest"
driver = GraphDatabase.driver(uri, auth=(username, password))

def get_graph_data(tx):
    query = (
        "MATCH (p1:Person)-[r]->(p2:Person) "
        "RETURN p1.name AS source, type(r) AS relation, p2.name AS target"
    )
    result = tx.run(query)
    return [{"source": record["source"], "relation": record["relation"], "target": record["target"]} for record in result]

@app.route('/graph_data')
def graph_data():
    with driver.session() as session:
        data = session.read_transaction(get_graph_data)
    return jsonify(data)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
