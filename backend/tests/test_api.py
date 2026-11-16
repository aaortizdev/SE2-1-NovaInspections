"""Pruebas de la API en modo mock (BE-2 a BE-6).

Ejecutar desde backend/:  python tests/test_api.py   (o con pytest)
Si falta el módulo httpx:  python -m pip install httpx
"""

import os
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["AI_MODE"] = "mock"
os.environ["AI_MOCK_DELAY_S"] = "0"
os.environ.pop("AI_MOCK_FAIL", None)

from fastapi.testclient import TestClient

from main import app, store
from models.schemas import EvaluationResultResponse, calcular_resumen

cliente = TestClient(app)

PDF = b"%PDF-1.4\n% etiqueta de prueba\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


@contextmanager
def entorno(**variables):
    anteriores = {k: os.environ.get(k) for k in variables}
    os.environ.update(variables)
    try:
        yield
    finally:
        for clave, valor in anteriores.items():
            if valor is None:
                os.environ.pop(clave, None)
            else:
                os.environ[clave] = valor


def crear(normativa="ecuador", nombre="etiqueta.pdf", tipo="application/pdf", contenido=PDF, terminos="true"):
    return cliente.post(
        "/evaluaciones",
        files={"archivo": (nombre, contenido, tipo)},
        data={"normativa": normativa, "acepto_terminos": terminos},
    )


def test_crear_devuelve_201_pending():
    r = crear()
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["status"] == "pending"
    assert cuerpo["archivo"] == "etiqueta.pdf" and cuerpo["normativa"] == "ecuador"
    assert len(cuerpo["evaluation_id"]) == 36


def test_validaciones_del_sprint_1_siguen_igual():
    r = crear(normativa="mexico")
    assert r.status_code == 400 and r.json()["detail"] == "Selecciona una opción válida de normativa."

    r = crear(terminos="false")
    assert r.status_code == 400 and r.json()["detail"] == "Debes aceptar los términos y condiciones."

    r = crear(nombre="etiqueta.gif", tipo="image/gif")
    assert r.status_code == 400 and r.json()["detail"] == "Solo se permiten archivos PDF, PNG o JPG."

    r = crear(contenido=b"")
    assert r.status_code == 400 and r.json()["detail"] == "El archivo está vacío."

    r = crear(contenido=b"esto no es un pdf")
    assert r.status_code == 400 and r.json()["detail"] == "El contenido no corresponde al formato indicado."

    r = crear(contenido=b"%PDF-" + b"0" * (15 * 1024 * 1024))
    assert r.status_code == 400 and r.json()["detail"] == "El archivo no puede superar los 15 MB."


def test_union_europea_ya_no_se_acepta_y_estados_unidos_si():
    assert crear(normativa="union_europea").status_code == 400
    assert crear(normativa="estados_unidos", nombre="e.png", tipo="image/png", contenido=PNG).status_code == 201


def test_flujo_completo_pending_in_progress_completed():
    evaluation_id = crear().json()["evaluation_id"]

    r = cliente.post(f"/evaluaciones/{evaluation_id}/analizar")
    assert r.status_code == 202
    assert r.json() == {"evaluation_id": evaluation_id, "status": "in_progress"}

    r = cliente.get(f"/evaluaciones/{evaluation_id}")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-store"
    resultado = EvaluationResultResponse.model_validate(r.json())
    assert resultado.status == "completed"
    assert resultado.evaluation_id == evaluation_id
    assert [h.severidad for h in resultado.hallazgos] == ["critico", "advertencia", "ok"]
    assert resultado.resumen == calcular_resumen(resultado.hallazgos)
    assert resultado.resumen.total == 3 and resultado.error is None
    assert resultado.hallazgos[1].x is None  # el hallazgo sin caja no se dibuja


def test_mientras_corre_el_estado_es_in_progress_sin_resultado():
    evaluation_id = crear().json()["evaluation_id"]
    assert store.iniciar(evaluation_id) == "ok"  # simula el análisis en curso

    cuerpo = cliente.get(f"/evaluaciones/{evaluation_id}").json()
    assert cuerpo["status"] == "in_progress"
    assert cuerpo["resumen"] is None and cuerpo["hallazgos"] == []

    assert cliente.post(f"/evaluaciones/{evaluation_id}/analizar").status_code == 409


def test_no_se_puede_analizar_dos_veces_una_completada():
    evaluation_id = crear().json()["evaluation_id"]
    assert cliente.post(f"/evaluaciones/{evaluation_id}/analizar").status_code == 202
    assert cliente.post(f"/evaluaciones/{evaluation_id}/analizar").status_code == 409


def test_evaluacion_inexistente_da_404():
    assert cliente.post("/evaluaciones/no-existe/analizar").status_code == 404
    assert cliente.get("/evaluaciones/no-existe").status_code == 404


def test_error_y_reintento_sin_volver_a_subir_el_archivo():
    evaluation_id = crear().json()["evaluation_id"]

    with entorno(AI_MOCK_FAIL="true"):
        assert cliente.post(f"/evaluaciones/{evaluation_id}/analizar").status_code == 202
        cuerpo = cliente.get(f"/evaluaciones/{evaluation_id}").json()

    assert cuerpo["status"] == "error"
    assert cuerpo["error"]["codigo"] == "AI_TIMEOUT" and cuerpo["error"]["reintentable"] is True
    assert cuerpo["resumen"] is None and cuerpo["hallazgos"] == []

    # Reintento: mismo evaluation_id, sin subir el archivo otra vez.
    assert cliente.post(f"/evaluaciones/{evaluation_id}/analizar").status_code == 202
    cuerpo = cliente.get(f"/evaluaciones/{evaluation_id}").json()
    assert cuerpo["status"] == "completed" and cuerpo["error"] is None


def test_cada_evaluacion_conserva_sus_propios_datos():
    ec = crear(normativa="ecuador").json()["evaluation_id"]
    us = crear(normativa="estados_unidos").json()["evaluation_id"]
    cliente.post(f"/evaluaciones/{ec}/analizar")
    cliente.post(f"/evaluaciones/{us}/analizar")

    reglas_ec = {h["regla_id"][:2] for h in cliente.get(f"/evaluaciones/{ec}").json()["hallazgos"]}
    reglas_us = {h["regla_id"][:2] for h in cliente.get(f"/evaluaciones/{us}").json()["hallazgos"]}
    assert reglas_ec == {"EC"} and reglas_us == {"US"}


def test_modo_real_sin_conectar_termina_en_error_claro_no_en_in_progress():
    evaluation_id = crear().json()["evaluation_id"]
    with entorno(AI_MODE="real"):
        cliente.post(f"/evaluaciones/{evaluation_id}/analizar")
        cuerpo = cliente.get(f"/evaluaciones/{evaluation_id}").json()
    assert cuerpo["status"] == "error" and cuerpo["error"]["codigo"] == "INTERNAL"
    assert cuerpo["error"]["reintentable"] is False


def test_health():
    cuerpo = cliente.get("/health").json()
    assert cuerpo["estado"] == "ok" and cuerpo["modo"] == "mock"
    assert isinstance(cuerpo["api_key_configurada"], bool)


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
