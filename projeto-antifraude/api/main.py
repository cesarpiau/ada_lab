import requests, json
from flask import Flask, jsonify, Response
from minio import Minio

app = Flask(__name__)

# ABRE A CONEXÃO COM O SERVIÇO
client = Minio('minio:9000', secure=False, access_key='guest', secret_key='guestguest')
bucket = 'relatorios'

def get_lista_relatorios_minio():
    objectList = client.list_objects(bucket)
    return objectList


def get_relatorio_minio(object_id):
    object = client.get_object(bucket, object_id)
    return object

@app.route("/relatorios", methods=["GET"])
def get_lista_relatorios():
    objectList = get_lista_relatorios_minio()
    listJson = []
    for o in objectList:
        obj_nome = o.object_name
        obj_tamanho = o.size
        obj_data = o.last_modified
        listJson.insert(f'"arquivo":"{obj_nome}","tamanho":"{obj_tamanho}","ultima-alteracao":"{obj_data}"')
    return json.dumps(listJson)
    
@app.route("/relatorios/<object_id>", methods=["GET"])
def get_relatorio(object_id):
    object = get_relatorio_minio(object_id)
    obj_nome = object.object_name
    obj_tamanho = object.size
    obj_data = object.last_modified
    objectJson = f'"arquivo":"{obj_nome}","tamanho":"{obj_tamanho}","ultima-alteracao":"{obj_data}"'
    return json.dumps(objectJson)

@app.route("/health", methods=["GET"])
def healthcheck():
    try:
        health = requests.get('https://minio:9000/minio/health/live')
        status = health.status_code
        if status == 200:
            return Response(jsonify({"status":"healthy"}), status=200)
        else:
            return Response(jsonify({"status":"unhealthy"}), status=500)
    except:
        return Response(jsonify({"status":"unhealthy"}), status=500)