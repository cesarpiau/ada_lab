#!/usr/bin/env python
import datetime, pika, sys, os, redis, json, uuid
from datetime import timedelta
from minio import Minio

def main():
    # ABERTURA DE CONEXÃO COM O RABBITMQ E DECLARAÇÃO DA FILA
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='antifraude')

    # ABERTURA DE CONEXÃO COM O CACHE REDIS
    r = redis.Redis(host='localhost', port=6379, db=0)

    # DEFINIÇÃO DA VARIÁVEL GLOBAL COM O NOME ÚNICO DO ARQUIVO DE RELATÓRIO PARA A EXECUÇÃO
    global arquivo
    arquivo =  f'{str(datetime.date.today())}_{str(uuid.uuid4())}.txt'

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
                criarRelatorio(msgTransacaoRecebida, msgTransacaoAnterior, resultado)
     
    # FUNÇÃO QUE ALIMENTA O ARQUIVO LOCAL DO RELATÓRIO DE FRAUDE
    def criarRelatorio(msgTransacaoRecebida, msgTransacaoAnterior, resultado):
        f = open(arquivo, "a")
        f.write(f'{msgTransacaoRecebida}\n')
        f.write(f'{msgTransacaoAnterior}\n')
        f.write(f'{resultado}\n\n')
        f.close()

    # ABRE O CANAL COM A FILA E COMEÇA A RETIRAR AS MENSAGENS
    channel.basic_consume(queue='antifraude', on_message_callback=callback, auto_ack=True)
    print(' [*] Aguardando Mensagens. Para sair, pressione CTRL+C')
    channel.start_consuming()

# FUNÇÃO QUE COPIA O RELATÓRIO PARA O SERVIÇO DE OBJECT STORE
def salvarRelatorio():
    # ABRE A CONEXÃO COM O SERVIÇO
    client = Minio('127.0.0.1:9000', secure=False, access_key='guest', secret_key='guestguest')
    bucket = 'relatorios'
    
    # CRIAR O BUCKET CASO ELE AINDA NÃO EXISTA
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    
    # ENVIA O ARQUIVO PAR O BUCKET, GERA LINK ASSINADO PARA DOWNLOAD E REMOVE O ARQUIVO LOCAL
    client.fput_object(bucket, arquivo, arquivo)
    url = client.get_presigned_url("GET", bucket, arquivo, expires=timedelta(hours=2))
    print(f'[v] Link para download do relatório: {url}')
    os.remove(arquivo)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # O RELATÓRIO É ENVIADO PARA O OBJECT STORE APÓS O USUÁRIO INTERROMPER O CONSUMO NA FILA
        print('[*] Consumidor Interrompido. Salvando relatório...')
        salvarRelatorio()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)