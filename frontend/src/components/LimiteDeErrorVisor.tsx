import { Component } from 'react'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
  onError: (error: Error) => void
}

type State = {
  tieneError: boolean
}

// react-pdf lanza el error de un PDF inválido durante el render de <Document>.
// Sin este límite, React desmonta toda la app y la pantalla queda en blanco.
// Los límites de error en React siguen requiriendo un componente de clase.
export default class LimiteDeErrorVisor extends Component<Props, State> {
  state: State = { tieneError: false }

  static getDerivedStateFromError(): State {
    return { tieneError: true }
  }

  componentDidCatch(error: Error) {
    this.props.onError(error)
  }

  render() {
    return this.state.tieneError ? null : this.props.children
  }
}