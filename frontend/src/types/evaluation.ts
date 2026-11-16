import type { SeveridadHallazgo } from '../components/CapaDeOverlays'

export type { SeveridadHallazgo }

// "idle" existe solo en el frontend (antes de pulsar "Analizar etiqueta").
export type EstadoEvaluacion = 'idle' | 'pending' | 'in_progress' | 'completed' | 'error'

export type Mercado = 'estados_unidos' | 'ecuador'

export type Hallazgo = {
  id: string
  regla_id: string
  pagina: number
  severidad: SeveridadHallazgo
  etiqueta: string
  x: number | null
  y: number | null
  ancho: number | null
  alto: number | null
  titulo: string
  elemento_evaluado: string
  descripcion_hallazgo: string
  recomendacion: string
  referencia_normativa: string
  confianza: number
}

export type Resumen = {
  total: number
  criticos: number
  advertencias: number
  conformes: number
}

export type ErrorAnalisis = {
  codigo: string
  mensaje: string
  reintentable: boolean
}

export type EvaluacionCreada = {
  evaluation_id: string
  status: 'pending'
  archivo: string
  normativa: Mercado
  creado_en: string
}

export type EvaluacionIniciada = {
  evaluation_id: string
  status: 'in_progress'
}

export type EvaluacionResultado = {
  evaluation_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  archivo: string
  normativa: Mercado
  resumen: Resumen | null
  hallazgos: Hallazgo[]
  advertencias_proceso?: string[]
  paginas_analizadas?: number | null
  error: ErrorAnalisis | null
}
