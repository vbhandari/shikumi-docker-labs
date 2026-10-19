import os
from pathlib import Path

import redis
from flask import Flask, abort, jsonify, request

app = Flask(__name__)
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    socket_connect_timeout=2,
)


def admin_token():
    path = Path(os.getenv("API_TOKEN_FILE", "/run/secrets/api_token"))
    return path.read_text().strip() if path.exists() else None


@app.get("/")
def root():
    return jsonify(
        message=os.getenv("MESSAGE", "hello from shikumi"),
        greeting=os.getenv("GREETING", "none"),
        hits=r.incr("hits"),
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/admin")
def admin():
    token = admin_token()
    if not token or request.headers.get("X-Admin-Token") != token:
        abort(401)
    return jsonify(admin="ok", hits=int(r.get("hits") or 0))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
