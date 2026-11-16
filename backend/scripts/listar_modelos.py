"""Lista los modelos de Gemini disponibles para tu API key. Ejecutar desde backend/:
   python scripts/listar_modelos.py
Copia el nombre (sin el prefijo "models/") en AI_MODEL o AI_FALLBACK_MODEL de backend/.env.
"""

import os
import sys

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    sys.exit("Falta GEMINI_API_KEY en backend/.env")

configurado = os.getenv("AI_MODEL", "gemini-3.8-flash")
nombres = []
cliente = genai.Client(api_key=api_key)  # se guarda para que la conexión siga abierta
for modelo in cliente.models.list():
    nombre = (modelo.name or "").removeprefix("models/")
    acciones = modelo.supported_actions or []
    if "gemini" in nombre and "generateContent" in acciones:
        nombres.append(nombre)

for nombre in sorted(set(nombres)):
    marca = "  <-- AI_MODEL actual" if nombre == configurado else ""
    print(nombre + marca)

if configurado not in nombres:
    print(f"\nOJO: '{configurado}' no aparece en la lista de tu cuenta.")