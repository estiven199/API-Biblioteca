
import os
import utils
import pymongo
from bson import ObjectId
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)
envmode = os.environ.get('envmode')
utl = utils.utils()


@app.route('/api/v1/books', methods=['GET','PUT'])
def books():
    if request.method == 'GET':
        headers = request.headers
        database, args = utl.validations(headers)
        if type(database) != pymongo.database.Database:
            return args
        data_full = utl.search_in_base_data_interna(args) 
        if len(data_full) == 0:
            data_full_google = utl.search_in_(args,'google')
            if 'Error' in data_full_google:
                return data_full_google
            [data_full.append(item) for item in data_full_google if item['id'] != "" ]
            data_full_nytimes = utl.search_in_(args,'nytimes')
            [data_full.append(item) for item in data_full_nytimes if item['id'] != "" ]
        return jsonify(data_full)
    if request.method == 'PUT':
        headers = request.headers
        database, args = utl.validations(headers,'PUT')
        if type(database) != pymongo.database.Database:
            return args

        return(args)    


if __name__ == '__main__':
    if envmode == 'prod':
        app.run(ssl_context='adhoc', host='0.0.0.0', port=80)
    app.run(debug=True, port=5000)
