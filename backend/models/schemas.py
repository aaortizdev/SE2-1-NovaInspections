"""Esquemas del Sprint 2 (BE-1). El contrato completo está en docs/api-contract.md.

Hay dos familias de modelos:
- AIFinding / AIOutput: lo que se le EXIGE a la IA (sin resumen, sin etiqueta, sin
  referencia normativa: esos campos los completa el backend).
- Finding / Summary / EvaluationResultResponse: lo que recibe el frontend.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Severidad = Literal["critico", "advertencia", "ok"]
EstadoEvaluacion = Literal["pending", "in_progress", "completed", "error"]
Mercado = Literal["estados_unidos", "ecuador"]
CodigoError = Literal[
    "AI_TIMEOUT",
    "AI_RATE_LIMIT",
    "AI_UNAVAILABLE",
    "AI_INVALID_RESPONSE",
    "FILE_UNREADABLE",
    "INTERNAL",
]

# Texto que muestra el visor sobre cada caja (CajaOverlay.etiqueta).
ETIQUETA_POR_SEVERIDAD: dict[str, str] = {
    "critico": "Crítico",
    "advertencia": "Advertencia",
    "ok": "OK",
}


# --------------------------------------------------------------------------- IA
class AIFinding(BaseModel):
    """Un hallazgo tal como lo devuelve la IA."""

    regla_id: str = Field(description="ID de la regla de la base regulatoria, p. ej. EC-RTE022-SEM-01")
    pagina: int = Field(ge=1, description="Página de la etiqueta (1 para imágenes)")
    severidad: Severidad
    caja_2d: list[int] | None = Field(
        default=None,
        min_length=4,
        max_length=4,
        description="[ymin, xmin, ymax, xmax] en escala 0-1000, o null si no hay elemento visible",
    )
    titulo: str
    elemento_evaluado: str
    descripcion_hallazgo: str
    recomendacion: str
    confianza: float = Field(ge=0, le=1)


class AIOutput(BaseModel):
    hallazgos: list[AIFinding]


# ---------------------------------------------------------------- Respuesta API
class Finding(BaseModel):
    """Hallazgo ya normalizado. x, y, ancho y alto son porcentajes (0-100)."""

    id: str
    regla_id: str
    pagina: int = Field(ge=1)
    severidad: Severidad
    etiqueta: str
    x: float | None = Field(default=None, ge=0, le=100)
    y: float | None = Field(default=None, ge=0, le=100)
    ancho: float | None = Field(default=None, ge=0, le=100)
    alto: float | None = Field(default=None, ge=0, le=100)
    titulo: str
    elemento_evaluado: str
    descripcion_hallazgo: str
    referencia_normativa: str
    recomendacion: str
    confianza: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def caja_completa_o_nula(self) -> "Finding":
        caja = (self.x, self.y, self.ancho, self.alto)
        if any(v is None for v in caja) and not all(v is None for v in caja):
            raise ValueError("x, y, ancho y alto deben venir los cuatro o ninguno")
        return self


class Summary(BaseModel):
    total: int = Field(ge=0)
    criticos: int = Field(ge=0)
    advertencias: int = Field(ge=0)
    conformes: int = Field(ge=0)


class AnalysisError(BaseModel):
    codigo: CodigoError
    mensaje: str
    reintentable: bool


class EvaluationCreateResponse(BaseModel):
    """POST /evaluaciones -> 201"""

    evaluation_id: str
    status: EstadoEvaluacion
    archivo: str
    normativa: Mercado
    creado_en: datetime


class EvaluationStartResponse(BaseModel):
    """POST /evaluaciones/{id}/analizar -> 202"""

    evaluation_id: str
    status: EstadoEvaluacion


class EvaluationResultResponse(BaseModel):
    """GET /evaluaciones/{id} -> 200 (en cualquier estado)"""

    evaluation_id: str
    status: EstadoEvaluacion
    archivo: str
    normativa: Mercado
    creado_en: datetime
    actualizado_en: datetime | None = None
    paginas_analizadas: int | None = None
    resumen: Summary | None = None
    hallazgos: list[Finding] = Field(default_factory=list)
    advertencias_proceso: list[str] = Field(default_factory=list)
    error: AnalysisError | None = None


def calcular_resumen(hallazgos: list[Finding]) -> Summary:
    """El resumen lo calcula el backend; la IA nunca cuenta."""
    return Summary(
        total=len(hallazgos),
        criticos=sum(h.severidad == "critico" for h in hallazgos),
        advertencias=sum(h.severidad == "advertencia" for h in hallazgos),
        conformes=sum(h.severidad == "ok" for h in hallazgos),
    )
