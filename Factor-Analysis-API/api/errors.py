from flask import Flask, jsonify
from app import app

app = Flask(__name__)

@app.errorhandler(404)
def invalid_route(errors):
    output = {"error":
              {"msg": "404 error: This route is currently not supported. See API documentation."}
              }
    resp = jsonify({'result': output})
    return resp