"""Valida backend/reglas/*.json. Ejecutar desde backend/:  python scripts/validar_reglas.py"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError

from models.reglas import MERCADOS_ACTIVOS, PREFIJO_POR_MERCADO, ReglaEtiquetado

CARPETA = Path(__file__).resolve().parents[1] / "reglas"


def main() -> int:
    errores: list[str] = []

    for mercado in MERCADOS_ACTIVOS:
        prefijo = PREFIJO_POR_MERCADO[mercado]
        ruta = CARPETA / f"{mercado}.json"
        if not ruta.exists():
            errores.append(f"Falta el archivo {ruta.name}")
            continue

        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errores.append(f"{ruta.name}: JSON inválido (línea {e.lineno}): {e.msg}")
            continue

        if not isinstance(datos, list):
            errores.append(f"{ruta.name}: debe ser una lista de reglas")
            continue

        ids = Counter()
        for i, bruto in enumerate(datos, start=1):
            try:
                regla = ReglaEtiquetado.model_validate(bruto)
            except ValidationError as e:
                for err in e.errors():
                    campo = ".".join(str(p) for p in err["loc"]) or "?"
                    errores.append(f"{ruta.name} regla #{i} ({bruto.get('id', '?')}): {campo}: {err['msg']}")
                continue

            ids[regla.id] += 1
            if not regla.id.startswith(prefijo + "-"):
                errores.append(f"{ruta.name}: {regla.id} no empieza con {prefijo}- (mercado {mercado})")
            if regla.estado == "verificada" and not regla.verificada_por:
                errores.append(f"{ruta.name}: {regla.id} está 'verificada' pero falta 'verificada_por'")

        for id_, n in ids.items():
            if n > 1:
                errores.append(f"{ruta.name}: id repetido {id_} ({n} veces)")

        estados = Counter(r.get("estado", "?") for r in datos if isinstance(r, dict))
        print(f"{ruta.name}: {len(datos)} reglas  {dict(estados)}")

    if errores:
        print("\nErrores:")
        for e in errores:
            print(" -", e)
        return 1

    print("\nTodo correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
