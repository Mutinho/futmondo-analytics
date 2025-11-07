#!/usr/bin/env python3
"""
Script de prueba para verificar las credenciales de Futmondo
"""

import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

email = os.getenv("FUTMONDO_EMAIL")
password = os.getenv("FUTMONDO_PASSWORD")

print(f"📧 Email: {email}")
print(f"🔐 Password: {'*' * len(password) if password else 'NOT SET'}")

if not email or not password:
    print("❌ Error: FUTMONDO_EMAIL o FUTMONDO_PASSWORD no están configurados")
    exit(1)

login_data = {
    "header": {
        "token": None,
        "userid": ""
    },
    "query": {
        "mail": email,
        "pwd": password
    },
    "answer": {}
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=utf-8',
    'Origin': 'https://app.futmondo.com',
    'Referer': 'https://app.futmondo.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}

url = "https://api.futmondo.com/5/login/with_mail"

print(f"\n🌐 URL: {url}")
print(f"📦 Request data: {json.dumps(login_data, indent=2)}")

try:
    response = requests.post(url, json=login_data, headers=headers, timeout=10)
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    
    data = response.json()
    
    if data.get("answer", {}).get("error"):
        error_code = data.get('answer', {}).get('code', 'Unknown')
        print(f"\n❌ Login failed: {error_code}")
        print("\n💡 Posibles causas:")
        print("   1. Email o contraseña incorrectos")
        print("   2. La cuenta no existe")
        print("   3. La cuenta está bloqueada o inactiva")
        print("\n✅ Acciones recomendadas:")
        print("   1. Verifica tus credenciales en https://app.futmondo.com")
        print("   2. Prueba hacer login manualmente en el navegador")
        print("   3. Verifica que no haya espacios en el email o contraseña")
    else:
        print("\n✅ ¡Login exitoso!")
        if "mobile" in data.get("answer", {}):
            token = data["answer"]["mobile"].get("token", "")
            userid = data["answer"]["mobile"].get("userid", "")
            print(f"   Token: {token[:20]}..." if token else "   Token: NO ENCONTRADO")
            print(f"   User ID: {userid}")
            
except Exception as e:
    print(f"\n❌ Error: {e}")

