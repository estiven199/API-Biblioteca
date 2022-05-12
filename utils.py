import os
import sys
import json
import certifi
import pymongo
import requests
import collections
import authentication
from bson import ObjectId
from flask import jsonify, request
from jsonschema import validate

user_mongo = os.environ.get('user_mongo')
pass_mongo = os.environ.get('pass_mongo')
cluster_mongo = os.environ.get('cluster_mongo')
api_key = os.environ.get('api_key')


ca = certifi.where()
conn = pymongo.MongoClient("mongodb+srv://{}:{}@{}.mongodb.net/retryWrites=true&w=majority".format(
    user_mongo, pass_mongo, cluster_mongo), tlsCAFile=ca)

db_base = conn['library']
auth = authentication.oauth()


class utils:
    def __init__(self):
        self. schema = {
            "type": "object",
            "additionalProperties": False,
            'properties': {
                'id': {'type': 'string'},
                'titulo': {"type": "string"},
                'subtitulo': {'type': 'string'},
                'autor': {'type': 'string'},
                'categoria': {'type': 'string'},
                'fecha_publicacion': {'type': 'string'},
                'editor': {'type': 'string'},
                'descripcion': {'type': 'string'},
                'fields': {'type': 'string'},
            }
        }
        self.schema_put = {
            "type": "object",
            "additionalProperties": False,
            'properties': {
                'id': {'type': 'string'},
                'fuente': {"type": "string", "enum": ["google", "nytimes"]},
            },
            "required": [
                "id",
                "fuente",
            ]
        }

        self.schema_delete = {
            "type": "object",
            "additionalProperties": False,
            'properties': {
                'id': {'type': 'string'},
            },
            "required": [
                "id",
            ]
        }
        self.urls = {"google": {'GET': 'https://www.googleapis.com/books/v1/volumes?q=+',
                                'PUT': 'https://www.googleapis.com/books/v1/volumes/'},
                     "nytimes": {'GET': 'https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json?api-key=' + api_key + '&',
                                 'PUT': 'https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json?api-key=' + api_key + '&'}
                     }

    def complete_json(self, json_, keys):
        required_fields = ['id', 'titulo', 'subtitulo', 'autor', 'categoria',
                           'fecha_publicacion', 'editor', 'descripcion', 'imagen']
        keys = [key for key in json_.keys()]
        missing_fields = set(required_fields) - set(keys)
        for key in missing_fields:
            json_.update({key: ''})
        return dict(collections.OrderedDict(sorted(json_.items())))

    def equivalence_fields_filter(self, source):
        json = {
            "google": {
                "titulo": "intitle",
                "autor": "inauthor",
                "categoria": "subject",
                "fecha_publicacion": "publishedDate",
                "editor": "inpublisher"},
            "nytimes": {
                "titulo": "title",
                "autor": "author",
                "categoria": "title",
                "fecha_publicacion": "title",
                "editor": "publisher"}}
        return json[source]

    def equivalence_fields_json(self, source):
        json = {
            "google": {
                "id": "id",
                "title": "titulo",
                "authors": "autor",
                "categories": "categoria",
                "descripcion": "descripcion",
                "publishedDate": "fecha_publicacion",
                "publisher": "editor",
                "imageLinks": "imagen"},
            "nytimes": {
                "isbns": "id",
                "title": "titulo",
                "author": "autor",
                "description": "descripcion",
                "created_date": "fecha_publicacion",
                "publisher": "editor",
                "book_image": "imagen"

            }}
        return json[source]

    def json_google(self, r):
        keys = ['title', 'authors', 'categories', 'descripcion',
                'publisher', 'publishedDate', 'imageLinks', 'id']
        json_keys = self.equivalence_fields_json('google')
        responsive = []
        for books in r['items']:
            json_ = {}
            books['volumeInfo']['id'] = books['id']
            for key in books['volumeInfo'].keys():
                if key in keys:
                    json_.update({json_keys[key]: books['volumeInfo'][key]})
                    json_['fuente'] = 'google'
                    responsive.append(self.complete_json(json_, keys))
            return responsive

    def json_nytimes(self, r):
        keys = ['title', 'author', 'description', 'publisher',
                'created_date', 'book_image', 'isbns']
        json_keys = self.equivalence_fields_json('nytimes')
        responsive = []
        for books in r['results']:
            json_ = {}
            for key in books.keys():
                if key in keys:
                    json_.update({json_keys[key]: books[key]})
                    json_['fuente'] = 'nytimes'
                    responsive.append(self.complete_json(json_, keys))
        return responsive

    def more_filters_per_field(self, fields, field_='', val=True):
        show_fields = {}
        data = fields.split(',')
        if val:
            [show_fields.update({field: "1"})
             for field in data if field != '']
            if len(show_fields) > 0:
                val = self.validation_fields(show_fields,requ='GET')
                if val != True:
                    return {'error': val}
            return show_fields
        else:
            return [{field_: field}
                    for field in data if field != '']

    def search_in_base_data_interna(self, args):
        show_fields = {}
        extra_param = []
        response = []
        for i in args:
            if i == "id":
                try:
                    extra_param.append({"_id": ObjectId(args[i])})
                except Exception as e:
                    e = sys.exc_info()[1]
                    return e.args[0]
            elif i == 'fields':
                show_fields = self.more_filters_per_field(args[i])
                if 'error' in show_fields.keys():
                    return show_fields['error']
                show_fields = {k: int(v) for k, v in show_fields.items()}
            else:
                filter_1 = self.more_filters_per_field(
                    args[i], field_=i, val=False)
                if len(filter_1) > 1:
                    extra_param.append({'$or': filter_1})
                else:
                    extra_param.append(filter_1[0])
        if len(show_fields) > 0:
            cursor = db_base.books.find({'$and': extra_param}, show_fields)
        else:
            cursor = db_base.books.find({'$and': extra_param})
        for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            doc['fuente'] = 'interna'
            dict(collections.OrderedDict(sorted(doc.items())))
            response.append(doc)
        return response

    def search_in_(self, args, fuente, req='GET'):
        json_keys = self.equivalence_fields_filter(fuente)
        filter_string = ''
        if req == 'GET':
            if fuente == 'google':
                s = ":"
                l = "+"
            else:
                s = "="
                l = "&"
            for k, v in args.items():
                if k != 'fields':
                    if fuente == 'google':
                        v = v.replace(' ', '+')
                    if len(filter_string) > 1:
                        filter_string += l+json_keys[k] + s + v
                    else:
                        filter_string += json_keys[k] + s + v
        else:
            if fuente == 'google':
                filter_string = args['id']
            else:
                filter_string = 'isbn='+args['id']
        url = self.urls[fuente][req]
        request = requests.get(url=url+filter_string).text
        r = json.loads(request)
        if 'totalItems' in r.keys() and r['totalItems']:
            return self.json_google(r)
        if 'volumeInfo' in r.keys():
            r['items'] = [r]
            return self.json_google(r)
        if 'results' in r.keys() and len(r['results']) > 0:
            return self.json_nytimes(r)
        if 'errors' in r.keys():
            return {'error': r['errors']}
        return 'Error in the process'

    def validation_fields(self, json, requ):
        try:
            if requ == 'GET':
                validate(instance=json, schema=self.schema)
            elif requ == 'PUT':
                validate(instance=json, schema=self.schema_put)
            else:
                validate(instance=json, schema=self.schema_delete)    
            return True
        except Exception as e:
            e = sys.exc_info()[1]
            return e.args[0]

    def validations(self, headers, requ='GET'):
        val = auth.login(db_base, headers)
        if val != True:
            return '', jsonify(val)
        args = request.args
        args = args.to_dict(flat=True)
        val = self.validation_fields(args, requ)
        if val != True:
            return '', jsonify(val)
        return db_base, args
