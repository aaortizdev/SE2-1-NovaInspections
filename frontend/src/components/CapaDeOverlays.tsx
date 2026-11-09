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
}

type Props = {
  cajas: CajaOverlay[]
  paginaActual: number
}

// Capa 2 del visor: va encima de la etiqueta (Capa 1), dentro del contenedor de
// zoom y paneo, por eso se mueve y escala junto con ella. En el Sprint 2/3 solo
// hay que pasarle las cajas que devuelva la IA.
export default function CapaDeOverlays({ cajas, paginaActual }: Props) {
  const cajasDeLaPagina = cajas.filter((caja) => caja.pagina === paginaActual)

  return (
    <div className="overlay-layer" aria-hidden="true">
      {cajasDeLaPagina.map((caja) => (
        <div
          key={caja.id}
          className={`overlay-box overlay-box--${caja.severidad}`}
          style={{
            left: `${caja.x}%`,
            top: `${caja.y}%`,
            width: `${caja.ancho}%`,
            height: `${caja.alto}%`,
          }}
          title={caja.etiqueta}
        >
          {caja.etiqueta && <span className="overlay-box-label">{caja.etiqueta}</span>}
        </div>
      ))}
    </div>
  )
}