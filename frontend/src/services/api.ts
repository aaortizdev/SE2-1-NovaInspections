import type { EvaluacionCreada, EvaluacionIniciada, EvaluacionResultado } from '../types/evaluation'

const MENSAJE_POR_DEFECTO = 'No se pudo enviar la etiqueta. Inténtalo de nuevo.'

function baseUrl(): string {
  const url = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  return url.replace(/\/+$/, '')
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// FastAPI responde los errores como {"detail": "..."}; en errores de validación (422)
// "detail" llega como una lista de objetos con "msg". Devolvemos solo el texto legible.
export async function obtenerMensajeDeError(respuesta: Response): Promise<string> {
  try {
    const cuerpo = await respuesta.json()
    const detalle = cuerpo?.detail

    if (typeof detalle === 'string' && detalle.trim()) {
      return detalle
    }

    if (Array.isArray(detalle) && detalle.length > 0) {
      return detalle.map((item) => item?.msg).filter(Boolean).join(' ') || MENSAJE_POR_DEFECTO
    }
  } catch {
    // La respuesta no era JSON (por ejemplo, una página de error del servidor).
  }

  return MENSAJE_POR_DEFECTO
}

async function pedir<T>(ruta: string, init: RequestInit): Promise<T> {
  const respuesta = await fetch(`${baseUrl()}${ruta}`, { cache: 'no-store', ...init })

  if (!respuesta.ok) {
    throw new ApiError(respuesta.status, await obtenerMensajeDeError(respuesta))
  }

  return (await respuesta.json()) as T
}

export function crearEvaluacion(
  archivo: File,
  normativa: string,
  aceptoTerminos: boolean,
  signal?: AbortSignal,
): Promise<EvaluacionCreada> {
  const datos = new FormData()
  datos.append('archivo', archivo)
  datos.append('normativa', normativa)
  datos.append('acepto_terminos', String(aceptoTerminos))

  return pedir<EvaluacionCreada>('/evaluaciones', { method: 'POST', body: datos, signal })
}

export function iniciarAnalisis(id: string, signal?: AbortSignal): Promise<EvaluacionIniciada> {
  return pedir<EvaluacionIniciada>(`/evaluaciones/${encodeURIComponent(id)}/analizar`, {
    method: 'POST',
    signal,
  })
}

export function obtenerEvaluacion(id: string, signal?: AbortSignal): Promise<EvaluacionResultado> {
  return pedir<EvaluacionResultado>(`/evaluaciones/${encodeURIComponent(id)}`, { signal })
}
