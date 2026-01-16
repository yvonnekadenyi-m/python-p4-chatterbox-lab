
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize the app with the db
db.init_app(app)
migrate = Migrate(app, db)

# Your routes go here
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{
        'id': msg.id,
        'body': msg.body,
        'username': msg.username,
        'created_at': msg.created_at,
        'updated_at': msg.updated_at
    } for msg in messages])

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    new_message = Message(
        body=data['body'],
        username=data['username']
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        'id': new_message.id,
        'body': new_message.body,
        'username': new_message.username,
        'created_at': new_message.created_at,
        'updated_at': new_message.updated_at
    }), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    data = request.get_json()
    message.body = data['body']
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    })

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    db.session.delete(message)
    db.session.commit()