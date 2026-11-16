import type { CajaOverlay } from '../components/CapaDeOverlays'
import type { Hallazgo } from '../types/evaluation'

// Convierte hallazgos del backend en cajas del visor. El número es la posición en la
// lista (F-001 → 1), el mismo que muestra la tarjeta del dictamen. Sin caja no se dibuja.
export function hallazgosACajas(hallazgos: Hallazgo[]): CajaOverlay[] {
  const cajas: CajaOverlay[] = []

  hallazgos.forEach((h, indice) => {
    if (h.x === null || h.y === null || h.ancho === null || h.alto === null) return

    cajas.push({
      id: h.id,
      pagina: h.pagina,
      x: h.x,
      y: h.y,
      ancho: h.ancho,
      alto: h.alto,
      severidad: h.severidad,
      etiqueta: h.etiqueta,
      titulo: h.titulo,
      numero: indice + 1,
    })
  })

  return cajas
}
