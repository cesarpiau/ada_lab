#!/usr/bin/env python
import argparse
import datetime
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='fila_credito')
channel.queue_declare(queue='fila_cs')


ap = argparse.ArgumentParser()
ap.add_argument("-p", type=int, default="0", help="Número da prioridade da mensagem na fila")
ap.add_argument("-rk", type=str, default="hello", help="Routing Key da publicação da mensagem na fila")

a = ap.parse_args()

body = '{"msg":"Hello World!", "data":"' + str(datetime.datetime.now()) + '"}'
properties = pika.BasicProperties(expiration="60000",content_type="application/json",priority=a.p)

channel.basic_publish(exchange='', routing_key=a.rk, body=body, properties=properties)
print(" [x] Sent " + body)
connection.close()