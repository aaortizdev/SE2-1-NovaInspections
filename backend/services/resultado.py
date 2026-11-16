"""Resultado común de los motores de análisis (mock y real)."""

from dataclasses import dataclass

from models.schemas import Finding


@dataclass
class ResultadoAnalisis:
    hallazgos: list[Finding]
    paginas_analizadas: int
    advertencias_proceso: list[str]
