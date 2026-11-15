import { useState } from 'react'
import type { KeyboardEvent } from 'react'

type Props = {
  porcentaje: number
  minimo: number
  maximo: number
  disabled?: boolean
  onCambiar: (porcentaje: number) => void
}

// Porcentaje de zoom editable: se aplica con Enter o al salir del campo, se limita
// al rango permitido y se sincroniza con los botones y la rueda del mouse.
export default function EntradaZoom({ porcentaje, minimo, maximo, disabled, onCambiar }: Props) {
  // null = no se está editando; se muestra el zoom actual del visor.
  const [borrador, setBorrador] = useState<string | null>(null)

  function aplicar() {
    if (borrador === null) {
      return
    }

    const valor = Number.parseInt(borrador, 10)
    setBorrador(null)

    if (Number.isNaN(valor)) {
      return
    }

    const valorLimitado = Math.min(Math.max(valor, minimo), maximo)

    if (valorLimitado !== porcentaje) {
      onCambiar(valorLimitado)
    }
  }

  function manejarTecla(evento: KeyboardEvent<HTMLInputElement>) {
    if (evento.key === 'Enter') {
      evento.currentTarget.blur() // dispara onBlur, que aplica el valor
    }

    if (evento.key === 'Escape') {
      setBorrador(null) // descarta lo escrito y vuelve al zoom actual
    }
  }

  return (
    <label className="zoom-level" title={`Escribe un valor entre ${minimo}% y ${maximo}%`}>
      <input
        className="zoom-input"
        type="text"
        inputMode="numeric"
        value={borrador ?? String(porcentaje)}
        disabled={disabled}
        aria-label={`Nivel de zoom, entre ${minimo}% y ${maximo}%`}
        onFocus={(evento) => evento.currentTarget.select()}
        onChange={(evento) => setBorrador(evento.target.value.replace(/\D/g, '').slice(0, 3))}
        onBlur={aplicar}
        onKeyDown={manejarTecla}
      />
      <span>%</span>
    </label>
  )
}