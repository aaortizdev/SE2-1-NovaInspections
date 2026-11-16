import { useEffect, useRef } from 'react'
import { useEvaluationStore } from '../store/useEvaluationStore'

export default function PanelDictamen() {
  const estado = useEvaluationStore((s) => s.evaluationStatus)
  const hallazgos = useEvaluationStore((s) => s.findings)
  const avisos = useEvaluationStore((s) => s.processWarnings)
  const seleccionado = useEvaluationStore((s) => s.selectedFindingId)
  const seleccionar = useEvaluationStore((s) => s.selectFinding)
  const refs = useRef<Record<string, HTMLElement | null>>({})

  useEffect(() => {
    if (seleccionado) {
      refs.current[seleccionado]?.scrollIntoView?.({ behavior: 'smooth', block: 'nearest' })
    }
  }, [seleccionado])

  if (estado === 'idle') return <p className="placeholder-text">Los resultados aparecerán aquí.</p>
  if (estado === 'pending' || estado === 'in_progress') {
    return <p className="placeholder-text">El dictamen aparecerá cuando termine el análisis.</p>
  }
  if (estado === 'error') return <p className="placeholder-text">No hay resultados por mostrar.</p>

  return (
    <div className="dictamen-list">
      {avisos.map((aviso) => (
        <p key={aviso} className="dictamen-warning">
          {aviso}
        </p>
      ))}

      {hallazgos.length === 0 && <p className="placeholder-text">No se encontraron hallazgos.</p>}

      {hallazgos.map((h, i) => (
        <article
          key={h.id}
          ref={(el) => {
            refs.current[h.id] = el
          }}
          className={`finding-card finding-card--${h.severidad}${
            seleccionado === h.id ? ' finding-card--selected' : ''
          }`}
          onClick={() => seleccionar(seleccionado === h.id ? null : h.id)}
        >
          <header className="finding-head">
            <span className={`overlay-badge overlay-badge--${h.severidad} finding-number`}>{i + 1}</span>
            <span className={`finding-severity finding-severity--${h.severidad}`}>{h.etiqueta}</span>
            <strong className="finding-title">{h.titulo}</strong>
          </header>
          <p className="finding-element">{h.elemento_evaluado}</p>
          <p>{h.descripcion_hallazgo}</p>
          <p className="finding-reco">
            <b>Recomendación:</b> {h.recomendacion}
          </p>
          <footer className="finding-foot">
            <span>{h.referencia_normativa}</span>
            <span>Confianza {Math.round(h.confianza * 100)} %</span>
          </footer>
        </article>
      ))}
    </div>
  )
}
