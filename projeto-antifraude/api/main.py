import requests, json
from datetime import timedelta
from flask import Flask, Response
from minio import Minio

app = Flask(__name__)

# ABRE A CONEXÃO COM O SERVIÇO
client = Minio('minio:9000', secure=False, access_key='guest', secret_key='guestguest')
bucket = 'relatorios'
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
    objectList = client.list_objects(bucket)
    return objectList


def get_relatorio_minio(object_id):
    url = client.presigned_get_object(bucket, object_id, expires=timedelta(hours=2))
    return url

@app.route("/relatorios", methods=["GET"])
def get_lista_relatorios():
    objectList = get_lista_relatorios_minio()
    listJson = []
    for o in objectList:
        objectJson = {"arquivo":""+o.object_name+"","tamanho":o.size,"ultima-alteracao":""+str(o.last_modified)+""}
        listJson.append(objectJson)
    return Response(json.dumps(listJson), mimetype="application/json")
    
@app.route("/relatorios/<object_id>", methods=["GET"])
def get_relatorio(object_id):
    url = get_relatorio_minio(object_id)
    urlJson = {"link":""+url+""}
    return Response(json.dumps(urlJson), mimetype="application/json")

@app.route("/health", methods=["GET"])
def healthcheck():
    try:
        health = requests.get('http://minio:9000/minio/health/live')
        status = health.status_code
        if status == 200:
            return Response(response=json.dumps({"status":"healthy"}), status=200)
        else:
            return Response(response=json.dumps({"status":"unhealthy"}), status=500)
    except:
        return Response(response=json.dumps({"status":"unhealthy"}), status=500)