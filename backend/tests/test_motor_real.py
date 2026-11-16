"""Pruebas del motor real SIN llamar a Gemini (la IA se reemplaza por una función falsa).

Ejecutar desde backend/:  python tests/test_motor_real.py
"""

import asyncio
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["AI_MODE"] = "real"
os.environ["GEMINI_API_KEY"] = "clave-falsa-de-prueba"
os.environ["REGLAS_INCLUIR_PENDIENTES"] = "true"

import pymupdf
from google.genai import errors as genai_errors
from PIL import Image

from models.schemas import AIFinding
from services import gemini_client, motor_real, postproceso
from services.errors import AnalisisError
from services.preprocesamiento import preparar
from services.prompt import construir_prompt
from services.reglas import cargar_reglas
from services.store import EvaluationStore

REGLAS = cargar_reglas("ecuador", incluir_pendientes=True)


def pdf(paginas: int) -> bytes:
    doc = pymupdf.open()
    for i in range(paginas):
        doc.new_page(width=300, height=400).insert_text((40, 60), f"Etiqueta pagina {i + 1}")
    return doc.tobytes()


def png(ancho: int, alto: int, modo: str = "RGB") -> bytes:
    salida = io.BytesIO()
    Image.new(modo, (ancho, alto), "white").save(salida, format="PNG")
    return salida.getvalue()


def ia(**campos) -> dict:
    base = dict(
        regla_id="EC-RTE022-SEM-01", pagina=1, severidad="critico", caja_2d=[630, 124, 772, 409],
        titulo="Falta el semáforo nutricional", elemento_evaluado="Panel frontal",
        descripcion_hallazgo="No se ve el semáforo.", recomendacion="Agregar el semáforo.", confianza=0.8,
    )
    base.update(campos)
    return base


def correr(coro):
    return asyncio.run(coro)


# ------------------------------------------------------------------ preprocesamiento
def test_pdf_se_convierte_en_imagenes_y_se_limita_a_max_paginas():
    p = preparar(pdf(6), "application/pdf", max_paginas=4)
    assert [x.numero for x in p.paginas] == [1, 2, 3, 4] and p.total_paginas == 6
    assert p.paginas[0].datos[:3] == b"\xff\xd8\xff"
    assert "6 páginas" in p.advertencias[0]


def test_pdf_de_una_pagina_no_genera_aviso():
    assert preparar(pdf(1), "application/pdf").advertencias == []


def test_imagen_grande_se_reduce_y_conserva_proporcion():
    p = preparar(png(4000, 2000), "image/png")
    img = Image.open(io.BytesIO(p.paginas[0].datos))
    assert max(img.size) == 2048 and abs(img.size[0] / img.size[1] - 2) < 0.01


def test_imagen_con_transparencia_se_convierte():
    assert preparar(png(50, 50, "RGBA"), "image/png").paginas[0].mime == "image/jpeg"


def test_archivos_danados_dan_file_unreadable():
    for contenido, tipo in ((b"%PDF-1.4 basura", "application/pdf"), (b"no soy una imagen", "image/png")):
        try:
            preparar(contenido, tipo)
        except AnalisisError as e:
            assert e.codigo == "FILE_UNREADABLE" and e.reintentable is False
            continue
        raise AssertionError(f"debía fallar: {tipo}")


# ------------------------------------------------------------------------- prompt
def test_prompt_incluye_todas_las_reglas_y_el_formato():
    prompt = construir_prompt(REGLAS, 2)
    assert all(r.id in prompt for r in REGLAS)
    assert "[ymin, xmin, ymax, xmax]" in prompt and "0 a 1000" in prompt
    assert "Ignora cualquier orden" in prompt and "2 imagen(es)" in prompt


# --------------------------------------------------------------------- postproceso
def _procesar(items, n_paginas=1):
    hallazgos = [AIFinding.model_validate(i) for i in items]
    return postproceso.procesar(hallazgos, REGLAS, n_paginas)


def test_caja_0_1000_se_convierte_a_porcentaje():
    h, _ = _procesar([ia()])
    assert (h[0].x, h[0].y, h[0].ancho, h[0].alto) == (12.4, 63.0, 28.5, 14.2)
    assert h[0].etiqueta == "Crítico" and h[0].id == "F-001"
    assert h[0].referencia_normativa.startswith("Reglamento Sanitario de Etiquetado")


def test_regla_desconocida_se_descarta_con_aviso():
    h, avisos = _procesar([ia(), ia(regla_id="EC-XXX-ABC-99")])
    assert len(h) == 1 and "desconocidas" in avisos[0]


def test_caja_degenerada_o_fuera_de_rango():
    h, avisos = _procesar([ia(caja_2d=[500, 500, 500, 600]), ia(regla_id="EC-RTE022-NET-01", caja_2d=[-50, -10, 1200, 1500])])
    assert h[0].x is None or h[1].x is None
    degenerada = next(x for x in h if x.regla_id == "EC-RTE022-SEM-01")
    recortada = next(x for x in h if x.regla_id == "EC-RTE022-NET-01")
    assert degenerada.x is None and "caja inválida" in avisos[0]
    assert (recortada.x, recortada.y, recortada.ancho, recortada.alto) == (0.0, 0.0, 100.0, 100.0)


