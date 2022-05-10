import base64
from flask import request

class oauth:
    def __init__(self):
        self.fields_obligatory = ['private_key_id','private_key','client_id']

    def login(self,db,headers):
        private_key_id = headers['private_key_id']
        private_key = headers['private_key']
        if set(headers) != set(self.fields_obligatory) or type(private_key_id) != bytes :
            return {'code':'500','message': 'Server error'}    
        inf_user = db.users.find_one({'client_id':headers['client_id']})
        if len(inf_user):
            return {'code':'401','message': 'Unauthorized'}  
        if inf_user['private_key_id'] != base64.b64encode(private_key_id.encode("utf-8")) or inf_user['private_key'] != private_key:
            return {'code':'401','message': 'Unauthorized'}  
        return True

        