import { useEvaluationStore } from '../store/useEvaluationStore'
import { reintentarAnalisis } from '../services/evaluationFlow'

export default function BannerEstadoEvaluacion() {
  const estado = useEvaluationStore((s) => s.evaluationStatus)
  const mensaje = useEvaluationStore((s) => s.errorMessage)
  const total = useEvaluationStore((s) => s.metrics?.total ?? 0)

  if (estado === 'idle') return null

  if (estado === 'pending') {
    return (
      <div className="eval-banner eval-banner--pending" role="status">
        <span className="eval-spinner eval-spinner--amber" aria-hidden="true" />
        Enviando etiqueta...
      </div>
    )
  }

  if (estado === 'in_progress') {
    return (
      <div className="eval-banner eval-banner--progress" role="status">
        <span className="eval-spinner" aria-hidden="true" />
        Analizando cumplimiento regulatorio con IA...
      </div>
    )
  }

  if (estado === 'completed') {
    return (
      <div className="eval-banner eval-banner--done" role="status">
        ✓ Análisis completado · {total} {total === 1 ? 'hallazgo' : 'hallazgos'}
      </div>
    )
  }

  return (
    <div className="eval-banner eval-banner--error" role="alert">
      <span>{mensaje || 'El análisis no pudo completarse.'}</span>
      <button type="button" className="eval-retry" onClick={() => void reintentarAnalisis()}>
        Reintentar análisis
      </button>
    </div>
  )
}
