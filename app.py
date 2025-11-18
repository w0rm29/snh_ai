import sqlite3
from flask import Flask, request

from . import db

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE="nodes.db"
    )
    
    db.init_app(app)
    
    def _build_tree(node_row):
        """
        Helper method that builds the tree from the child nodes
        node_row: a json entry to be added in the tree
        """
        children = db.get_children_db(node_row["id"])
        return {
            "id": node_row["id"],
            "label": node_row["label"],
            "children": [_build_tree(child) for child in children]
        }

    def _insert_tree(node, parent_id=None):
        """
        Helper method that recursively insert node and its children into the DB.
        node: dict with keys "id", "label", "children"
        parent_id: id of the parent node
        """
        node_id = node["id"]
        label = node["label"]

        db.create_node_db(node_id, label, parent_id)

        for child in node.get("children", []):
            _insert_tree(child, parent_id=node_id)
        
    
    @app.route("/", methods=['GET'])
    def welcome():
        return "<h1>Welcome to the app</h1>"


    @app.route("/api/tree", methods=['GET'])
    def get_all_trees():
        """
        Gets the full skeleton from the database
        """
        roots = db.get_root_nodes_db()
        tree = [_build_tree(root) for root in roots]
        return tree, 200


    @app.route("/api/tree", methods=['POST'])
    def create_node():
        """
        Creates a new node to the existing tree
        """
        data = request.get_json()
        if not data:
            return {"error": "JSON body required"}, 400

        try:
            _insert_tree(data)
        except sqlite3.IntegrityError:
            return {"error": "Node ID already exists"}, 400

        return {"message": "Tree inserted successfully"}, 201


    @app.teardown_appcontext
    def teardown_db(exception):
        """
        Closes the database connection
        """
        db.close_db(exception)

    return app

if __name__ == 'main':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)