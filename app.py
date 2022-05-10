import os
import certifi
import pymongo
import base64
from flask import Flask
app =Flask(__name__)

ca = certifi.where()
envmode = os.environ.get('envmode')
user_mongo = os.environ.get('user_mongo')
pass_mongo = os.environ.get('pass_mongo')
cluster_mongo = os.environ.get('cluster_mongo')

conn = pymongo.MongoClient("mongodb+srv://{}:{}@{}.mongodb.net/retryWrites=true&w=majority".format(user_mongo, pass_mongo,cluster_mongo), tlsCAFile=ca)
db_configlobal = conn['library']





if __name__ == '__main__':
    if envmode == 'prod':
        app.run(ssl_context='adhoc',host='0.0.0.0',port=80)
    app.run(debug=True,port=5000)    