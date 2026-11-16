"""Valida y normaliza la salida de la IA: reglas conocidas, cajas 0-1000 → porcentaje, ids, severidad."""

import json
import logging
import re

from pydantic import ValidationError

from models.reglas import ReglaEtiquetado
from models.schemas import ETIQUETA_POR_SEVERIDAD, AIFinding, Finding
from services.errors import AnalisisError

logger = logging.getLogger("solinal.postproceso")

ORDEN_SEVERIDAD = {"critico": 0, "advertencia": 1, "ok": 2}


def _invalida(detalle: str) -> AnalisisError:
    return AnalisisError(
        "AI_INVALID_RESPONSE",
        f"La IA devolvió una respuesta que no se pudo interpretar ({detalle}). Inténtalo de nuevo.",
        True,
    )


def parsear(texto: str) -> tuple[list[AIFinding], int]:
    """Devuelve (hallazgos válidos, cantidad descartada por formato)."""
    limpio = texto.strip()
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", limpio, flags=re.IGNORECASE)

    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError as e:
        logger.warning("Respuesta de la IA que no es JSON: %s", limpio[:800])
        raise _invalida("JSON inválido") from e

    # Algunos modelos devuelven la lista suelta en vez de {"hallazgos": [...]}: se acepta.
    lista = datos if isinstance(datos, list) else datos.get("hallazgos") if isinstance(datos, dict) else None
    if not isinstance(lista, list):
        logger.warning("Respuesta de la IA sin la lista 'hallazgos': %s", limpio[:800])
        raise _invalida("falta la lista 'hallazgos'")

    validos: list[AIFinding] = []
    descartados = 0
    for bruto in lista:
        try:
            validos.append(AIFinding.model_validate(bruto))
        except ValidationError:
            descartados += 1
    return validos, descartados


def _caja_a_porcentaje(caja: list[int] | None) -> tuple[float, float, float, float] | None:
    if caja is None:
        return None
    ymin, xmin, ymax, xmax = (min(max(v, 0), 1000) for v in caja)
    if ymax <= ymin or xmax <= xmin:
        return None
    return (
        round(xmin / 10, 1),
        round(ymin / 10, 1),
        round((xmax - xmin) / 10, 1),
        round((ymax - ymin) / 10, 1),
    )


def procesar(
    hallazgos_ia: list[AIFinding],
    reglas: list[ReglaEtiquetado],
    n_paginas: int,
    descartados_por_formato: int = 0,
) -> tuple[list[Finding], list[str]]:
    por_id = {r.id: (i, r) for i, r in enumerate(reglas)}
    avisos: list[str] = []
    vistos: set[tuple[str, int]] = set()
    elegidos: list[tuple[int, int, AIFinding, ReglaEtiquetado, str]] = []
    desconocidos = cajas_invalidas = 0

    for h in hallazgos_ia:
        if h.regla_id not in por_id:
            desconocidos += 1
            continue
        orden_regla, regla = por_id[h.regla_id]

        pagina = min(max(h.pagina, 1), n_paginas)
        clave = (h.regla_id, pagina)
        if clave in vistos:
            continue
        vistos.add(clave)

        severidad = h.severidad
        # La severidad de un incumplimiento la define la regla; la IA no puede agravarla.
        if severidad == "critico" and regla.severidad_si_incumple == "advertencia":
            severidad = "advertencia"

        elegidos.append((ORDEN_SEVERIDAD[severidad], orden_regla, h.model_copy(update={"pagina": pagina}), regla, severidad))

    if not elegidos:
        raise _invalida("no hubo hallazgos para las reglas")

    elegidos.sort(key=lambda t: (t[0], t[1]))

    resultado: list[Finding] = []
    for posicion, (_, _, h, regla, severidad) in enumerate(elegidos, start=1):
        caja = _caja_a_porcentaje(h.caja_2d)
        if h.caja_2d is not None and caja is None:
            cajas_invalidas += 1
        x, y, ancho, alto = caja if caja else (None, None, None, None)

        resultado.append(
            Finding(
                id=f"F-{posicion:03d}",
                regla_id=regla.id,
                pagina=h.pagina,
                severidad=severidad,
                etiqueta=ETIQUETA_POR_SEVERIDAD[severidad],
                x=x, y=y, ancho=ancho, alto=alto,
                titulo=h.titulo.strip()[:120],
                elemento_evaluado=h.elemento_evaluado.strip()[:200],
                descripcion_hallazgo=h.descripcion_hallazgo.strip()[:600],
                referencia_normativa=regla.referencia_normativa,
                recomendacion=h.recomendacion.strip()[:600],
                confianza=h.confianza,
            )
        )

    if desconocidos:
        avisos.append(f"La IA devolvió {desconocidos} hallazgo(s) con reglas desconocidas; se descartaron.")
    if descartados_por_formato:
        avisos.append(f"{descartados_por_formato} hallazgo(s) tenían un formato inválido y se descartaron.")
    if cajas_invalidas:
        avisos.append(f"{cajas_invalidas} hallazgo(s) traían una caja inválida y se muestran sin ubicación.")

    return resultado, avisos
