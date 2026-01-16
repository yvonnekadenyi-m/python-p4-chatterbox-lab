
from app import app
from models import db, Message

with app.app_context():  # <-- app context ensures SQLAlchemy knows the app
    # Clear existing messages
    db.session.query(Message).delete()

    # Add sample messages
    messages = [
        Message(body="Hello, World!", username="Ian"),
        Message(body="Flask + React is fun!", username="Jacklyne")
    ]

    db.session.add_all(messages)
    db.session.commit()
    print("Seeded the database!")