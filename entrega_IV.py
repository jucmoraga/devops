import uuid
import random
import requests

def peticiones(url: str):
    #Gereamos el token de acceso
    token = requests.post(f"{url}/v1/blacklists/token").json().get('token')

    #Generamos tipo de request (exitoso/malo)
    tipo_request = random.choice(['exitoso', 'malo'])

    #Definimos headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    if tipo_request == 'exitoso':
        #Generamos payload
        payload = {
            "email": f"user_{uuid.uuid4()}@example.com",
            "appId": str(uuid.uuid4()),
            "blockedReason": 'Suspected fraudulent activity'
        }

        #Realizamos la peticion POST para agregar a la blacklist
        requests.post(f"{url}/v1/blacklists", json = payload, headers = headers)

        #Realizamos la peticion GET para consultar el email agregado
        requests.get(f"{url}/v1/blacklists/{payload.get('email')}", headers = headers).json()
    
    else:
        #Generamos payload
        payload = {
            "email": f"user_{uuid.uuid4()}@example.com",
            "appId": str(uuid.uuid4()),
            "blockedReason": ''.join(['a'] * 300)
        }

        #Realizamos la peticion POST para agregar a la blacklist
        requests.post(f"{url}/v1/blacklists", json = payload, headers = headers)
    
    print(requests.get(f"{url}/v1/blacklists/health").json())

if __name__ == '__main__':
    #URL localhost
    url_local = 'http://localhost:5000'

    #URL del balanceador de carga
    url_cloud = 'http://elb-1891227252.us-east-1.elb.amazonaws.com'

    #Prueba de peticiones
    for _ in range(50): 
        peticiones(url_local)
        print(_)