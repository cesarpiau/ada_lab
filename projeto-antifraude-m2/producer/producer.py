import json, pika, time
 
# ABRE O ARQUIVO COM A MASSA DE TESTES DE TRANSAÇÕES
f = open('transacoes.json')
 
# CARREGA O ARQUIVO COM UM OBJETO JSON
data = json.load(f)

# ABERTURA DE CONEXÃO COM O RABBITMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# DECLARA A FILA DE TRANSAÇÕES E DEFINE A PROPRIEDADE DAS MENSAGENS NA FILA DE TRANSAÇÕES
channel.queue_declare(queue='transacoes')
prop_transacoes = pika.BasicProperties(content_type="application/json")

# DECLARA A FILA DE ANTI-FRAUDE E DEFINE AS PROPRIEDADES DAS MENSAGENS NA FILA DE TRANSAÇÕES
channel.queue_declare(queue='antifraude')
prop_antifraude = pika.BasicProperties(expiration="30000",content_type="application/json")

# ITERAÇÃO PARA CAPTURAR ENVIAR AS MENSAGENS DO ARQUIVO PARA AS FILAS DE TRANSAÇÕES E ANTI-FRAUDE
for i in data:
    message = json.dumps(i)
    channel.basic_publish(exchange='', routing_key='transacoes', body=message, properties=prop_transacoes)
    channel.basic_publish(exchange='', routing_key='antifraude', body=message, properties=prop_antifraude)
    print(" [+] Transação Enviada: " + message)
    time.sleep(0.1)

connection.close()
f.close()