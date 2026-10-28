import { useEffect, useState } from 'react'
import type { ChangeEvent, DragEvent } from 'react'
import './App.css'

function App() {
  const [archivo, setArchivo] = useState<File | null>(null)
  const [urlArchivo, setUrlArchivo] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [normativa, setNormativa] = useState('')
  const [aceptoTerminos, setAceptoTerminos] = useState(false)
  const [mensajeAnalisis, setMensajeAnalisis] = useState('')

  useEffect(() => {
    if (!archivo) {
      setUrlArchivo(null)
      return
    }

    const url = URL.createObjectURL(archivo)
    setUrlArchivo(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [archivo])

  function validarYSeleccionarArchivo(archivoSeleccionado: File) {
    const tiposPermitidos = [
      'application/pdf',
      'image/png',
      'image/jpeg',
    ]

    if (!tiposPermitidos.includes(archivoSeleccionado.type)) {
      setError('Formato no permitido. Selecciona un archivo PDF, PNG o JPG.')
      return
    }

    setError('')
    setArchivo(archivoSeleccionado)
  }

  function manejarArchivo(evento: ChangeEvent<HTMLInputElement>) {
    const archivoSeleccionado = evento.target.files?.[0]

    if (archivoSeleccionado) {
      validarYSeleccionarArchivo(archivoSeleccionado)
    }

    // Permite seleccionar nuevamente el mismo archivo.
    evento.target.value = ''
  }

  function manejarArchivoArrastrado(
    evento: DragEvent<HTMLLabelElement>,
  ) {
    evento.preventDefault()

    const archivoArrastrado = evento.dataTransfer.files[0]

    if (archivoArrastrado) {
      validarYSeleccionarArchivo(archivoArrastrado)
    }
  }

  function quitarArchivo() {
    setArchivo(null)
    setError('')
  }

  async function enviarEvaluacion() {
    if (!archivo || !normativa || !aceptoTerminos) {
      return
    }

    const datos = new FormData()

    datos.append('archivo', archivo)
    datos.append('normativa', normativa)
    datos.append('acepto_terminos', String(aceptoTerminos))

    setMensajeAnalisis('Enviando etiqueta...')

    try {
      const respuesta = await fetch('http://127.0.0.1:8000/evaluaciones', {
        method: 'POST',
        body: datos,
      })

      const resultado = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeAnalisis(resultado.detail || 'No se pudo enviar la etiqueta.')
        return
      }

      setMensajeAnalisis(`${resultado.mensaje} ${resultado.estado}`)
    } catch {
      setMensajeAnalisis(
        'No se pudo conectar con el backend. Comprueba que esté ejecutándose.',
      )
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-name">
            Solinal<span className="logo-dot">.</span>
          </span>
          <span className="logo-subtitle">Etiqueta</span>
        </div>

        <div className="header-actions">
          <span className="language">🇪🇸 ES</span>
          <span className="user-icon">👤</span>
        </div>
      </header>

      <div className="workspace">
        <nav className="sidebar">
          <div className="sidebar-item">
            <span className="sidebar-icon">⌂</span>
            <span>Inicio</span>
          </div>

          <div className="sidebar-item active">
            <span className="sidebar-icon">⬡</span>
            <span>Detector</span>
          </div>

          <div className="sidebar-item">
            <span className="sidebar-icon">▤</span>
            <span>Tabla nutricional</span>
          </div>
        </nav>

        <aside className="left-panel">
          <p className="step">PASO 01</p>

          <h2>
            Cargar <span>etiqueta</span>
          </h2>

          {!archivo ? (
            <label
              className="upload-area"
              onDragOver={(evento) => evento.preventDefault()}
              onDrop={manejarArchivoArrastrado}
            >
              <span className="upload-icon">↑</span>

              <strong>Arrastra el archivo</strong>
              <span className="upload-hint">o haz clic para seleccionar</span>

              <div className="file-formats">
                <span>PDF</span>
                <span>PNG</span>
                <span>JPG</span>
              </div>

              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={manejarArchivo}
                hidden
              />
            </label>
          ) : (
            <>
              <div className="file-card">
                <div className="file-icon">
                  {archivo.type === 'application/pdf' ? 'PDF' : 'IMG'}
                </div>

                <div className="file-information">
                  <strong>{archivo.name}</strong>
                  <span>Etiqueta cargada</span>
                </div>

                <button
                  type="button"
                  className="remove-file"
                  onClick={quitarArchivo}
                  aria-label="Quitar archivo"
                >
                  ×
                </button>
              </div>
            </>
          )}

          {error && <p className="file-error">{error}</p>}

          <div className="regulation-section">
            <label htmlFor="normativa" className="section-label">
              NORMATIVA DE ANÁLISIS
            </label>

            <select
              id="normativa"
              className="regulation-select"
              value={normativa}
              onChange={(evento) => {
                setNormativa(evento.target.value)
                setMensajeAnalisis('')
              }}
            >
              <option value="" disabled>
                Elige la normativa de análisis
              </option>

              <option value="estados_unidos">Estados Unidos (FDA)</option>
              <option value="union_europea">Unión Europea (EFSA)</option>
              <option value="reino_unido">Reino Unido (FSA)</option>
              <option value="mexico">México (COFEPRIS)</option>
              <option value="colombia">Colombia (INVIMA)</option>
              <option value="ecuador">Ecuador (ARCSA)</option>
            </select>
          </div>
          {false && (
          <section className="metrics-section">
            <h3 className="section-label">▥ &nbsp; MÉTRICAS / RESUMEN</h3>

            <div className="metrics-grid">
              <div className="metric-card">
                <span>TOTAL</span>
                <strong>0</strong>
              </div>

              <div className="metric-card">
                <span>CRÍTICOS</span>
                <strong className="metric-critical">0</strong>
              </div>

              <div className="metric-card">
                <span>AVISOS</span>
                <strong className="metric-warning">0</strong>
              </div>

              <div className="metric-card">
                <span>CONFORMES</span>
                <strong className="metric-ok">0</strong>
              </div>
            </div>
          </section>
          )}
          <div className="consent-section">
            <label className="consent-label">
              <input
                type="checkbox"
                checked={aceptoTerminos}
                onChange={(evento) => {
                  setAceptoTerminos(evento.target.checked)
                  setMensajeAnalisis('')
                }}
              />

              <span>
                He leído y acepto los{' '}
                <a
                  href={`${import.meta.env.BASE_URL}terminos.html`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  términos y condiciones
                </a>
                . Entiendo que los resultados son informativos y no constituyen una
                certificación legal.
              </span>
            </label>

            <button
              type="button"
              className="analyze-button"
              disabled={!archivo || !normativa || !aceptoTerminos}
              onClick={enviarEvaluacion}
            >
              Analizar etiqueta
            </button>

            {mensajeAnalisis && (
              <p className="analysis-message" role="status">
                {mensajeAnalisis}
              </p>
            )}
          </div>
        </aside>

        <main className="viewer-panel">
          <div className="viewer-toolbar">
            VISOR · {archivo ? archivo.name : 'SIN ARCHIVO'}
          </div>

          <div className="viewer-content">
            {!archivo && <p>La etiqueta aparecerá aquí</p>}

            {archivo && urlArchivo && archivo.type.startsWith('image/') && (
              <img
                className="label-preview"
                src={urlArchivo}
                alt={`Vista previa de ${archivo.name}`}
              />
            )}

            {archivo && urlArchivo && archivo.type === 'application/pdf' && (
              <iframe
                className="pdf-preview"
                src={urlArchivo}
                title={`Vista previa de ${archivo.name}`}
              />
            )}
          </div>
        </main>

        <aside className="right-panel">
          <p className="step">PASO 03</p>

          <h2>
            Dictamen <span>regulatorio</span>
          </h2>

          <p className="placeholder-text">
            Los resultados aparecerán aquí.
          </p>
        </aside>
      </div>
    </div>
  )
}

export default App
