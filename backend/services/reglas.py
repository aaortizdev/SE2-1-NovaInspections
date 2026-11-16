"""Carga las reglas de un mercado desde backend/reglas/<mercado>.json."""

import json
import os
from pathlib import Path

from models.reglas import MERCADOS_ACTIVOS, ReglaEtiquetado

CARPETA = Path(__file__).resolve().parents[1] / "reglas"


def cargar_reglas(mercado: str, incluir_pendientes: bool | None = None) -> list[ReglaEtiquetado]:
    """Devuelve las reglas del mercado. Por defecto solo las 'verificada'.

    Con REGLAS_INCLUIR_PENDIENTES=true (solo desarrollo) también devuelve las 'pendiente_revision'.
    """
    if mercado not in MERCADOS_ACTIVOS:
        raise ValueError(f"Mercado no soportado: {mercado}")

    if incluir_pendientes is None:
        incluir_pendientes = os.getenv("REGLAS_INCLUIR_PENDIENTES", "false").lower() == "true"

    datos = json.loads((CARPETA / f"{mercado}.json").read_text(encoding="utf-8"))
    reglas = [ReglaEtiquetado.model_validate(r) for r in datos]

    if incluir_pendientes:
        return reglas
    return [r for r in reglas if r.estado == "verificada"]
