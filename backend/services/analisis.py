"""Ejecuta el análisis en segundo plano y garantiza que la evaluación nunca quede en in_progress."""

import logging
import os

from models.schemas import AnalysisError
from services import mock_engine
from services.errors import AnalisisError
from services.store import EvaluationStore

logger = logging.getLogger("solinal.analisis")


async def ejecutar_analisis(store: EvaluationStore, evaluation_id: str) -> None:
    evaluacion = store.obtener(evaluation_id)
    if evaluacion is None:
        return

    try:
        modo = os.getenv("AI_MODE", "mock").lower()

        if modo == "mock":
            resultado = await mock_engine.analizar(evaluacion)
        else:
            # AI-8 conectará aquí el motor real (preprocesamiento + Gemini + postproceso).
            raise AnalisisError(
                "INTERNAL",
                "El motor de IA real todavía no está conectado. Usa AI_MODE=mock.",
                reintentable=False,
            )

        store.completar(
            evaluation_id,
            hallazgos=resultado.hallazgos,
            paginas_analizadas=resultado.paginas_analizadas,
            advertencias_proceso=resultado.advertencias_proceso,
        )
    except AnalisisError as error:
        logger.warning("Análisis %s falló: %s (%s)", evaluation_id, error.mensaje, error.codigo)
        store.fallar(
            evaluation_id,
            AnalysisError(codigo=error.codigo, mensaje=error.mensaje, reintentable=error.reintentable),
        )
    except Exception:  # noqa: BLE001 - nada debe dejar la evaluación en in_progress
        logger.exception("Error inesperado en el análisis %s", evaluation_id)
        store.fallar(
            evaluation_id,
            AnalysisError(
                codigo="INTERNAL",
                mensaje="Ocurrió un error inesperado al analizar la etiqueta. Inténtalo de nuevo.",
                reintentable=True,
            ),
        )
