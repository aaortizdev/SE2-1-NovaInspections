import { useEffect, useState } from 'react'
import type { ChangeEvent, DragEvent, PointerEvent as ReactPointerEvent } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { TransformComponent, TransformWrapper } from 'react-zoom-pan-pinch'
import { Toaster, toast } from 'sonner'
import LimiteDeErrorVisor from './components/LimiteDeErrorVisor'                         
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import './App.css'

const TAMANO_MAXIMO_BYTES = 15 * 1024 * 1024

// FastAPI responde los errores como {"detail": "..."}; en errores de validación (422)
// "detail" llega como una lista de objetos con "msg". Devolvemos solo el texto legible.
async function obtenerMensajeDeError(respuesta: Response) {
  const mensajePorDefecto = 'No se pudo enviar la etiqueta. Inténtalo de nuevo.'

  try {
    const cuerpo = await respuesta.json()
    const detalle = cuerpo?.detail

    if (typeof detalle === 'string' && detalle.trim()) {
      return detalle
    }

    if (Array.isArray(detalle) && detalle.length > 0) {
      return detalle.map((item) => item?.msg).filter(Boolean).join(' ') || mensajePorDefecto
    }
  } catch {
    // La respuesta no era JSON (por ejemplo, una página de error del servidor).
  }

  return mensajePorDefecto
}



pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

