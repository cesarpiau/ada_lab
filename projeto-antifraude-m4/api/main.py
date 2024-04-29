import os, requests, json
from datetime import timedelta
from flask import Flask, Response
from minio import Minio

app = Flask(__name__)

# ABRE A CONEXÃO COM O SERVIÇO
minio_endpoint = os.environ['MINIO_ENDPOINT']
client = Minio(endpoint=minio_endpoint, secure=False, access_key='guest', secret_key='guestguest')
bucket = 'relatorios'

# CRIAR O BUCKET CASO ELE AINDA NÃO EXISTA
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
            "Resource": "arn:aws:s3:::"+bucket+"",
        },
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::"+bucket+"/*",
        },
    ],
}
client.set_bucket_policy(bucket, json.dumps(policy))

def get_lista_relatorios_minio():
    if client.bucket_exists(bucket):
        objectList = client.list_objects(bucket)
        return objectList
    else:
        return None

def get_relatorio_minio(object_id):
    if client.bucket_exists(bucket):
        object = client.get_object(bucket, object_id)
        object.release_conn()
        return object
    else:
        return None

@app.route("/relatorios", methods=["GET"])
def get_lista_relatorios():
    objectList = get_lista_relatorios_minio()
    if objectList is None:
        return Response(status=404)
    else:
        listJson = []
        for o in objectList:
            objectJson = {"arquivo":""+o.object_name+"","tamanho":o.size,"ultima-alteracao":""+str(o.last_modified)+""}
            listJson.append(objectJson)
        return Response(json.dumps(listJson), mimetype="application/json")
    
@app.route("/relatorios/<object_id>", methods=["GET"])
def get_relatorio(object_id):
    object = get_relatorio_minio(object_id)
    if object is None:
        return Response(status=404)
    else:
        return Response(object.data, mimetype="application/txt")

@app.route("/health", methods=["GET"])
def healthcheck():
    try:
        health = requests.get('http://minio:9000/minio/health/live')
        status = health.status_code
        if status == 200:
            return Response(response=json.dumps({"status":"healthy"}), status=200, mimetype="application/json")
        else:
            return Response(response=json.dumps({"status":"unhealthy"}), status=500, mimetype="application/json")
    except:
        return Response(response=json.dumps({"status":"unhealthy"}), status=500, mimetype="application/json")