from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SOLINAL Etiqueta API")

# Permite que el frontend local se comunique con el backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MERCADOS_PERMITIDOS = {
    "estados_unidos",
    "union_europea",
    "reino_unido",
    "mexico",
    "colombia",
    "ecuador",
}

FORMATOS_PERMITIDOS = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

TAMANO_MAXIMO = 15 * 1024 * 1024  # 15 MB


@app.get("/")
def inicio():
    return {"mensaje": "El backend de SOLINAL Etiqueta está funcionando"}


@app.post("/evaluaciones")
async def crear_evaluacion(
    archivo: Annotated[UploadFile, File()],
    normativa: Annotated[str, Form()],
    acepto_terminos: Annotated[bool, Form()],
):
    if normativa not in MERCADOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Selecciona una opción válida de normativa.",
        )

    if not acepto_terminos:
        raise HTTPException(
            status_code=400,
            detail="Debes aceptar los términos y condiciones.",
        )

    nombre_archivo = archivo.filename or ""
    extension = Path(nombre_archivo).suffix.lower()
    tipo_esperado = FORMATOS_PERMITIDOS.get(extension)

    if tipo_esperado is None or archivo.content_type != tipo_esperado:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF, PNG o JPG.",
        )

    # Leemos hasta un byte más del límite para detectar archivos grandes.
    contenido = await archivo.read(TAMANO_MAXIMO + 1)

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(
            status_code=400,
            detail="El archivo no puede superar los 15 MB.",
        )

    firmas_validas = {
        ".pdf": b"%PDF-",
        ".png": b"\x89PNG\r\n\x1a\n",
        ".jpg": b"\xff\xd8\xff",
        ".jpeg": b"\xff\xd8\xff",
    }

    if not contenido.startswith(firmas_validas[extension]):
        raise HTTPException(
            status_code=400,
            detail="El contenido no corresponde al formato indicado.",
        )

    return {
        "mensaje": "Archivo recibido y validado correctamente.",
        "archivo": nombre_archivo,
        "normativa": normativa,
        "estado": "Pendiente IA",
    }