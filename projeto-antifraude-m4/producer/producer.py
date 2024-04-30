import os, json, pika, time
from minio import Minio
 
def main():
    # ABERTURA DE CONEXÃO COM O RABBITMQ
    rabbitmq_host = os.environ['RABBITMQ_HOST']
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    # ABRE A CONEXÃO COM O SERVIÇO MINIO
    global client, bucket
    minio_endpoint = os.environ['MINIO_ENDPOINT']
    minio_access_key = os.environ['MINIO_ROOT_USER']
    minio_secret_key = os.environ['MINIO_ROOT_PASSWORD']
    client = Minio(endpoint=minio_endpoint, secure=False, access_key=minio_access_key, secret_key=minio_secret_key)
    bucket = 'transacoes'
        
    # CRIAR O BUCKET CASO ELE AINDA NÃO EXISTA
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    # DECLARA A FILA DE TRANSAÇÕES E DEFINE A PROPRIEDADE DAS MENSAGENS NA FILA DE TRANSAÇÕES
    channel.queue_declare(queue='transacoes')
    prop_transacoes = pika.BasicProperties(content_type="application/json")

    # DECLARA A FILA DE ANTI-FRAUDE E DEFINE AS PROPRIEDADES DAS MENSAGENS NA FILA DE TRANSAÇÕES
    channel.queue_declare(queue='antifraude')
    prop_antifraude = pika.BasicProperties(expiration="30000",content_type="application/json")

    # FUNÇÃO QUE LISTA OS ARQUIVOS DE TRANSAÇÕES NO BUCKET E OS ENVIA PARA PROCESSAMENTO
    def processar_lista_relatorios_minio():
        if client.bucket_exists(bucket):
            objectList = client.list_objects(bucket)
            for o in objectList:
                object = client.get_object(bucket, o.object_name)
                print(" [!] Processando arquivo: "+o.object_name)
                enviar_transacoes(object)
        else:
            print(" [!] Nenhum arquivo encontrado. Próxima execução em 1 minuto.")

    # FUNÇÃO QUE TRATA OS ARQUIVOS DE TRANSAÇÕES E ENVIA PARA A FILA
    def enviar_transacoes(arquivo_transacoes):
        # CARREGA O ARQUIVO COMO UM OBJETO JSON
        data = json.loads(arquivo_transacoes.data)

        # ITERAÇÃO PARA CAPTURAR ENVIAR AS MENSAGENS DO ARQUIVO PARA AS FILAS DE TRANSAÇÕES E ANTI-FRAUDE
        for i in data:
            message = json.dumps(i)
            channel.basic_publish(exchange='', routing_key='transacoes', body=message, properties=prop_transacoes)
            channel.basic_publish(exchange='', routing_key='antifraude', body=message, properties=prop_antifraude)
            print(" [+] Transação Enviada: " + message)
            time.sleep(0.1)
    
    processar_lista_relatorios_minio()
    connection.close()

main()