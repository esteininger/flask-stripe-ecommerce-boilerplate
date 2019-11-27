from time import time
from flask import jsonify, request


def success_response(data, code=200):
    return jsonify({
        "ok": True,
        "code": code,
        "endpoint": request.path,
        "timestamp": time(),
        "response": data
    })


def error_response(msg, code=500):
    data = {
        "ok": False,
        "code": code,
        "timestamp": time(),
        "message": str(msg)
    }
    return jsonify(data), 500


def check_json(json, keys):
    for key in keys:
        if key not in json:
            return key
    return None
