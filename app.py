from flask import Flask, render_template, request, redirect, url_for
from py2neo import Graph

app = Flask(__name__)

graph = Graph("bolt://neo4j_container:7687", auth=("neo4j", "test1234"))

@app.route("/")
def home():
    results = graph.run("MATCH (n)-[r]->(m) RETURN n, r, m").data()
    return render_template("index.html", results=results)

@app.route("/insert_data", methods=['POST'])
def insert_data():
    person = request.form['person']
    connections = request.form.getlist('connection')
    connection_names = request.form.getlist('connection_name')
    graph.run(f"CREATE (n:Person {{name: '{person}'}})")
    for conn, conn_name in zip(connections, connection_names):
        graph.run(f"MATCH (a:Person {{name: '{person}'}}), (b:Person {{name: '{conn}'}}) CREATE (a)-[:{conn_name}]->(b)")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

