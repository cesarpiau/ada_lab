# Python program to read
# json file
 
import json
import pika
 
# Opening JSON file
f = open('transacoes.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)
 
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='transacoes')
prop_transacoes = pika.BasicProperties(content_type="application/json")

channel.queue_declare(queue='antifraude')
prop_antifraude = pika.BasicProperties(expiration="10000",content_type="application/json")

for i in data:
    channel.basic_publish(exchange='', routing_key='transacoes', body=str(i), properties=prop_transacoes)
    channel.basic_publish(exchange='', routing_key='antifraude', body=str(i), properties=prop_antifraude)
    print(" [x] Sent " + str(i))

connection.close()
f.close()