function App() {
  const [archivo, setArchivo] = useState<File | null>(null)
  const [vistaPrevia, setVistaPrevia] = useState<{ archivo: File; url: string } | null>(null)
  const [zoomPorcentaje, setZoomPorcentaje] = useState(100)
  const [numPagesPDF, setNumPagesPDF] = useState(1)
  const [paginaActual, setPaginaActual] = useState(1)
  const [normativa, setNormativa] = useState('')
  const [aceptoTerminos, setAceptoTerminos] = useState(false)
  const [mensajeAnalisis, setMensajeAnalisis] = useState('')
  const [mostrarConfirmacionBorrado, setMostrarConfirmacionBorrado] = useState(false)

  const [anchoIzquierdo, setAnchoIzquierdo] = useState(350)
  const [anchoDerecho, setAnchoDerecho] = useState(390)
  const [panelDerechoAbierto, setPanelDerechoAbierto] = useState(true)
  const [panelIzquierdoAbierto, setPanelIzquierdoAbierto] = useState(true)

  function limitar(valor: number, minimo: number, maximo: number) {
    return Math.min(Math.max(valor, minimo), maximo)
  }

  function iniciarRedimension(
    evento: ReactPointerEvent<HTMLDivElement>,
    lado: 'izquierdo' | 'derecho',
  ) {
    evento.preventDefault()

    const xInicial = evento.clientX
    const anchoInicial = lado === 'izquierdo' ? anchoIzquierdo : anchoDerecho

    document.body.classList.add('resizing')

    function mover(e: PointerEvent) {
      const desplazamiento = e.clientX - xInicial

      if (lado === 'izquierdo') {
        setAnchoIzquierdo(limitar(anchoInicial + desplazamiento, 280, 560))
      } else {
        // El panel derecho crece al arrastrar hacia la izquierda.
        setAnchoDerecho(limitar(anchoInicial - desplazamiento, 300, 640))
      }
    }

    function soltar() {
      document.body.classList.remove('resizing')
      window.removeEventListener('pointermove', mover)
      window.removeEventListener('pointerup', soltar)
    }

    window.addEventListener('pointermove', mover)
    window.addEventListener('pointerup', soltar)
  }

  const columnasWorkspace = [
    '64px',
    ...(panelIzquierdoAbierto ? [`${anchoIzquierdo}px`, '1px'] : []),
    'minmax(300px, 1fr)',
    ...(panelDerechoAbierto ? ['1px', `${anchoDerecho}px`] : []),
  ].join(' ')

    useEffect(() => {
    if (!archivo) {
      setVistaPrevia(null)
      return
    }

    const url = URL.createObjectURL(archivo)
    setVistaPrevia({ archivo, url })

    return () => {
      URL.revokeObjectURL(url)
    }
    }, [archivo])
    const urlArchivo = vistaPrevia?.archivo === archivo ? vistaPrevia.url : null
    
   function validarYSeleccionarArchivo(archivoSeleccionado: File): boolean {
    const tiposPermitidos = [
      'application/pdf',
      'image/png',
      'image/jpeg',
    ]

    if (!tiposPermitidos.includes(archivoSeleccionado.type)) {
      toast.error('Formato no permitido. Selecciona un archivo PDF, PNG o JPG.')
      return false
    }

    if (archivoSeleccionado.size > TAMANO_MAXIMO_BYTES) {
      toast.error('El archivo no puede superar los 15 MB.')
      return false
    }

    setZoomPorcentaje(100)
    setZoomPorcentaje(100)
    setNumPagesPDF(1)
    setPaginaActual(1)
    setArchivo(archivoSeleccionado)
    return true
  }

  function manejarArchivo(evento: ChangeEvent<HTMLInputElement>): boolean {
    const archivoSeleccionado = evento.target.files?.[0]
    const aceptado = archivoSeleccionado
      ? validarYSeleccionarArchivo(archivoSeleccionado)
      : false

    // Permite seleccionar nuevamente el mismo archivo.
    evento.target.value = ''

    return aceptado
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

  function intentarQuitarArchivo() {
    if (mensajeAnalisis.includes('Pendiente IA')) {
      setMostrarConfirmacionBorrado(true)
      return
    }
    ejecutarBorrado()
  }

  function ejecutarBorrado() {
    setArchivo(null)
    setZoomPorcentaje(100)
    setNumPagesPDF(1)
    setPaginaActual(1)
    setMensajeAnalisis('')
    setAceptoTerminos(false)
    setNormativa('')
    setMostrarConfirmacionBorrado(false)
  }

  function manejarArchivoDanado(tipo: 'PDF' | 'imagen') {
    // El id fijo evita que se apilen toasts repetidos si el evento se dispara varias veces.
    toast.error(
      `No se pudo leer ${tipo === 'PDF' ? 'el PDF' : 'la imagen'}. Es posible que el archivo esté dañado.`,
      { id: 'archivo-danado' },
    )
    ejecutarBorrado()
  }

  function cancelarBorrado() {
    setMostrarConfirmacionBorrado(false)
  }

  async function enviarEvaluacion() {
    if (!archivo || !normativa || !aceptoTerminos) {
      return
    }

    const datos = new FormData()

    datos.append('archivo', archivo)
    datos.append('normativa', normativa)
    datos.append('acepto_terminos', String(aceptoTerminos))

    setMensajeAnalisis('')
    // Mismo id en loading, error y éxito: sonner reemplaza el toast en lugar de apilarlos.
    toast.loading('Enviando etiqueta...', { id: 'analisis' })

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      const urlLimpia = API_URL.replace(/\/+$/, '')
      const urlEvaluaciones = `${urlLimpia}/evaluaciones`

      console.log('URL a la que se intenta conectar:', urlEvaluaciones)

      const respuesta = await fetch(urlEvaluaciones, {
        method: 'POST',
        body: datos,
      })

            if (!respuesta.ok) {
        const mensajeError = await obtenerMensajeDeError(respuesta)
        console.error(`Error HTTP ${respuesta.status}:`, mensajeError)
        toast.error(mensajeError, { id: 'analisis' })
        return
      }

      const resultado = await respuesta.json()
      toast.success(resultado.mensaje, { id: 'analisis' })
      setMensajeAnalisis(`${resultado.mensaje} ${resultado.estado}`)
    } catch (error) {
      console.error(error)
      toast.error('No se pudo conectar con el backend. Comprueba que esté ejecutándose.', {
        id: 'analisis',
      })
    }
  }

  return (
    <div className="app">
      <Toaster position="top-right" richColors closeButton /> 
      <header className="header">
        <div className="brand">
          <img
            className="brand-icon"
            src={`${import.meta.env.BASE_URL}logo-solinal.svg`}
            alt=""
          />

          <div className="logo">
            <span className="logo-name">
              Solinal<span className="logo-dot" />
            </span>
            <span className="logo-subtitle">Etiqueta</span>
          </div>
        </div>

        <div className="header-actions">
          <button type="button" className="language" aria-label="Idioma: Español">
            <svg className="flag" viewBox="0 0 24 16" aria-hidden="true">
              <rect width="24" height="16" rx="2.5" fill="#c60b1e" />
              <rect y="4" width="24" height="8" fill="#ffc400" />
            </svg>
            <span>ES</span>
          </button>

          <button type="button" className="user-icon" aria-label="Cuenta de usuario">
            <svg
              viewBox="0 0 24 24"
              width="18"
              height="18"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
            </svg>
          </button>
        </div>
      </header>

      <div className="workspace" style={{ gridTemplateColumns: columnasWorkspace }}>
        <nav className="sidebar">
          <div className="sidebar-item active">
            <span className="sidebar-icon">⬡</span>
            <span>Detector</span>
          </div>
        </nav>

        {panelIzquierdoAbierto && (
          <>
            <aside className="left-panel">
              <div className="panel-header">
                <h2>
                  Cargar <span>etiqueta</span>
                </h2>

                <button
                  type="button"
                  className="panel-toggle"
                  onClick={() => setPanelIzquierdoAbierto(false)}
                  aria-label="Ocultar barra lateral"
                  title="Ocultar barra lateral"
                >
                  <span className="panel-toggle-icon left" />
                </button>
              </div>

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
                  <div className="file-card-container" style={{ position: 'relative' }}>
                    <div className={`file-card ${mostrarConfirmacionBorrado ? 'blur-effect' : ''}`}>
                      <div className="file-icon">
                        {archivo.type === 'application/pdf' ? 'PDF' : 'IMG'}
                      </div>

                      <div
                        className="file-information"
                        style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}
                      >
                        <strong>{archivo.name}</strong>
                        <span>Etiqueta cargada</span>

                        {!mensajeAnalisis.includes('Pendiente IA') && (
                          <label
                            className="upload-button"
                            style={{
                              padding: '6px 10px',
                              fontSize: '11px',
                              width: 'fit-content',
                              marginTop: '4px',
                            }}
                          >
                            Cambiar archivo
                            <input
                              type="file"
                              accept=".pdf,.png,.jpg,.jpeg"
                              onChange={(evento) => {
                                // Si el archivo nuevo se rechaza, se conservan el
                                // archivo actual, los términos y la normativa.
                                if (!manejarArchivo(evento)) {
                                  return
                                }

                                setMensajeAnalisis('')
                                setAceptoTerminos(false)
                                setNormativa('')
                                setMostrarConfirmacionBorrado(false)
                              }}
                              hidden
                            />
                          </label>
                        )}
                      </div>

                      <button
                        type="button"
                        className="remove-file"
                        onClick={intentarQuitarArchivo}
                        aria-label="Quitar archivo"
                      >
                        ×
                      </button>
                    </div>

                    {mostrarConfirmacionBorrado && (
                      <div className="confirm-overlay">
                        <p>¿Seguro que deseas cancelar el proceso?</p>
                        <div className="confirm-actions">
                          <button type="button" className="btn-cancelar" onClick={cancelarBorrado}>
                            Cancelar
                          </button>
                          <button type="button" className="btn-continuar" onClick={ejecutarBorrado}>
                            Continuar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}

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
                {!mensajeAnalisis.includes('Pendiente IA') ? (
                  <>
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
                  </>
                ) : (
                  /* Vista cuando el análisis ya está en curso */
                  <p className="analysis-message" style={{ color: '#009b88', fontWeight: 'bold', marginTop: 0 }} role="status">
                    {mensajeAnalisis}
                  </p>
                )}
              </div>
            </aside>

            <div
              className="resizer"
              role="separator"
              aria-orientation="vertical"
              aria-label="Redimensionar panel de carga"
              onPointerDown={(evento) => iniciarRedimension(evento, 'izquierdo')}
            />
          </>
        )}

        <main className="viewer-panel">
          <TransformWrapper
            key={urlArchivo ?? 'sin-archivo'}
            initialScale={1}
            minScale={0.25}
            maxScale={4}
            onTransform={(_, state) => setZoomPorcentaje(Math.round(state.scale * 100))}
          >
            {({ zoomIn, zoomOut, resetTransform }) => (
              <>
                <div className="viewer-toolbar">
                  <div className="viewer-toolbar-left">
                    {!panelIzquierdoAbierto && (
                      <button
                        type="button"
                        className="panel-toggle"
                        onClick={() => setPanelIzquierdoAbierto(true)}
                        aria-label="Mostrar barra lateral"
                        title="Mostrar barra lateral"
                      >
                        <span className="panel-toggle-icon left" />
                      </button>
                    )}
                    <span>VISOR · {archivo ? archivo.name : 'SIN ARCHIVO'}</span>
                  </div>

                  <div className="viewer-controls">
                    <button
                      type="button"
                      className="toolbar-btn"
                      onClick={() => zoomOut()}
                      disabled={!archivo}
                      aria-label="Alejar"
                    >
                      -
                    </button>
                    <button
                      type="button"
                      className="toolbar-btn"
                      onClick={() => zoomIn()}
                      disabled={!archivo}
                      aria-label="Acercar"
                    >
                      +
                    </button>
                    <button
                      type="button"
                      className="toolbar-btn fit-btn"
                      onClick={() => resetTransform()}
                      disabled={!archivo}
                    >
                      FIT
                    </button>
                    {archivo?.type === 'application/pdf' && (
                      <>
                        <button
                          type="button"
                          className="toolbar-btn"
                          onClick={() => {
                            setPaginaActual((pagina) => Math.max(1, pagina - 1))
                            resetTransform()
                          }}
                          disabled={paginaActual === 1}
                          aria-label="Página anterior"
                        >
                          Anterior
                        </button>
                        <span className="page-level">
                          Pág. {paginaActual} de {numPagesPDF}
                        </span>
                        <button
                          type="button"
                          className="toolbar-btn"
                          onClick={() => {
                            setPaginaActual((pagina) => Math.min(numPagesPDF, pagina + 1))
                            resetTransform()
                          }}
                          disabled={paginaActual === numPagesPDF}
                          aria-label="Página siguiente"
                        >
                          Siguiente
                        </button>
                      </>
                    )}
                    <span className="zoom-level">{zoomPorcentaje}%</span>
                  </div>

                  {!panelDerechoAbierto && (
                    <button
                      type="button"
                      className="panel-toggle"
                      onClick={() => setPanelDerechoAbierto(true)}
                      aria-label="Mostrar barra lateral"
                      title="Mostrar barra lateral"
                    >
                      <span className="panel-toggle-icon" />
                    </button>
                  )}
                </div>

                <div className="viewer-content">
                  <TransformComponent wrapperClass="viewer-canvas" contentClass="viewer-canvas-content">
                    {!archivo && <p>La etiqueta aparecerá aquí</p>}

                    {archivo && urlArchivo && archivo.type.startsWith('image/') && (
                      <img
                        className="label-preview"
                        src={urlArchivo}
                        alt={`Vista previa de ${archivo.name}`}
                        onError={() => manejarArchivoDanado('imagen')}
                      />
                    )}

                    {archivo && urlArchivo && archivo.type === 'application/pdf' && (
                      <LimiteDeErrorVisor key={urlArchivo} onError={() => manejarArchivoDanado('PDF')}>
                        <Document
                          file={urlArchivo}
                          onLoadSuccess={({ numPages }) => {
                            setNumPagesPDF(numPages)
                            setPaginaActual((pagina) => Math.min(pagina, numPages))
                          }}
                          onLoadError={() => manejarArchivoDanado('PDF')}
                        >
                          <Page
                            key={`pagina-${paginaActual}`}
                            className="pdf-page"
                            pageNumber={paginaActual}
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                          />
                        </Document>
                      </LimiteDeErrorVisor>
                    )}
                  </TransformComponent>
                </div>
              </>
            )}
          </TransformWrapper>
        </main>

        {panelDerechoAbierto && (
          <>
            <div
              className="resizer"
              role="separator"
              aria-orientation="vertical"
              aria-label="Redimensionar panel de resultados"
              onPointerDown={(evento) => iniciarRedimension(evento, 'derecho')}
            />

            <aside className="right-panel">
              <div className="panel-header">
                <h2>
                  Dictamen <span>regulatorio</span>
                </h2>

                <button
                  type="button"
                  className="panel-toggle"
                  onClick={() => setPanelDerechoAbierto(false)}
                  aria-label="Ocultar barra lateral"
                  title="Ocultar barra lateral"
                >
                  <span className="panel-toggle-icon" />
                </button>
              </div>

              <p className="placeholder-text">Los resultados aparecerán aquí.</p>
            </aside>
          </>
        )}
      </div>
    </div>
  )
}

export default App