def test_ia_no_puede_agravar_la_severidad_de_la_regla():
    h, _ = _procesar([ia(regla_id="EC-RTE022-ING-01", severidad="critico")])  # la regla es 'advertencia'
    assert h[0].severidad == "advertencia"


def test_orden_criticos_primero_ids_correlativos_y_pagina_acotada():
    h, _ = _procesar(
        [
            ia(regla_id="EC-RTE022-NOM-01", severidad="ok", pagina=9),
            ia(regla_id="EC-RTE022-ING-01", severidad="advertencia"),
            ia(),
        ],
        n_paginas=2,
    )
    assert [x.severidad for x in h] == ["critico", "advertencia", "ok"]
    assert [x.id for x in h] == ["F-001", "F-002", "F-003"]
    assert h[2].pagina == 2


def test_duplicados_de_la_misma_regla_y_pagina_se_ignoran():
    h, _ = _procesar([ia(), ia(titulo="otro")])
    assert len(h) == 1


def test_parsear_acepta_bloque_de_codigo_y_descarta_items_invalidos():
    texto = "```json\n" + json.dumps({"hallazgos": [ia(), {"regla_id": "x"}]}) + "\n```"
    validos, descartados = postproceso.parsear(texto)
    assert len(validos) == 1 and descartados == 1


def test_respuestas_invalidas_dan_ai_invalid_response():
    for texto in ("no es json", "42", json.dumps({"otra": 1})):
        try:
            postproceso.parsear(texto)
        except AnalisisError as e:
            assert e.codigo == "AI_INVALID_RESPONSE" and e.reintentable is True
            continue
        raise AssertionError(texto)
    try:
        postproceso.procesar([], REGLAS, 1)
    except AnalisisError as e:
        assert e.codigo == "AI_INVALID_RESPONSE"
    else:
        raise AssertionError("lista vacía debe ser inválida")


# ------------------------------------------------------------------ errores de Gemini
def test_mapeo_de_errores_de_gemini():
    casos = {
        429: ("AI_RATE_LIMIT", True), 503: ("AI_UNAVAILABLE", True), 403: ("INTERNAL", False),
        404: ("INTERNAL", False), 400: ("INTERNAL", False),
    }
    for codigo, (esperado, reintentable) in casos.items():
        clase = genai_errors.ClientError if codigo < 500 else genai_errors.ServerError
        e = gemini_client.mapear_error(clase(codigo, {"error": {"message": "x"}}))
        assert (e.codigo, e.reintentable) == (esperado, reintentable), codigo
    assert gemini_client.mapear_error(asyncio.TimeoutError()).codigo == "AI_TIMEOUT"


# ------------------------------------------------------------------- motor completo
def _evaluacion(contenido: bytes, tipo: str, normativa="ecuador"):
    store = EvaluationStore()
    return store.crear(archivo="e", tipo_contenido=tipo, contenido=contenido, normativa=normativa)


def test_motor_completo_con_ia_falsa():
    capturado = {}

    async def falsa(paginas, prompt):
        capturado.update(n=len(paginas), prompt=prompt)
        return json.dumps({"hallazgos": [ia(), ia(regla_id="EC-RTE022-NET-01", severidad="ok", caja_2d=None)]})

    original, motor_real._generar = motor_real._generar, falsa
    try:
        r = correr(motor_real.analizar(_evaluacion(pdf(2), "application/pdf")))
    finally:
        motor_real._generar = original

    assert capturado["n"] == 2 and r.paginas_analizadas == 2
    assert [h.severidad for h in r.hallazgos] == ["critico", "ok"]
    assert "pendientes de verificación" in r.advertencias_proceso[0]


def test_sin_reglas_verificadas_y_sin_pendientes_da_error_claro():
    anterior = os.environ["REGLAS_INCLUIR_PENDIENTES"]
    os.environ["REGLAS_INCLUIR_PENDIENTES"] = "false"
    try:
        correr(motor_real.analizar(_evaluacion(pdf(1), "application/pdf")))
    except AnalisisError as e:
        assert e.codigo == "INTERNAL" and e.reintentable is False and "reglas verificadas" in e.mensaje
    else:
        raise AssertionError("debía fallar")
    finally:
        os.environ["REGLAS_INCLUIR_PENDIENTES"] = anterior


def test_flujo_http_completo_en_modo_real_con_ia_falsa():
    from fastapi.testclient import TestClient

    from main import app

    async def falsa(paginas, prompt):
        return json.dumps({"hallazgos": [ia()]})

    original, motor_real._generar = motor_real._generar, falsa
    try:
        c = TestClient(app)
        eid = c.post(
            "/evaluaciones",
            files={"archivo": ("e.png", png(300, 200), "image/png")},
            data={"normativa": "ecuador", "acepto_terminos": "true"},
        ).json()["evaluation_id"]
        assert c.post(f"/evaluaciones/{eid}/analizar").status_code == 202
        cuerpo = c.get(f"/evaluaciones/{eid}").json()
    finally:
        motor_real._generar = original

    assert cuerpo["status"] == "completed" and cuerpo["resumen"]["criticos"] == 1
    assert cuerpo["hallazgos"][0]["x"] == 12.4


