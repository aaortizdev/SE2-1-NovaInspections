"""Prueba el motor real (preprocesamiento + Gemini + postproceso) con un archivo, sin levantar la API.

Uso (desde backend/):  python scripts/probar_motor.py "C:\\ruta\\etiqueta.png"
                       python scripts/probar_motor.py "C:\\ruta\\etiqueta.pdf" --json
Requiere GEMINI_API_KEY en backend/.env. Usa las reglas de ecuador (incluye pendientes si
REGLAS_INCLUIR_PENDIENTES=true).
"""

import asyncio
import logging
import mimetypes
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

from services import motor_real
from services.errors import AnalisisError
from services.store import EvaluationStore


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)

    ruta = Path(args[0])
    tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
    evaluacion = EvaluationStore().crear(
        archivo=ruta.name, tipo_contenido=tipo, contenido=ruta.read_bytes(), normativa="ecuador"
    )

    inicio = time.time()
    try:
        r = asyncio.run(motor_real.analizar(evaluacion))
    except AnalisisError as e:
        sys.exit(f"ERROR {e.codigo}: {e.mensaje} (reintentable={e.reintentable})")

    print(f"Páginas analizadas: {r.paginas_analizadas}  ·  {time.time() - inicio:.1f} s")
    for aviso in r.advertencias_proceso:
        print(f"AVISO: {aviso}")
    print()
    for h in r.hallazgos:
        caja = f"x={h.x} y={h.y} ancho={h.ancho} alto={h.alto}" if h.x is not None else "sin caja"
        print(f"{h.id} [{h.etiqueta}] {h.regla_id} · {h.titulo}  ({caja}, confianza {h.confianza})")
        print(f"      {h.descripcion_hallazgo}")
        if "--json" in sys.argv:
            print("      " + h.model_dump_json())


if __name__ == "__main__":
    main()
