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
prop_antifraude = pika.BasicProperties(expiration="30000",content_type="application/json")

for i in data:
    message = json.dumps(i)
    channel.basic_publish(exchange='', routing_key='transacoes', body=message, properties=prop_transacoes)
    channel.basic_publish(exchange='', routing_key='antifraude', body=message, properties=prop_antifraude)
    print(" [x] Sent " + message)

connection.close()
f.close()