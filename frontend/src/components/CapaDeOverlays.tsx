import './CapaDeOverlays.css'

export type SeveridadHallazgo = 'critico' | 'advertencia' | 'ok'

// Coordenadas en porcentaje (0 a 100) respecto al tamaño de la etiqueta, no en píxeles.
// Así la caja queda en el mismo lugar sin importar el zoom ni el tamaño del visor.
export type CajaOverlay = {
  id: string
  pagina: number // 1 para imágenes; en PDFs, la página donde está el hallazgo
  x: number
  y: number
  ancho: number
  alto: number
  severidad: SeveridadHallazgo
  etiqueta?: string
  titulo?: string // texto del tooltip: "{etiqueta} · {titulo}"
  numero?: number // número del círculo (posición en el dictamen)
}

type Props = {
  cajas: CajaOverlay[]
  paginaActual: number
  zoomPorcentaje?: number
  seleccionadaId?: string | null
  onSeleccionar?: (id: string) => void
}

// Capa 2 del visor: va encima de la etiqueta (Capa 1), dentro del contenedor de
// zoom y paneo, por eso se mueve y escala junto con ella.
export default function CapaDeOverlays({
  cajas,
  paginaActual,
  zoomPorcentaje = 100,
  seleccionadaId = null,
  onSeleccionar,
}: Props) {
  const cajasDeLaPagina = cajas.filter((caja) => caja.pagina === paginaActual)
  // Las cajas más pequeñas van encima de las grandes: así una caja que contiene a otras
  // (por ejemplo, "información no está en español") no tapa a las de adentro y todas se pueden
  // seleccionar con el mouse. La selección y el hover no cambian este orden.
  const porArea = [...cajasDeLaPagina].sort((a, b) => b.ancho * b.alto - a.ancho * a.alto)
  const capaDe = new Map(porArea.map((caja, i) => [caja.id, i + 1]))
  // El círculo y el tooltip se contra-escalan para mantener un tamaño legible con cualquier zoom.
  const contraEscala = 100 / Math.max(zoomPorcentaje, 1)

  return (
    <div className="overlay-layer">
      {cajasDeLaPagina.map((caja) => {
        const tooltip = [caja.etiqueta, caja.titulo].filter(Boolean).join(' · ')

        return (
          <div
            key={caja.id}
            className={`overlay-box overlay-box--${caja.severidad}${
              seleccionadaId === caja.id ? ' overlay-box--selected' : ''
            }`}
            style={{
              left: `${caja.x}%`,
              top: `${caja.y}%`,
              width: `${caja.ancho}%`,
              height: `${caja.alto}%`,
              zIndex: capaDe.get(caja.id),
            }}
            role={onSeleccionar ? 'button' : undefined}
            aria-label={tooltip || undefined}
            onClick={onSeleccionar ? () => onSeleccionar(caja.id) : undefined}
          >
            {caja.numero !== undefined && (
              <span
                className={`overlay-badge overlay-badge--${caja.severidad}`}
                style={{ transform: `scale(${contraEscala})` }}
              >
                {caja.numero}
              </span>
            )}
            {tooltip && (
              <span className="overlay-tooltip" style={{ transform: `scale(${contraEscala})` }}>
                {tooltip}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}
