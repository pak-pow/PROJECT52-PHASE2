import sqlite3
import click #type: ignore
from flask import current_app, g #type: ignore


def get_db():
    """Open a new database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row  # rows behave like dicts
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Read schema.sql and apply it to the database."""
    db = get_db()
    
    # NEW: Try migrating the existing table before running schema.sql
    # so that the INSERT statements in schema.sql don't fail due to a missing column.
    try:
        db.execute("ALTER TABLE projects ADD COLUMN featured INTEGER DEFAULT 0;")
        db.commit()
    except sqlite3.OperationalError:
        pass  # Table does not exist yet (new DB) or column already exists

    with current_app.open_resource("data/schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    db.commit()


@click.command("init-db")
def init_db_command():
    """CLI command: flask init-db — creates tables and seeds data."""
    init_db()
    click.echo("Database initialised.")


def init_app(app):
    """Register db helpers with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
