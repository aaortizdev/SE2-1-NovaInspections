"""Motor de IA real (AI-8): preprocesamiento + Gemini + postproceso."""

import asyncio
import os

from services import gemini_client, postproceso
from services.errors import AnalisisError
from services.preprocesamiento import preparar
from services.prompt import construir_prompt
from services.reglas import cargar_reglas
from services.resultado import ResultadoAnalisis
from services.store import Evaluacion

# Se puede reemplazar en las pruebas por una función falsa.
_generar = gemini_client.generar


async def analizar(evaluacion: Evaluacion) -> ResultadoAnalisis:
    if not os.getenv("GEMINI_API_KEY"):
        raise AnalisisError("INTERNAL", "Falta GEMINI_API_KEY en backend/.env.", reintentable=False)

    reglas = cargar_reglas(evaluacion.normativa)
    if not reglas:
        raise AnalisisError(
            "INTERNAL",
            "No hay reglas verificadas para esta normativa. Verifica las reglas o usa REGLAS_INCLUIR_PENDIENTES=true en desarrollo.",
            reintentable=False,
        )

    preparado = await asyncio.to_thread(preparar, evaluacion.contenido, evaluacion.tipo_contenido)
    prompt = construir_prompt(reglas, len(preparado.paginas))

    texto = await _generar(preparado.paginas, prompt)

    hallazgos_ia, descartados = postproceso.parsear(texto)
    hallazgos, avisos = postproceso.procesar(hallazgos_ia, reglas, len(preparado.paginas), descartados)

    advertencias = list(preparado.advertencias) + avisos
    if any(r.estado != "verificada" for r in reglas):
        advertencias.insert(0, "Se usaron reglas pendientes de verificación: el resultado es solo de desarrollo.")

    return ResultadoAnalisis(
        hallazgos=hallazgos,
        paginas_analizadas=len(preparado.paginas),
        advertencias_proceso=advertencias,
    )
