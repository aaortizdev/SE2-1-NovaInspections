"""Valida que los JSON de ejemplo del contrato cumplen los esquemas.

Ejecutar desde backend/:  python tests/test_schemas.py   (o con pytest)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError

from models.schemas import (
    AIOutput,
    EvaluationCreateResponse,
    EvaluationResultResponse,
    EvaluationStartResponse,
    Finding,
    calcular_resumen,
)

EJEMPLOS = Path(__file__).resolve().parents[2] / "docs" / "ejemplos"


def cargar(nombre: str) -> dict:
    return json.loads((EJEMPLOS / nombre).read_text(encoding="utf-8"))


def test_creada():
    r = EvaluationCreateResponse.model_validate(cargar("creada.json"))
    assert r.status == "pending"


def test_iniciada():
    r = EvaluationStartResponse.model_validate(cargar("iniciada.json"))
    assert r.status == "in_progress"


def test_completada_y_resumen_coherente():
    r = EvaluationResultResponse.model_validate(cargar("completada.json"))
    assert r.status == "completed"
    assert r.resumen == calcular_resumen(r.hallazgos)


def test_error():
    r = EvaluationResultResponse.model_validate(cargar("error.json"))
    assert r.status == "error" and r.error is not None and r.error.reintentable


def test_salida_ia():
    r = AIOutput.model_validate(cargar("ai_output.json"))
    assert r.hallazgos[0].caja_2d == [630, 124, 772, 409]
    assert r.hallazgos[1].caja_2d is None


def test_severidad_invalida_se_rechaza():
    datos = cargar("ai_output.json")
    datos["hallazgos"][0]["severidad"] = "grave"
    try:
        AIOutput.model_validate(datos)
    except ValidationError:
        return
    raise AssertionError("Debió rechazar la severidad 'grave'")


def test_caja_de_tres_valores_se_rechaza():
    datos = cargar("ai_output.json")
    datos["hallazgos"][0]["caja_2d"] = [630, 124, 772]
    try:
        AIOutput.model_validate(datos)
    except ValidationError:
        return
    raise AssertionError("Debió rechazar una caja de 3 valores")


def test_caja_parcial_se_rechaza():
    datos = cargar("completada.json")["hallazgos"][0]
    datos["ancho"] = None
    try:
        Finding.model_validate(datos)
    except ValidationError:
        return
    raise AssertionError("Debió rechazar una caja con solo algunos campos")


def test_coordenada_fuera_de_rango_se_rechaza():
    datos = cargar("completada.json")["hallazgos"][0]
    datos["x"] = 120
    try:
        Finding.model_validate(datos)
    except ValidationError:
        return
    raise AssertionError("Debió rechazar x=120")


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
