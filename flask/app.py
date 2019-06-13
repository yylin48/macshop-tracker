# -*- coding:utf8 -*-
import os, json, time, datetime, logging
from pymongo import MongoClient
from flask import (Flask, make_response, render_template, jsonify)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def connect_mongo():
    client = MongoClient('database',27017)
    db = client['test']
    return db

@app.route('/show')
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