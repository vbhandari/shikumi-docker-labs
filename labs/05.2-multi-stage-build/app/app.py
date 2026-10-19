import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def root():
    return jsonify(
        message="hello v2",
        greeting=os.getenv("GREETING", "none"),
    )

@app.get("/healthz")
def healthz():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
