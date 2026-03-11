from flask import Flask, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ.get("POSTGRES_DB", "flaskdb"),
        user=os.environ.get("POSTGRES_USER", "flaskuser"),
        password=os.environ.get("POSTGRES_PASSWORD", "flaskpass"),
    )


@app.route("/")
def home():
    return jsonify({"message":"ok"})

@app.route("/hello/<name>")
def hello(name):
    return jsonify({"message": f"Hello {name}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)