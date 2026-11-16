import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    EvaluationCreateResponse,
    EvaluationResultResponse,
    EvaluationStartResponse,
)
from services.analisis import ejecutar_analisis
from services.store import EvaluationStore

load_dotenv()

app = FastAPI(title="SOLINAL Etiqueta API")

# CORS_ORIGINS (separados por comas) viene de backend/.env; sin definir, se permite todo (solo desarrollo).
_origenes = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sprint 2: solo Ecuador (ARCSA / RTE INEN 022). Estados Unidos (FDA) queda como "Próximamente":
# sus reglas ya están en backend/reglas/estados_unidos.json; para activarlo basta agregarlo aquí.
MERCADOS_PERMITIDOS = {
    "ecuador",
}

FORMATOS_PERMITIDOS = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

TAMANO_MAXIMO = 15 * 1024 * 1024  # 15 MB

store = EvaluationStore()


@app.get("/")
def inicio():
    return {"mensaje": "El backend de SOLINAL Etiqueta está funcionando"}


@app.get("/health")
def salud():
    return {
        "estado": "ok",
        "modo": os.getenv("AI_MODE", "mock").lower(),
        "api_key_configurada": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/evaluaciones", response_model=EvaluationCreateResponse, status_code=201)
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

    evaluacion = store.crear(
        archivo=nombre_archivo,
        tipo_contenido=tipo_esperado,
        contenido=contenido,
        normativa=normativa,
    )

    return EvaluationCreateResponse(
        evaluation_id=evaluacion.evaluation_id,
        status=evaluacion.status,
        archivo=evaluacion.archivo,
        normativa=evaluacion.normativa,  # type: ignore[arg-type]
        creado_en=evaluacion.creado_en,
    )


@app.post(
    "/evaluaciones/{evaluation_id}/analizar",
    response_model=EvaluationStartResponse,
    status_code=202,
)
async def iniciar_analisis(evaluation_id: str, tareas: BackgroundTasks):
    resultado = store.iniciar(evaluation_id)

    if resultado == "not_found":
        raise HTTPException(
            status_code=404,
            detail="No existe una evaluación con ese identificador.",
        )

    if resultado == "conflict":
        raise HTTPException(
            status_code=409,
            detail="La evaluación ya está en curso o ya fue completada.",
        )

    tareas.add_task(ejecutar_analisis, store, evaluation_id)

    return EvaluationStartResponse(evaluation_id=evaluation_id, status="in_progress")


@app.get("/evaluaciones/{evaluation_id}", response_model=EvaluationResultResponse)
def obtener_evaluacion(evaluation_id: str, respuesta: Response):
    respuesta.headers["Cache-Control"] = "no-store"

    evaluacion = store.a_respuesta(evaluation_id)

    if evaluacion is None:
        raise HTTPException(
            status_code=404,
            detail="No existe una evaluación con ese identificador.",
        )

    return evaluacion
