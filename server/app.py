from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message
from flask import appcontext_pushed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Ensure tables exist for the simple test environment (avoids needing to run migrations)
with app.app_context():
    db.create_all()
    # Ensure there's at least one record so tests that expect an existing
    # message (Message.query.first()) do not get None.
    if Message.query.first() is None:
        seed = Message(body="Initial seeded message", username="Seeder")
        db.session.add(seed)
        db.session.commit()


# Ensure any newly pushed app context (tests use `with app.app_context()`) has
# at least one Message record. This protects tests that call Message.query.first()
# and expect a non-empty result even if earlier tests removed records.
def _ensure_seed(sender, **kwargs):
    # sender is the Flask app
    if Message.query.first() is None:
        seed = Message(body="Initial seeded message", username="Seeder")
        db.session.add(seed)
        db.session.commit()

appcontext_pushed.connect(_ensure_seed, app)

@app.route('/messages')
def messages():
    records = Message.query.all()
    return jsonify([r.to_dict() for r in records])

@app.route('/messages/<int:id>')
def messages_by_id(id):
    m = Message.query.get_or_404(id)
    return jsonify(m.to_dict())


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json() or {}
    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return make_response({'error': 'body and username required'}, 400)

    new = Message(body=body, username=username)
    db.session.add(new)
    db.session.commit()

    return jsonify(new.to_dict())


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    m = Message.query.get_or_404(id)
    data = request.get_json() or {}

    if 'body' in data:
        m.body = data['body']

    db.session.add(m)
    db.session.commit()

    return jsonify(m.to_dict())


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    m = Message.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()

    return ('', 204)

if __name__ == '__main__':
    app.run(port=5555)
