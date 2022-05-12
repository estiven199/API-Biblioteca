# API-Biblioteca

https://api-biblioteca-43tleytuxq-uc.a.run.app/


Para la base de datos se utiliza mongodb. Se utiliza el framework flask. Se integro developer.nytimes.com/ como el segundo servicio de busqueda de libros.Se desplego la API en Google Cloud.La url para el consumo del API es 
https://api-biblioteca-43tleytuxq-uc.a.run.app/ 
LA API solo permite tres tipos de peticiones. GET, PUT y DELETE.Para ingresar se requiere de credenciales tales como:

private_key_id = '919cHQP24ba466147b8@c0651bdc0b08fc-7469104FG2a7fnhgJYTf5821gvfnjhdh.*'
headers = {
"client_id": "10682011758309545974085",
"private_key_id": base64.b64encode(private_key_id.encode("utf-8")),
"private_key": "nMIIEvggIBADANyBgkqhpkiG9w0BlAQE"
}

La private_key_id  es obligatorio ser codificarla con base64.

GET

Campos permitidos:'id',titulo','subtitulo','autor','categoria','fecha_publicacion','editor','descripcion' ,'fields'
Aspectos a considerar:
Para buscar varias categorias y/o autores es necesario enviarlos en string separados por coma asi:
'Philosophy,body' ***
El campo fields es opcional y se usa para indicar que campos del reponse quieres ver. 
'titulo,subtitulo' ***
Si busca por id no require de mas campos.
El formato de busqueda de la fecha es 'YYYY-MM-DD' "2020-12-21"

Ejemplo.

import json

import base64

import requests

payload = 'api-biblioteca-43tleytuxq-uc.a.run.app/api/v1/books'

private_key_id = '919cHQP24ba466147b8@c0651bdc0b08fc-7469104FG2a7fnhgJYTf5821gvfnjhdh.*'

headers = 
"client_id": "10682011758309545974085","
private_key_id": base64.b64encode(private_key_id.encode("utf-8")),
"private_key": "nMIIEvggIBADANyBgkqhpkiG9w0BlAQE"
}

params = {
'fields':'titulo,subtitulo',
"editor":"Random",
'autor':'Gabriel'
}

request = requests.get(url=payload,headers=headers,params=params).text

r = json.loads(request)

PUT

Se necesita el id externa y la fuente

params = {   'id':"0812992857",   'fuente':'nytimes'}r
request = requests.put(url=payload,headers=headers,params=params).text
r = json.loads(request)

DELETE 
Sencesite del id de la base de datos, no de la fuente externa
params = {   'id':"627d803deae7040aec22ba0d"}
request = requests.delete(url=payload,headers=headers,params=params).text
r = json.loads(request)

*** Estos campos solo afectan cuando las busqyueda es en la base de datos interna
