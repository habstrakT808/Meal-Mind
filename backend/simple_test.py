from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

@app.route('/')
def hello():
    return "Hello from Meal Mind!"

@app.route('/api/test')
def test():
    return jsonify({"message": "API working!", "status": "success"})

@app.route('/api/db-test')
def db_test():
    try:
        db.create_all()
        return jsonify({"message": "Database connection working!", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"})

if __name__ == '__main__':
    app.run(debug=True)