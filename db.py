from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    """Initialize database tables when the app starts."""
    db.create_all()
