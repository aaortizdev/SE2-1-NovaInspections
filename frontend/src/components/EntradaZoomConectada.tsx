import { useEvaluationStore } from '../store/useEvaluationStore'
import EntradaZoom from './EntradaZoom'

type Props = {
  minimo: number
  maximo: number
  disabled: boolean
  onCambiar: (porcentaje: number) => void
}

// Se suscribe al zoom del store para que App no se vuelva a renderizar en cada fotograma.
export default function EntradaZoomConectada({ minimo, maximo, disabled, onCambiar }: Props) {
  const porcentaje = useEvaluationStore((s) => s.zoomScale)
  return (
    <EntradaZoom
      porcentaje={porcentaje}
      minimo={minimo}
      maximo={maximo}
      disabled={disabled}
      onCambiar={onCambiar}
    />
  )
}
