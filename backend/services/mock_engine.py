"""Motor de IA simulado (BE-6). Sirve para desarrollar el frontend y para la demostración sin gastar cuota.

Variables de entorno (se leen en cada llamada):
  AI_MOCK_DELAY_S  segundos de espera simulada (por defecto 4)
  AI_MOCK_FAIL     "true" para forzar un error AI_TIMEOUT reintentable

Los textos llevan el prefijo [MOCK]: no son contenido regulatorio real. Los ID de regla son de ejemplo.
"""

import asyncio
import os

from models.schemas import ETIQUETA_POR_SEVERIDAD, Finding
from services.errors import AnalisisError
from services.resultado import ResultadoAnalisis
from services.store import Evaluacion


def _hallazgo(**campos) -> Finding:
    severidad = campos["severidad"]
    return Finding(etiqueta=ETIQUETA_POR_SEVERIDAD[severidad], **campos)


def hallazgos_de_ejemplo(normativa: str) -> list[Finding]:
    if normativa == "estados_unidos":
        return [
            _hallazgo(
                id="F-001", regla_id="US-FDA-NET-01", pagina=1, severidad="critico",
                x=5.0, y=5.0, ancho=30.0, alto=15.0,
                titulo="Contenido neto incompleto",
                elemento_evaluado="Declaración de contenido neto",
                descripcion_hallazgo="[MOCK] Descripción de ejemplo del hallazgo crítico.",
                referencia_normativa="[MOCK] Referencia de ejemplo (FDA).",
                recomendacion="[MOCK] Recomendación de ejemplo.",
                confianza=0.82,
            ),
            _hallazgo(
                id="F-002", regla_id="US-FDA-ALE-01", pagina=1, severidad="advertencia",
                x=None, y=None, ancho=None, alto=None,
                titulo="No se puede confirmar la declaración de alérgenos",
                elemento_evaluado="Lista de ingredientes",
                descripcion_hallazgo="[MOCK] Descripción de ejemplo de la advertencia.",
                referencia_normativa="[MOCK] Referencia de ejemplo (FDA).",
                recomendacion="[MOCK] Recomendación de ejemplo.",
                confianza=0.55,
            ),
            _hallazgo(
                id="F-003", regla_id="US-FDA-FAB-01", pagina=1, severidad="ok",
                x=5.0, y=85.0, ancho=60.0, alto=8.0,
                titulo="Fabricante e importador declarados",
                elemento_evaluado="Datos del fabricante",
                descripcion_hallazgo="[MOCK] Descripción de ejemplo de un elemento conforme.",
                referencia_normativa="[MOCK] Referencia de ejemplo (FDA).",
                recomendacion="[MOCK] Sin acciones requeridas.",
                confianza=0.93,
            ),
        ]

    return [
        _hallazgo(
            id="F-001", regla_id="EC-RTE022-SEM-01", pagina=1, severidad="critico",
            x=12.4, y=63.0, ancho=28.5, alto=14.2,
            titulo="Falta el semáforo nutricional",
            elemento_evaluado="Panel frontal",
            descripcion_hallazgo="[MOCK] Descripción de ejemplo del hallazgo crítico.",
            referencia_normativa="[MOCK] Referencia de ejemplo (RTE INEN 022).",
            recomendacion="[MOCK] Recomendación de ejemplo.",
            confianza=0.82,
        ),
        _hallazgo(
            id="F-002", regla_id="EC-RTE022-ALE-01", pagina=1, severidad="advertencia",
            x=None, y=None, ancho=None, alto=None,
            titulo="No se puede confirmar la declaración de alérgenos",
            elemento_evaluado="Lista de ingredientes",
            descripcion_hallazgo="[MOCK] Descripción de ejemplo de la advertencia.",
            referencia_normativa="[MOCK] Referencia de ejemplo (RTE INEN 022).",
            recomendacion="[MOCK] Recomendación de ejemplo.",
            confianza=0.55,
        ),
        _hallazgo(
            id="F-003", regla_id="EC-RTE022-FAB-01", pagina=1, severidad="ok",
            x=5.0, y=85.0, ancho=60.0, alto=8.0,
            titulo="Datos del fabricante presentes",
            elemento_evaluado="Datos del fabricante",
            descripcion_hallazgo="[MOCK] Descripción de ejemplo de un elemento conforme.",
            referencia_normativa="[MOCK] Referencia de ejemplo (RTE INEN 022).",
            recomendacion="[MOCK] Sin acciones requeridas.",
            confianza=0.93,
        ),
    ]


async def analizar(evaluacion: Evaluacion) -> ResultadoAnalisis:
    await asyncio.sleep(float(os.getenv("AI_MOCK_DELAY_S", "4")))

    if os.getenv("AI_MOCK_FAIL", "false").lower() == "true":
        raise AnalisisError(
            "AI_TIMEOUT",
            "El motor de IA tardó demasiado en responder. Inténtalo de nuevo.",
            reintentable=True,
        )

    return ResultadoAnalisis(
        hallazgos=hallazgos_de_ejemplo(evaluacion.normativa),
        paginas_analizadas=1,
        advertencias_proceso=["Modo mock: resultados de ejemplo, no son un análisis real."],
    )
