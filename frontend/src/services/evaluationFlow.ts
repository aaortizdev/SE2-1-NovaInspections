import { toast } from 'sonner'
import { useEvaluationStore } from '../store/useEvaluationStore'
import { ApiError, crearEvaluacion, iniciarAnalisis, obtenerEvaluacion } from './api'

// Tiempos del polling (exportado y mutable solo para poder acelerarlo en pruebas).
export const tiempos = {
  intervaloMs: 2000,
  intervaloLentoMs: 4000,
  pasoALentoMs: 30_000,
  maximoMs: 8 * 60_000,
}

const TOAST_ID = 'analisis'
const MSG_SIN_CONEXION = 'No se pudo conectar con el backend. Comprueba que esté ejecutándose.'
const MSG_TIEMPO = 'El análisis tardó demasiado. Inténtalo de nuevo.'

let controlador: AbortController | null = null

const store = () => useEvaluationStore.getState()

function dormir(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    const t = setTimeout(done, ms)
    function done() {
      signal.removeEventListener('abort', done)
      clearTimeout(t)
      resolve()
    }
    signal.addEventListener('abort', done)
  })
}

function nuevaEjecucion(): AbortController {
  controlador?.abort()
  controlador = new AbortController()
  return controlador
}

function fallar(mensaje: string) {
  store().setStatus('error', mensaje)
  toast.error(mensaje, { id: TOAST_ID })
}

// Consulta el estado hasta completed/error. Ignora todo si la ejecución fue cancelada.
async function sondear(id: string, ctl: AbortController) {
  const { signal } = ctl
  const inicio = Date.now()
  let fallosDeRed = 0

  while (!signal.aborted) {
    const transcurrido = Date.now() - inicio
    if (transcurrido > tiempos.maximoMs) {
      return fallar(MSG_TIEMPO)
    }

    await dormir(transcurrido > tiempos.pasoALentoMs ? tiempos.intervaloLentoMs : tiempos.intervaloMs, signal)
    if (signal.aborted) return

    try {
      const r = await obtenerEvaluacion(id, signal)
      if (signal.aborted || controlador !== ctl) return
      fallosDeRed = 0

      if (r.status === 'completed') {
        store().setResults(r.hallazgos, r.resumen, r.advertencias_proceso ?? [])
        toast.success('Análisis completado.', { id: TOAST_ID })
        return
      }

      if (r.status === 'error') {
        return fallar(r.error?.mensaje ?? 'El análisis no pudo completarse.')
      }
    } catch (error) {
      if (signal.aborted) return
      if (error instanceof ApiError) {
        if (error.status === 404) {
          store().setEvaluationId(null)
          return fallar('La evaluación ya no existe en el servidor. Vuelve a analizar la etiqueta.')
        }
        return fallar(error.message)
      }
      fallosDeRed += 1
      if (fallosDeRed >= 3) return fallar(MSG_SIN_CONEXION)
    }
  }
}

async function iniciarYSondear(id: string, ctl: AbortController) {
  try {
    await iniciarAnalisis(id, ctl.signal)
  } catch (error) {
    if (ctl.signal.aborted) return
    if (error instanceof ApiError) {
      if (error.status === 404) {
        store().setEvaluationId(null)
        return fallar('La evaluación ya no existe en el servidor. Vuelve a analizar la etiqueta.')
      }
      // 409: ya estaba en curso; se sigue consultando su estado.
      if (error.status !== 409) return fallar(error.message)
    } else {
      return fallar(MSG_SIN_CONEXION)
    }
  }

  if (ctl.signal.aborted) return
  store().setStatus('in_progress')
  toast.loading('Analizando cumplimiento regulatorio con IA...', { id: TOAST_ID })
  await sondear(id, ctl)
}

export async function enviarYAnalizar(): Promise<void> {
  const s = store()
  if (!s.fileData || !s.selectedRegulation || !s.termsAccepted) return
  if (s.evaluationStatus === 'pending' || s.evaluationStatus === 'in_progress') return

  const ctl = nuevaEjecucion()
  s.beginEvaluation()
  toast.loading('Enviando etiqueta...', { id: TOAST_ID })

  try {
    const creada = await crearEvaluacion(s.fileData, s.selectedRegulation, s.termsAccepted, ctl.signal)
    if (ctl.signal.aborted) return
    store().setEvaluationId(creada.evaluation_id)
    await iniciarYSondear(creada.evaluation_id, ctl)
  } catch (error) {
    if (ctl.signal.aborted) return
    if (error instanceof ApiError) {
      // Validación rechazada (400/422): se vuelve al formulario con el motivo.
      if (error.status === 400 || error.status === 422) {
        store().resetEvaluation()
        toast.error(error.message, { id: TOAST_ID })
        return
      }
      return fallar(error.message)
    }
    fallar(MSG_SIN_CONEXION)
  }
}

export async function reintentarAnalisis(): Promise<void> {
  const s = store()
  if (s.evaluationStatus !== 'error') return

  // Sin evaluation_id (404 previo o fallo al crear) hay que volver a enviar el archivo.
  if (!s.evaluationId) return enviarYAnalizar()

  const ctl = nuevaEjecucion()
  const id = s.evaluationId
  s.setStatus('pending')
  toast.loading('Reintentando análisis...', { id: TOAST_ID })
  await iniciarYSondear(id, ctl)
}

export function cancelarEvaluacionActiva(): void {
  controlador?.abort()
  controlador = null
  toast.dismiss(TOAST_ID)
}
