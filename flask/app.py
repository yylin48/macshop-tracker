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

########
# CRUD #
########

@app.route('/show', methods=['GET'])
def show():
    db = connect_mongo()
    collection = 'user_list'
    user = db[collection].find()
    lis = []
    for item in user:
        if item['is_delete'] == False:
            obj = {
                'name' : item['name'],
                'keyword' : item['keyword'],
                'url' : item['url'],
                'line_id' : item['line_id']
            }
            lis.append(obj)
    res = {"data":lis}

    return jsonify(res)

@app.route('/add', methods=['POST'])
@jwt_required
def add():
    
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    post_list = ['name', 'keyword', 'url', 'line_id']
    for item in post_list:
        if not request.json.get(item, None):
            return jsonify({"msg": "Missing parameter"}), 400
    
    db = connect_mongo()
    collection = 'user_list'
    #軟刪除
    query1 = {'line_id':request.json.get('line_id'), 'is_delete':True}
    #存在
    query2 = {'line_id':request.json.get('line_id'), 'is_delete':False}
    if db[collection].count(query2) == 1:
        return jsonify({"msg": "line_id is existed"}), 400
    #資料庫有 但是軟刪除 改用update方式
    if db[collection].count(query1) == 1:
        new_obj = { 
            "$set" : {
                'name' : request.json.get('name'), 
                'keyword' : request.json.get('keyword'), 
                'url' : request.json.get('url'), 
                'line_id' : request.json.get('line_id'),
                'is_delete' : False
            }
        }
        db[collection].update_one(query1, new_obj)
        return jsonify({"msg": "success"}), 200
    obj = {
        'name' : request.json.get('name', None), 
        'keyword' : request.json.get('keyword', None), 
        'url' : request.json.get('url', None), 
        'line_id' : request.json.get('line_id', None),
        'is_delete' : False
    }
    db[collection].insert_one(obj)
    return jsonify({"msg": "success"}), 200

@app.route('/delete/<line_id>', methods=['DELETE'])
@jwt_required
def delete(line_id):
    
    db = connect_mongo()
    collection = 'user_list'

    if db[collection].count({'line_id':line_id}) == 0:
        return jsonify({"msg": "line_id is not existed"}), 400
    query = {'line_id' : line_id }
    newvalues = { "$set": { "is_delete": True } }
    db[collection].update_one(query, newvalues)
    return jsonify({"msg": "success"}), 200

@app.route('/update/<line_id>', methods=['PUT'])
@jwt_required
def update():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    post_list = ['name', 'keyword', 'url', 'line_id']
    for item in post_list:
        if not request.json.get(item, None):
            return jsonify({"msg": "Missing parameter"}), 400

    db = connect_mongo()
    collection = 'user_list'
    if db[collection].count({'line_id':line_id}) == 0:
        return jsonify({"msg": "line_id is not existed"}), 400
    query = {'line_id' : line_id }
    new_obj = { 
        "$set" : {
            'name' : request.json.get('name'), 
            'keyword' : request.json.get('keyword'), 
            'url' : request.json.get('url'), 
            'line_id' : request.json.get('line_id'),
        }
    }
    db[collection].update_one(query, new_obj)
    return jsonify({"msg": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=5000)