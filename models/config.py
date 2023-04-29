from flask import Flask
from models.database import db, init_db

app = Flask(__name__)
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()

if __name__ == '__main__':
    app.run(debug=True)