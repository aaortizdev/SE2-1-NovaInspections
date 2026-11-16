import { useEvaluationStore } from '../store/useEvaluationStore'
import { hallazgosACajas } from '../utils/hallazgos'
import CapaDeOverlays from './CapaDeOverlays'

// Conecta los hallazgos del store con la capa de overlays. Vive aparte para que el
// zoom (que cambia muchas veces por segundo) no vuelva a renderizar toda la App.
export default function CapaHallazgos() {
  const hallazgos = useEvaluationStore((s) => s.findings)
  const pagina = useEvaluationStore((s) => s.pageNumber)
  const esPdf = useEvaluationStore((s) => s.fileType === 'application/pdf')
  const zoom = useEvaluationStore((s) => s.zoomScale)
  const seleccionada = useEvaluationStore((s) => s.selectedFindingId)
  const seleccionar = useEvaluationStore((s) => s.selectFinding)

  return (
    <CapaDeOverlays
      cajas={hallazgosACajas(hallazgos)}
      paginaActual={esPdf ? pagina : 1}
      zoomPorcentaje={zoom}
      seleccionadaId={seleccionada}
      onSeleccionar={(id) => seleccionar(seleccionada === id ? null : id)}
    />
  )
}
