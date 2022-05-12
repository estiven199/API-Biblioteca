import os
import sys
import certifi
import pymongo
import authentication
from bson import ObjectId
from flask import jsonify, request
from jsonschema import validate

user_mongo = os.environ.get('user_mongo')
pass_mongo = os.environ.get('pass_mongo')
cluster_mongo = os.environ.get('cluster_mongo')

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

    def more_filters_per_field(self, fields, field_='', val=True):
        show_fields = {}
        data = fields.split(',')
        if val:
            [show_fields.update({field: "1"})
             for field in data if field != '']
            if len(show_fields) > 0:
                val = self.validation_fields(show_fields)
                if val != True:
                    return {'error': val}
            return show_fields
        else:
            return [{field_: field}
                    for field in data if field != '']

    def search_in_base_data_interna(self,args):
        show_fields = {}
        extra_param = []
        response = []
        for i in args:
            if i == "id":
                extra_param.append({"_id": ObjectId(args[i])})
            elif i == 'fields':
                show_fields = self.more_filters_per_field(args[i])
                if 'error' in show_fields.keys():
                    print(show_fields['error'])
                show_fields = {k: int(v) for k, v in show_fields.items()}
            else:
                categoria = self.more_filters_per_field(args[i], field_=i, val=False)
                if len(categoria) > 1:
                    filter1 = extra_param.append({'$or': categoria})
                else:
                    extra_param.append(categoria[0])
        if len(show_fields) > 0:
            cursor = db_base.books.find({'$and': extra_param}, show_fields)
        else:
            cursor = db_base.books.find({'$and': extra_param})
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            doc['fuente'] = 'interna'
            response.append(doc)
        return response

    def validation_fields(self, json):
        try:
            validate(instance=json, schema=self.schema)
            return True
        except Exception as e:
            e = sys.exc_info()[1]
            return e.args[0]

    def validations(self, headers):
        val = auth.login(db_base, headers)
        if val != True:
            return '', jsonify(val)
        args = request.args
        args = args.to_dict(flat=True)
        val = self.validation_fields(args)
        if val != True:
            return '', jsonify(val)
        return db_base, args
