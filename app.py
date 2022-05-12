
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


@app.route('/api/v1/books', methods=['GET'])
def books():
    if request.method == 'GET':
        headers = request.headers
        database, args = utl.validations(headers)
        if type(database) != pymongo.database.Database:
            return args
        # extra_param, show_fields = utl.choose_extra_param(args)
        # if extra_param == 'error':
        #     return show_fields

        # data = database.books.find()

        return jsonify(args)


if __name__ == '__main__':
    if envmode == 'prod':
        app.run(ssl_context='adhoc', host='0.0.0.0', port=80)
    app.run(debug=True, port=5000)
