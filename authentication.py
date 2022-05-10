import base64
from flask import request

class oauth:
    def __init__(self):
        self.fields_obligatory = ['Private-Key', 'Private-Key-Id', 'Client-Id']

    def login(self,db,headers):
        fields_request = [key for key in headers.keys() if key in self.fields_obligatory ]
        if set(fields_request) != set(self.fields_obligatory) :
            return {'code':'500','message': 'Server error'} 
        private_key_id = bytes(headers['Private-Key-Id'],encoding = "utf-8")
        private_key_id = base64.b64decode(private_key_id).decode("utf-8")
        private_key = headers['Private-Key'] 
        inf_user = db.users.find_one({'client_id':headers['Client-Id']})
        
        if len(inf_user) == 0:
            return {'code':'400','message': 'Unauthorized'}  
        print(inf_user['private_key'])
        print(private_key)
        if inf_user['private_key_id'] != private_key_id or inf_user['private_key'] != private_key:
            return {'code':'401','message': 'Unauthorized'}  
        return True

        