#!/usr/bin/env python
import argparse
import datetime
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')


ap = argparse.ArgumentParser()
ap.add_argument("priority", nargs='?', default="0")
a = ap.parse_args()
priority = int(a.priority)

body = '{"msg":"Hello World!", "data":"' + str(datetime.datetime.now()) + '"}'
properties = pika.BasicProperties(expiration="10000",content_type="application/json",priority=priority)

channel.basic_publish(exchange='', routing_key='hello', body=body, properties=properties)
print(" [x] Sent " + body)
connection.close()