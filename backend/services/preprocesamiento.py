"""AI-1: convierte el archivo subido en imágenes para la IA.

- PDF: cada página (hasta AI_MAX_PAGES) se renderiza a JPEG. Así las cajas que devuelve la IA
  coinciden con lo que se ve en el visor.
- Imagen: se corrige el modo de color y se reduce si es muy grande. Las proporciones no cambian.
"""

import io
import os
from dataclasses import dataclass, field

import pymupdf
from PIL import Image, UnidentifiedImageError

from services.errors import AnalisisError

LADO_MAXIMO_PX = 2048
CALIDAD_JPEG = 88


@dataclass
class Pagina:
    numero: int  # 1, 2, 3...
    datos: bytes
    mime: str = "image/jpeg"


@dataclass
class Preparado:
    paginas: list[Pagina]
    total_paginas: int
    advertencias: list[str] = field(default_factory=list)


def _ilegible(detalle: str) -> AnalisisError:
    return AnalisisError(
        "FILE_UNREADABLE",
        f"No se pudo leer el archivo ({detalle}). Sube otro archivo e inténtalo de nuevo.",
        reintentable=False,
    )


def _a_jpeg(imagen: Image.Image) -> bytes:
    if imagen.mode in ("RGBA", "LA", "P"):
        imagen = imagen.convert("RGBA")
        fondo = Image.new("RGB", imagen.size, (255, 255, 255))
        fondo.paste(imagen, mask=imagen.split()[-1])
        imagen = fondo
    elif imagen.mode != "RGB":
        imagen = imagen.convert("RGB")

    if max(imagen.size) > LADO_MAXIMO_PX:
        imagen.thumbnail((LADO_MAXIMO_PX, LADO_MAXIMO_PX))

    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", quality=CALIDAD_JPEG)
    return salida.getvalue()


def _preparar_pdf(contenido: bytes, max_paginas: int) -> Preparado:
    try:
        doc = pymupdf.open(stream=contenido, filetype="pdf")
    except Exception as e:  # noqa: BLE001 - cualquier fallo de apertura = archivo ilegible
        raise _ilegible("PDF dañado") from e

    try:
        if doc.needs_pass:
            raise _ilegible("el PDF está protegido con contraseña")
        total = doc.page_count
        if total == 0:
            raise _ilegible("el PDF no tiene páginas")

        paginas: list[Pagina] = []
        for indice in range(min(total, max_paginas)):
            pagina = doc[indice]
            ancho, alto = pagina.rect.width, pagina.rect.height
            if ancho <= 0 or alto <= 0:
                raise _ilegible("una página del PDF no tiene tamaño")
            zoom = min(4.0, LADO_MAXIMO_PX / max(ancho, alto))
            pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
            paginas.append(Pagina(numero=indice + 1, datos=pix.tobytes("jpeg", jpg_quality=CALIDAD_JPEG)))
    except AnalisisError:
        raise
    except Exception as e:  # noqa: BLE001
        raise _ilegible("no se pudo procesar el PDF") from e
    finally:
        doc.close()

    avisos = []
    if total > len(paginas):
        avisos.append(f"El PDF tiene {total} páginas; se analizaron solo las primeras {len(paginas)}.")
    return Preparado(paginas=paginas, total_paginas=total, advertencias=avisos)


def _preparar_imagen(contenido: bytes) -> Preparado:
    try:
        imagen = Image.open(io.BytesIO(contenido))
        imagen.load()
        datos = _a_jpeg(imagen)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as e:
        raise _ilegible("imagen dañada") from e
    return Preparado(paginas=[Pagina(numero=1, datos=datos)], total_paginas=1)


def preparar(contenido: bytes, tipo_contenido: str, max_paginas: int | None = None) -> Preparado:
    if max_paginas is None:
        max_paginas = max(1, int(os.getenv("AI_MAX_PAGES", "4")))

    if tipo_contenido == "application/pdf":
        return _preparar_pdf(contenido, max_paginas)
    return _preparar_imagen(contenido)
