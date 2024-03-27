from flask import Flask, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host="redis", port=6379, db=0)

def set_key(key, value):
    r.set(key,value)

def get_key(key):
    return r.get(key)

@app.route("/set/<key>/<value>", methods=["GET"])
def set_key_value(key, value):
    set_key(key, value)
    return jsonify({"msg":"key set"})

@app.route("/get/<key>", methods=["GET"])
def get_key_value(key):
    value = get_key(key)
    if value is None:
        return jsonify({"msg":"key not found"})
    else:
        return jsonify({"msg":value.decode("utf-8")})

@app.route("/health", methods=["GET"])
def healthcheck():
    return jsonify({"msg":"serviço saudável"})