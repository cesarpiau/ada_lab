#!/usr/bin/env python
import pika, sys, os, redis, json

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='antifraude')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [x] Received {data['conta']}")

    channel.basic_consume(queue='antifraude', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)