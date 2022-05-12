
import os
import utils
import pymongo
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)
envmode = os.environ.get('envmode')
utl = utils.utils()


@app.route('/api/v1/books', methods=['GET','PUT','DELETE'])
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
            print(data_full_nytimes)
            [data_full.append(item) for item in data_full_nytimes if item['id'] != "" ]
        return jsonify(data_full)
    elif request.method == 'PUT':
        headers = request.headers
        database, args = utl.validations(headers,'PUT')
        if type(database) != pymongo.database.Database:
            return args
        json_ = utl.search_in_(args,args['fuente'],'PUT')
        if type(json_) == str and'error' in json_.keys():
            return jsonify(json_)
        json_ = json_[-1]  
        del json_['id']
        del json_['fuente']
        database.books.insert_one(json_)
        json_['id'] = str(json_['_id'])
        del json_['_id']
        return jsonify(json_)  
    elif request.method == 'DELETE':  
        print(2525)    
        return ''

if __name__ == '__main__':
    if envmode == 'prod':
        app.run(ssl_context='adhoc', host='0.0.0.0', port=80)
    app.run(debug=True, port=5000)
