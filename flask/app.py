# -*- coding:utf8 -*-
import os, json, time, datetime, logging
from pymongo import MongoClient
from flask import (Flask, make_response, render_template, jsonify, request)
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)

#setup 
app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] =  'Oa3La13adDLOsFPdg8924098713h98hfoiew'
#DB connect
def connect_mongo():
    client = MongoClient('database',27017)
    db = client['test']
    return db

########
# apis #
########

@app.route('/', methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/health', methods=['GET'])
def health_check():
    r = make_response(jsonify(health='Well done.'), 200)
    r.add_etag()
    return r

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'admin' or password != 'daisy':
        return jsonify({"msg": "Bad username or password"}), 401

    expires = datetime.timedelta(days = 1)
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username,expires_delta=expires)
    return jsonify(access_token=access_token), 200

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/show', methods=['GET'])
def show():
    db = connect_mongo()
    collection = 'user_list'
    user = db[collection].find()
    lis = []
    for item in user:
        obj = {
            'name' : item['name'],
            'category': item['category'],
            'keyword' : item['keyword'],
            'url' : item['url'],
            'line_id' : item['line_id']
        }
        lis.append(obj)
    res = {"data":lis}

    return jsonify(res)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=5000)