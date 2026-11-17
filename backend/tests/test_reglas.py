"""Pruebas del formato de reglas. Ejecutar desde backend/:  python tests/test_reglas.py"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError

from models.reglas import ReglaEtiquetado
from services.reglas import CARPETA, cargar_reglas


def _ejemplo() -> dict:
    return json.loads((CARPETA / "ecuador.json").read_text(encoding="utf-8"))[0]


def test_ecuador_es_valido_y_sin_ids_repetidos():
    reglas = cargar_reglas("ecuador", incluir_pendientes=True)
    assert len(reglas) >= 10
    assert len({r.id for r in reglas}) == len(reglas)
    assert all(r.id.startswith("EC-") for r in reglas)


def test_mercado_no_activo_se_rechaza():
    try:
        cargar_reglas("estados_unidos", incluir_pendientes=True)
    except ValueError:
        return
    raise AssertionError("estados_unidos no debe cargarse mientras esté como Próximamente")


def test_por_defecto_solo_se_usan_verificadas():
    assert cargar_reglas("ecuador", incluir_pendientes=False) == []


def test_formato_de_id_invalido():
    d = _ejemplo(); d["id"] = "ecuador-semaforo"
    try:
        ReglaEtiquetado.model_validate(d)
    except ValidationError:
        return
    raise AssertionError("debía rechazar el id")


def test_campo_desconocido_y_severidad_invalida():
    for cambio in ({"categoria": "x"}, {"severidad_si_incumple": "grave"}, {"fuente_url": "http://x.com"}):
        d = {**_ejemplo(), **cambio}
        try:
            ReglaEtiquetado.model_validate(d)
        except ValidationError:
            continue
        raise AssertionError(f"debía rechazar {cambio}")


def test_referencia_normativa_la_arma_el_backend():
    regla = next(r for r in cargar_reglas("ecuador", incluir_pendientes=True) if r.id == "EC-RTE022-SEM-01")
    assert regla.referencia_normativa.endswith("AM 5103 Art. 12")


if __name__ == "__main__":
    pruebas = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
