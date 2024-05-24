#!/usr/bin/env python
import datetime, pika, os, redis, json, logging, sys
from datetime import timedelta
from minio import Minio

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def main():
    # ABERTURA DE CONEXÃO COM O RABBITMQ E DECLARAÇÃO DA FILA
    rabbitmq_host = os.environ['RABBITMQ_HOST']
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='antifraude')

    # ABERTURA DE CONEXÃO COM O CACHE REDIS
    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0, health_check_interval=10)
    r = redis.Redis(connection_pool=redis_pool)

    # ABRE A CONEXÃO COM O SERVIÇO MINIO
    global client, bucket
    minio_endpoint = os.environ['MINIO_ENDPOINT']
    minio_access_key = os.environ['MINIO_ROOT_USER']
    minio_secret_key = os.environ['MINIO_ROOT_PASSWORD']
    client = Minio(endpoint=minio_endpoint, secure=False, access_key=minio_access_key, secret_key=minio_secret_key)
    bucket = 'relatorios'
    
    # CRIAR O BUCKET CASO ELE AINDA NÃO EXISTA
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    # FUNÇÃO DE CALLBACK PARA TRATAR AS MENSAGENS RETIRADAS DA FILA DE ANTI-FRAUDE
    def callback(ch, method, properties, body):
        message = json.loads(body)
        conta = str(message['conta'])

        # ACIONA O MOTOR ANTI-FRAUDE CASO NÃO SEJA A PRIMEIRA TRANSAÇÃO PARA A CONTA
        if not r.exists(conta):
            r.lpush(conta, json.dumps(message))
            r.expire(conta, 30)
        else:
            motorAntiFraude(conta, message)
            r.lpush(conta, json.dumps(message))
            r.expire(conta, 30)

    # FUNÇÃO DO MOTOR ANTI-FRAUDE
    def motorAntiFraude(conta, message):
        # RETIRA A TRANSAÇÃO ANTERIOR DO CACHE E CARREGA O JSON
        ultimaTransacao = json.loads(r.lindex(conta, 0))
        
        # DEFINE A VARIÁVEL COM TEMPO MÍNIMO TOLERADO PARA TRANSAÇÕES EM DIFERENTES UF
        mintimediff = timedelta(hours=2)

        msgTransacaoRecebida = " [?] Transação Recebida: " + json.dumps(message)
        print(f'\n{msgTransacaoRecebida}')

        # SE A TRANSAÇÃO RECEBIDA OCORREU EM UF DIFERENTE DA TRANSAÇÃO ANTERIOR, CALCULA O TEMPO ENTRE AS DUAS 
        if ultimaTransacao['uf'] != message['uf']:
            dataanterior = datetime.datetime.strptime(ultimaTransacao['timestamp'], '%Y-%m-%dT%H:%M:%S')
            dataatual = datetime.datetime.strptime(message['timestamp'], '%Y-%m-%dT%H:%M:%S')
            timediff = dataatual - dataanterior
            
            # SE O TEMPO ENTRE AS TRANSAÇÕES FOR MENOR QUE O MÍNIMO, A TRANSAÇÃO É CONSIDERADA FRAUDE
            if timediff < mintimediff:
                msgTransacaoAnterior = " [A] Transação Anterior: " + json.dumps(ultimaTransacao)
                print(msgTransacaoAnterior)
                resultado = " [!] FRAUDE [!] UF Diferente - Diferença de Horário: " + str(timediff)
                print(resultado)
                
                # A TRANSAÇÃO CO SUSPEITA DE FRAUDE VAI PARA O RELATÓRIO LOCAL
                atualizarRelatorio(conta, msgTransacaoRecebida, msgTransacaoAnterior, resultado)
     
    # FUNÇÃO QUE VERIFICA SE EXISTE O OBJETO NO BUCKET
    def objectExists(bucket, object):
        try:
            client.get_object(bucket, object)
            return True
        except:
            return False
    
    # FUNÇÃO QUE ALIMENTA O ARQUIVO DO RELATÓRIO DE FRAUDE
    def atualizarRelatorio(conta, msgTransacaoRecebida, msgTransacaoAnterior, resultado):
        objeto = f'{conta}.txt'
        
        # RECUPERAR O RELATÓRIO DO BUCKET CASO ELE EXISTA
        if objectExists(bucket, objeto):
            client.fget_object(bucket, objeto, objeto)

        # INCLUIR A NOVA TRANSAÇÃO
        f = open(objeto, "a")
        f.write(f'{msgTransacaoRecebida}\n')
        f.write(f'{msgTransacaoAnterior}\n')
        f.write(f'{resultado}\n\n')
        f.close()

        # ENVIA O NOVO RELATORIO PARA O BUCKET
        client.fput_object(bucket, objeto, objeto, 'text/plain')
        os.remove(objeto)

    # ABRE O CANAL COM A FILA E COMEÇA A RETIRAR AS MENSAGENS
    channel.basic_consume(queue='antifraude', on_message_callback=callback, auto_ack=True)
    print(' [*] Aguardando Mensagens...')
    channel.start_consuming()

main()
# if __name__ == '__main__':
#     try:
#         main()
#     except:
#         os._exit(1)