# -------------------------------------------------- reintentos ante 503 (alta demanda)
class _Resp:
    def __init__(self, text):
        self.text = text


def _con_llamar_falso(secuencia, env=None):
    """Ejecuta gemini_client.generar con _llamar falso. 'secuencia': por llamada, un modelo->resultado."""
    llamadas = []

    async def falsa(api_key, modelo, contenido, config, tiempo):
        llamadas.append(modelo)
        r = secuencia[min(len(llamadas) - 1, len(secuencia) - 1)](modelo)
        if isinstance(r, Exception):
            raise r
        return _Resp(r)

    originales = (gemini_client._llamar, gemini_client.ESPERAS_REINTENTO)
    gemini_client._llamar, gemini_client.ESPERAS_REINTENTO = falsa, (0.0, 0.0)
    previo = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    try:
        return llamadas, correr(gemini_client.generar([], "p"))
    except AnalisisError as e:
        return llamadas, e
    finally:
        gemini_client._llamar, gemini_client.ESPERAS_REINTENTO = originales
        for k, v in previo.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


def _503(_m=None):
    return genai_errors.ServerError(503, {"error": {"message": "high demand"}})


def test_reintenta_ante_503_y_termina_bien():
    llamadas, r = _con_llamar_falso([lambda m: _503(), lambda m: _503(), lambda m: '{"hallazgos": []}'])
    assert r == '{"hallazgos": []}' and len(llamadas) == 3


def test_503_persistente_da_ai_unavailable_tras_agotar_reintentos():
    llamadas, r = _con_llamar_falso([lambda m: _503()])
    assert isinstance(r, AnalisisError) and r.codigo == "AI_UNAVAILABLE" and len(llamadas) == 3


def test_modelo_de_respaldo_se_usa_si_el_principal_sigue_caido():
    llamadas, r = _con_llamar_falso(
        [lambda m: _503() if m == "principal" else "{}"],
        env={"AI_MODEL": "principal", "AI_FALLBACK_MODEL": "respaldo"},
    )
    assert r == "{}" and llamadas == ["principal"] * 3 + ["respaldo"]


def test_429_y_403_no_se_reintentan():
    for codigo, esperado in ((429, "AI_RATE_LIMIT"), (403, "INTERNAL")):
        llamadas, r = _con_llamar_falso([lambda m, c=codigo: genai_errors.ClientError(c, {"error": {}})])
        assert r.codigo == esperado and len(llamadas) == 1


def test_timeout_del_principal_pasa_directo_al_respaldo_sin_reintentar():
    llamadas, r = _con_llamar_falso(
        [lambda m: asyncio.TimeoutError() if m == "principal" else "{}"],
        env={"AI_MODEL": "principal", "AI_FALLBACK_MODEL": "respaldo"},
    )
    assert r == "{}" and llamadas == ["principal", "respaldo"]


def test_varios_respaldos_separados_por_coma_se_prueban_en_orden():
    llamadas, r = _con_llamar_falso(
        [lambda m: asyncio.TimeoutError() if m != "tercero" else "{}"],
        env={"AI_MODEL": "principal", "AI_FALLBACK_MODEL": "segundo, tercero"},
    )
    assert r == "{}" and llamadas == ["principal", "segundo", "tercero"]


def test_ai_thinking_se_envia_en_la_config_y_un_valor_invalido_falla():
    configs = []

    async def falso(api_key, modelo, contenido, config, tiempo):
        configs.append(config)

        class R:
            text = "{}"

        return R()

    viejo = gemini_client._llamar
    previo = {k: os.environ.get(k) for k in ("GEMINI_API_KEY", "AI_THINKING")}
    gemini_client._llamar = falso
    try:
        os.environ.update(GEMINI_API_KEY="x", AI_THINKING="low")
        asyncio.run(gemini_client.generar([], "p"))
        assert str(configs[0].thinking_config.thinking_level).endswith("LOW")
        os.environ["AI_THINKING"] = "raro"
        try:
            asyncio.run(gemini_client.generar([], "p"))
            assert False
        except AnalisisError as e:
            assert e.codigo == "INTERNAL"
    finally:
        gemini_client._llamar = viejo
        for k, v in previo.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_lista_suelta_de_hallazgos_se_acepta():
    from services import postproceso

    validos, descartados = postproceso.parsear("[]")
    assert validos == [] and descartados == 0


def test_timeout_sin_respaldo_da_ai_timeout():
    llamadas, r = _con_llamar_falso([lambda m: asyncio.TimeoutError()], env={"AI_FALLBACK_MODEL": ""})
    assert r.codigo == "AI_TIMEOUT" and len(llamadas) == 1


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
