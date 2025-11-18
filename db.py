import sqlite3
import click
from flask import current_app, g


def get_db():
    """
    Gets database instance
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    """
    Initialises the databse
    """
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def create_node_db(id, label, parent_id):
    db = get_db()
    db.execute(
        "INSERT INTO nodes (id, label, parent_id) VALUES (?, ?, ?)",
        (id, label, parent_id)
    )
    db.commit()


def get_node_db(node_id):
    db = get_db()
    return db.execute(
        "SELECT id, label, parent_id FROM nodes WHERE id = ?",
        (node_id,)
    ).fetchone()


def get_children_db(parent_id):
    db = get_db()
    return db.execute(
        "SELECT id, label, parent_id FROM nodes WHERE parent_id = ?",
        (parent_id,)
    ).fetchall()


def get_root_nodes_db():
    db = get_db()
    return db.execute(
        "SELECT id, label FROM nodes WHERE parent_id IS NULL"
    ).fetchall()
