import json
import os
from bson import ObjectId
import certifi
import pymongo
import base64
import authentication 
from flask_cors import CORS
from flask import Flask, request ,jsonify
app =Flask(__name__)
CORS(app)
ca = certifi.where()
envmode = os.environ.get('envmode')
user_mongo = os.environ.get('user_mongo')
pass_mongo = os.environ.get('pass_mongo')
cluster_mongo = os.environ.get('cluster_mongo')

conn = pymongo.MongoClient("mongodb+srv://{}:{}@{}.mongodb.net/retryWrites=true&w=majority".format(user_mongo, pass_mongo,cluster_mongo), tlsCAFile=ca)
db_base = conn['library']
auth = authentication.oauth()

@app.route('/api/v1/books', methods=['GET'])
def books():
    if request.method == 'GET':
        headers = request.headers
        val = auth.login(db_base,headers)
        if val:
            args = request.args
            args.to_dict(flat=False)
            
            extra_param = []

            for i in args:
                print(i)
                if i == "id":
                    extra_param.append({"_id": ObjectId(args[i])})   
                elif i == 'fields':pass

                    # print(args[i])
                else:
                    extra_param.append({i: args[i]})    
            return args

if __name__ == '__main__':
    if envmode == 'prod':
        app.run(ssl_context='adhoc',host='0.0.0.0',port=80)
    app.run(debug=True,port=5000)    