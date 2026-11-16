"""Almacén de evaluaciones en memoria (BE-2).

Una evaluación = un archivo + una normativa + su estado y resultado. Se pierde al reiniciar el
servidor (la base de datos queda para el Sprint 3), por eso se usa un solo worker.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from models.schemas import (
    AnalysisError,
    EstadoEvaluacion,
    EvaluationResultResponse,
    Finding,
    Summary,
    calcular_resumen,
)

MAX_EVALUACIONES = 50  # al superarlo se descartan las más antiguas (cada una guarda su archivo)


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


@dataclass
class Evaluacion:
    evaluation_id: str
    archivo: str
    tipo_contenido: str
    contenido: bytes
    normativa: str
    status: EstadoEvaluacion = "pending"
    creado_en: datetime = field(default_factory=_ahora)
    actualizado_en: datetime | None = None
    paginas_analizadas: int | None = None
    resumen: Summary | None = None
    hallazgos: list[Finding] = field(default_factory=list)
    advertencias_proceso: list[str] = field(default_factory=list)
    error: AnalysisError | None = None


ResultadoIniciar = Literal["ok", "not_found", "conflict"]


class EvaluationStore:
    def __init__(self) -> None:
        self._items: dict[str, Evaluacion] = {}
        self._lock = threading.Lock()

    def crear(self, archivo: str, tipo_contenido: str, contenido: bytes, normativa: str) -> Evaluacion:
        evaluacion = Evaluacion(
            evaluation_id=str(uuid4()),
            archivo=archivo,
            tipo_contenido=tipo_contenido,
            contenido=contenido,
            normativa=normativa,
        )
        with self._lock:
            self._items[evaluacion.evaluation_id] = evaluacion
            while len(self._items) > MAX_EVALUACIONES:
                self._items.pop(next(iter(self._items)))
        return evaluacion

    def obtener(self, evaluation_id: str) -> Evaluacion | None:
        with self._lock:
            return self._items.get(evaluation_id)

    def iniciar(self, evaluation_id: str) -> ResultadoIniciar:
        """pending o error -> in_progress. Es atómico: dos clics seguidos no lanzan dos análisis."""
        with self._lock:
            evaluacion = self._items.get(evaluation_id)
            if evaluacion is None:
                return "not_found"
            if evaluacion.status not in ("pending", "error"):
                return "conflict"
            evaluacion.status = "in_progress"
            evaluacion.error = None
            evaluacion.resumen = None
            evaluacion.hallazgos = []
            evaluacion.advertencias_proceso = []
            evaluacion.actualizado_en = _ahora()
            return "ok"

    def completar(
        self,
        evaluation_id: str,
        hallazgos: list[Finding],
        paginas_analizadas: int,
        advertencias_proceso: list[str],
    ) -> None:
        with self._lock:
            evaluacion = self._items.get(evaluation_id)
            if evaluacion is None:
                return
            evaluacion.status = "completed"
            evaluacion.hallazgos = hallazgos
            evaluacion.resumen = calcular_resumen(hallazgos)
            evaluacion.paginas_analizadas = paginas_analizadas
            evaluacion.advertencias_proceso = advertencias_proceso
            evaluacion.error = None
            evaluacion.actualizado_en = _ahora()

    def fallar(self, evaluation_id: str, error: AnalysisError) -> None:
        with self._lock:
            evaluacion = self._items.get(evaluation_id)
            if evaluacion is None:
                return
            evaluacion.status = "error"
            evaluacion.error = error
            evaluacion.resumen = None
            evaluacion.hallazgos = []
            evaluacion.actualizado_en = _ahora()

    def a_respuesta(self, evaluation_id: str) -> EvaluationResultResponse | None:
        """Copia consistente del estado actual (se arma dentro del lock)."""
        with self._lock:
            e = self._items.get(evaluation_id)
            if e is None:
                return None
            return EvaluationResultResponse(
                evaluation_id=e.evaluation_id,
                status=e.status,
                archivo=e.archivo,
                normativa=e.normativa,  # type: ignore[arg-type]
                creado_en=e.creado_en,
                actualizado_en=e.actualizado_en,
                paginas_analizadas=e.paginas_analizadas,
                resumen=e.resumen,
                hallazgos=list(e.hallazgos),
                advertencias_proceso=list(e.advertencias_proceso),
                error=e.error,
            )
