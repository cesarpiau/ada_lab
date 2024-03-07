import datetime
import requests
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

ip = "200.201.175.8"
url = f'https://ipinfo.io/{ip}/geo'

now = datetime.datetime.now()

if r.exists(ip):
    geo = r.get(ip)
    tempo = datetime.datetime.now() - now
else:
    response = requests.request('GET', url)
    if response.status_code < 300:
        r.set(ip, response.text)
        r.expire(ip, 30)
        geo = response.text
        tempo = datetime.datetime.now() - now
print(geo)
print(f'Tempo de Execução: '+str(tempo))