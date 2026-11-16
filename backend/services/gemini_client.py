"""AI-2: llamada a Gemini. Convierte los fallos del SDK en AnalisisError con código claro."""

import asyncio
import logging
import os

from services.errors import AnalisisError
from services.preprocesamiento import Pagina

logger = logging.getLogger("solinal.gemini")


def mapear_error(exc: Exception) -> AnalisisError:
    """Traduce una excepción del SDK o de red a un error controlado (sin exponer la clave)."""
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return AnalisisError("AI_TIMEOUT", "El motor de IA tardó demasiado en responder. Inténtalo de nuevo.", True)

    # Fallos de red de la librería HTTP que use el SDK (httpx, requests...), sin importarla aquí.
    if type(exc).__module__.split(".")[0] in ("httpx", "httpx2", "requests", "httpcore", "urllib3"):
        return AnalisisError("AI_UNAVAILABLE", "No se pudo conectar con el servicio de IA. Inténtalo de nuevo.", True)

    codigo = getattr(exc, "code", None)
    if isinstance(codigo, int):
        if codigo == 429:
            return AnalisisError(
                "AI_RATE_LIMIT",
                "Se alcanzó el límite de uso de la IA. Espera un minuto e inténtalo de nuevo.",
                True,
            )
        if codigo >= 500:
            return AnalisisError("AI_UNAVAILABLE", "El servicio de IA no está disponible ahora. Inténtalo de nuevo.", True)
        if codigo in (401, 403):
            return AnalisisError("INTERNAL", "La IA rechazó la clave de acceso. Revisa GEMINI_API_KEY.", False)
        if codigo == 404:
            return AnalisisError("INTERNAL", "El modelo de IA configurado no existe. Revisa AI_MODEL.", False)
        if codigo == 400:
            return AnalisisError("INTERNAL", "La IA rechazó la solicitud. Revisa GEMINI_API_KEY y AI_MODEL.", False)

    return AnalisisError("INTERNAL", "Ocurrió un error inesperado al llamar a la IA. Inténtalo de nuevo.", True)


# Esperas (segundos) antes de cada reintento cuando Google responde 503/5xx. Reemplazable en pruebas.
ESPERAS_REINTENTO = (3.0, 8.0)


async def _llamar(api_key: str, modelo: str, contenido: list, config, tiempo: float):
    from google import genai

    cliente = genai.Client(api_key=api_key)
    return await asyncio.wait_for(
        cliente.aio.models.generate_content(model=modelo, contents=contenido, config=config),
        timeout=tiempo,
    )


async def generar(paginas: list[Pagina], prompt: str) -> str:
    """Envía el prompt y las imágenes a Gemini y devuelve el texto de la respuesta (JSON).

    Si Google responde 503/5xx (alta demanda) reintenta con espera; si sigue fallando y existe
    AI_FALLBACK_MODEL (uno o varios), los prueba en orden.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AnalisisError("INTERNAL", "Falta GEMINI_API_KEY en backend/.env.", reintentable=False)

    from google.genai import types

    modelos = [os.getenv("AI_MODEL", "gemini-3.8-flash")]
    # AI_FALLBACK_MODEL admite varios modelos separados por coma; se prueban en ese orden.
    for respaldo in os.getenv("AI_FALLBACK_MODEL", "").split(","):
        respaldo = respaldo.strip()
        if respaldo and respaldo not in modelos:
            modelos.append(respaldo)
    tiempo = float(os.getenv("AI_TIMEOUT_S", "90"))

    contenido: list = [prompt]
    for pagina in paginas:
        contenido.append(f"Página {pagina.numero}:")
        contenido.append(types.Part.from_bytes(data=pagina.datos, mime_type=pagina.mime))

    parametros = {"response_mime_type": "application/json", "temperature": 0}
    # Opcional: AI_THINKING = minimal | low | medium | high. Menos "pensamiento" = respuesta más rápida.
    nivel = os.getenv("AI_THINKING", "").strip().upper()
    if nivel:
        if nivel not in ("MINIMAL", "LOW", "MEDIUM", "HIGH"):
            raise AnalisisError("INTERNAL", "AI_THINKING debe ser minimal, low, medium o high.", reintentable=False)
        parametros["thinking_config"] = types.ThinkingConfig(thinking_level=nivel)
    config = types.GenerateContentConfig(**parametros)

    ultimo_error: AnalisisError | None = None
    for modelo in modelos:
        for intento in range(len(ESPERAS_REINTENTO) + 1):
            try:
                respuesta = await _llamar(api_key, modelo, contenido, config, tiempo)
            except AnalisisError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("Fallo al llamar a Gemini %s (%s): %s", modelo, type(exc).__name__, exc)
                error = mapear_error(exc)
                if error.codigo not in ("AI_UNAVAILABLE", "AI_TIMEOUT"):
                    raise error from exc
                ultimo_error = error
                if error.codigo == "AI_TIMEOUT":
                    # Un modelo que no responde en el tiempo máximo no se reintenta: se pasa al respaldo.
                    break
                if intento < len(ESPERAS_REINTENTO):
                    await asyncio.sleep(ESPERAS_REINTENTO[intento])
                continue

            texto = (getattr(respuesta, "text", None) or "").strip()
            if not texto:
                raise AnalisisError(
                    "AI_INVALID_RESPONSE",
                    "La IA no devolvió una respuesta utilizable. Inténtalo de nuevo.",
                    True,
                )
            logger.info("Respuesta recibida del modelo %s", modelo)
            return texto

    assert ultimo_error is not None
    raise ultimo_error
