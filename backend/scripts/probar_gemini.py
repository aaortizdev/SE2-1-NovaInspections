"""Prueba la API key de Gemini (cierra S2-00). Ejecutar desde backend/.

Uso:
  python scripts/probar_gemini.py                       # 1) la key funciona (solo texto)
  python scripts/probar_gemini.py muestra.png           # 2) acepta imágenes
  python scripts/probar_gemini.py etiqueta.pdf          # 3) acepta PDF
  python scripts/probar_gemini.py muestra.png --cajas   # 4) devuelve cajas box_2d 0-1000

Requiere:  pip install google-genai python-dotenv
Lee GEMINI_API_KEY y AI_MODEL de backend/.env (ver .env.example).
"""

import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROMPT_CAJAS = (
    "Localiza el recuadro de información nutricional (o el elemento más grande con texto). "
    "Responde SOLO un JSON: una lista con un objeto "
    '{"label": "...", "box_2d": [ymin, xmin, ymax, xmax]} '
    "con las coordenadas normalizadas de 0 a 1000."
)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("AI_MODEL", "gemini-3.8-flash")

    if not api_key:
        sys.exit("Falta GEMINI_API_KEY en backend/.env")

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pide_cajas = "--cajas" in sys.argv

    contenido: list = ["Responde solo con la palabra OK."]
    config = None

    if args:
        ruta = Path(args[0])
        mime = mimetypes.guess_type(ruta.name)[0]
        if mime not in {"application/pdf", "image/png", "image/jpeg"}:
            sys.exit("Usa un archivo .pdf, .png o .jpg")
        pregunta = PROMPT_CAJAS if pide_cajas else "Describe en una frase qué muestra este archivo."
        contenido = [types.Part.from_bytes(data=ruta.read_bytes(), mime_type=mime), pregunta]
        if pide_cajas:
            config = types.GenerateContentConfig(response_mime_type="application/json")

    cliente = genai.Client(api_key=api_key)
    print(f"Modelo: {modelo}")

    try:
        respuesta = cliente.models.generate_content(model=modelo, contents=contenido, config=config)
    except Exception as error:  # noqa: BLE001 - queremos ver el mensaje completo del proveedor
        sys.exit(f"FALLÓ la llamada: {error}")

    print("Respuesta:", respuesta.text)
    print("OK: la key y el modelo funcionan para este tipo de entrada.")


if __name__ == "__main__":
    main()
