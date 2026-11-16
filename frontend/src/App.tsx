import { useEffect, useState } from 'react'
import type { ChangeEvent, DragEvent, PointerEvent as ReactPointerEvent } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { TransformComponent, TransformWrapper } from 'react-zoom-pan-pinch'
import { Toaster, toast } from 'sonner'
import LimiteDeErrorVisor from './components/LimiteDeErrorVisor'
import CapaHallazgos from './components/CapaHallazgos'
import EntradaZoomConectada from './components/EntradaZoomConectada'
import BannerEstadoEvaluacion from './components/BannerEstadoEvaluacion'
import PanelDictamen from './components/PanelDictamen'
import { useEvaluationStore } from './store/useEvaluationStore'
import { cancelarEvaluacionActiva, enviarYAnalizar } from './services/evaluationFlow'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import './App.css'
import './estado-evaluacion.css'

const TAMANO_MAXIMO_BYTES = 15 * 1024 * 1024
const ESCALA_MINIMA = 0.25 // 25 %
const ESCALA_MAXIMA = 4 // 400 %

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

function App() {
  const archivo = useEvaluationStore((s) => s.fileData)
  const urlArchivo = useEvaluationStore((s) => s.previewUrl)
  const paginaActual = useEvaluationStore((s) => s.pageNumber)
  const numPagesPDF = useEvaluationStore((s) => s.numPages)
  const normativa = useEvaluationStore((s) => s.selectedRegulation)
  const aceptoTerminos = useEvaluationStore((s) => s.termsAccepted)
  const estado = useEvaluationStore((s) => s.evaluationStatus)
  const metricas = useEvaluationStore((s) => s.metrics)
  const setFile = useEvaluationStore((s) => s.setFile)
  const setNormativa = useEvaluationStore((s) => s.setRegulation)
  const setAceptoTerminos = useEvaluationStore((s) => s.setTermsAccepted)
  const setZoomPorcentaje = useEvaluationStore((s) => s.setZoomScale)
  const setPaginaActual = useEvaluationStore((s) => s.setPageNumber)
  const setNumPagesPDF = useEvaluationStore((s) => s.setNumPages)

  const [mostrarOverlays, setMostrarOverlays] = useState(true)
  const [mostrarConfirmacionBorrado, setMostrarConfirmacionBorrado] = useState(false)
  const enCurso = estado === 'pending' || estado === 'in_progress'

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

      // La URL de vista previa se crea en el mismo momento que se guarda el archivo (ver
  // validarYSeleccionarArchivo), así archivo y URL cambian juntos en un solo render.
  // Este efecto solo libera la URL anterior cuando deja de usarse.
  useEffect(() => {
    if (!urlArchivo) {
      return
    }

    return () => {
      URL.revokeObjectURL(urlArchivo)
    }
  }, [urlArchivo])

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

    // Un archivo nuevo cancela cualquier análisis anterior y limpia sus resultados.
    cancelarEvaluacionActiva()
    setFile(archivoSeleccionado, URL.createObjectURL(archivoSeleccionado))
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
    if (enCurso || estado === 'completed') {
      setMostrarConfirmacionBorrado(true)
      return
    }
    ejecutarBorrado()
  }

  function ejecutarBorrado() {
    cancelarEvaluacionActiva()
    useEvaluationStore.getState().clearAll()
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

  function enviarEvaluacion() {
    void enviarYAnalizar()
  }

  function cambiarNormativa(valor: string) {
    // Cambiar la normativa invalida un resultado o error anterior.
    if (estado === 'completed' || estado === 'error') {
      cancelarEvaluacionActiva()
      useEvaluationStore.getState().resetEvaluation()
    }
    setNormativa(valor)
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

                        {!enCurso && (
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
                        <p>
                          {enCurso
                            ? '¿Seguro que deseas cancelar el proceso?'
                            : 'Se perderán los resultados del análisis. ¿Continuar?'}
                        </p>
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
                  disabled={enCurso}
                  onChange={(evento) => cambiarNormativa(evento.target.value)}
                >
                  <option value="" disabled>
                    Elige la normativa de análisis
                  </option>

                  <option value="estados_unidos">Estados Unidos (FDA)</option>
                  <option value="ecuador">Ecuador (ARCSA)</option>
                  <option value="union_europea" disabled>Unión Europea (EFSA) · Próximamente</option>
                  <option value="reino_unido" disabled>Reino Unido (FSA) · Próximamente</option>
                  <option value="mexico" disabled>México (COFEPRIS) · Próximamente</option>
                  <option value="colombia" disabled>Colombia (INVIMA) · Próximamente</option>
                </select>
              </div>

              {estado === 'completed' && metricas && (
                <section className="metrics-section">
                  <h3 className="section-label">▥ &nbsp; MÉTRICAS / RESUMEN</h3>

                  <div className="metrics-grid">
                    <div className="metric-card">
                      <span>TOTAL</span>
                      <strong>{metricas.total}</strong>
                    </div>

                    <div className="metric-card">
                      <span>CRÍTICOS</span>
                      <strong className="metric-critical">{metricas.criticos}</strong>
                    </div>

                    <div className="metric-card">
                      <span>AVISOS</span>
                      <strong className="metric-warning">{metricas.advertencias}</strong>
                    </div>

                    <div className="metric-card">
                      <span>CONFORMES</span>
                      <strong className="metric-ok">{metricas.conformes}</strong>
                    </div>
                  </div>
                </section>
              )}

              <div className="consent-section">
                {estado === 'idle' ? (
                  <>
                    <label className="consent-label">
                      <input
                        type="checkbox"
                        checked={aceptoTerminos}
                        onChange={(evento) => {
                          setAceptoTerminos(evento.target.checked)
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
                  <BannerEstadoEvaluacion />
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
            minScale={ESCALA_MINIMA}
            maxScale={ESCALA_MAXIMA}
            onTransform={(_, state) => setZoomPorcentaje(Math.round(state.scale * 100))}
          >
            {({ zoomIn, zoomOut, resetTransform, centerView }) => (
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

                    <button
                      type="button"
                      className={`toolbar-btn overlay-btn ${mostrarOverlays ? 'active' : ''}`}
                      onClick={() => setMostrarOverlays((visible) => !visible)}
                      disabled={!archivo}
                      aria-pressed={mostrarOverlays}
                      title={mostrarOverlays ? 'Ocultar overlays' : 'Mostrar overlays'}
                    >
                      Overlays
                    </button>

                  
                    {archivo?.type === 'application/pdf' && (
                      <>
                        <button
                          type="button"
                          className="toolbar-btn"
                          onClick={() => {
                            setPaginaActual(paginaActual - 1)
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
                            setPaginaActual(Math.min(numPagesPDF, paginaActual + 1))
                            resetTransform()
                          }}
                          disabled={paginaActual === numPagesPDF}
                          aria-label="Página siguiente"
                        >
                          Siguiente
                        </button>
                      </>
                    )}
                    <EntradaZoomConectada
                      minimo={ESCALA_MINIMA * 100}
                      maximo={ESCALA_MAXIMA * 100}
                      disabled={!archivo}
                      onCambiar={(porcentaje) => centerView(porcentaje / 100)}
                    />
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

                                        {archivo && urlArchivo && (
                      // Escenario: mide exactamente lo mismo que la etiqueta, para que
                      // la Capa 2 quede pegada a la imagen o al PDF y no a todo el visor.
                      <div className="label-stage">
                        {/* Capa 1: la etiqueta (imagen o PDF) */}
                        {archivo.type.startsWith('image/') && (
                          <img
                            className="label-preview"
                            src={urlArchivo}
                            alt={`Vista previa de ${archivo.name}`}
                            onError={() => manejarArchivoDanado('imagen')}
                          />
                        )}

                        {archivo.type === 'application/pdf' && (
                          <LimiteDeErrorVisor key={urlArchivo} onError={() => manejarArchivoDanado('PDF')}>
                            <Document
                              file={urlArchivo}
                              onLoadSuccess={({ numPages }) => {
                                setNumPagesPDF(numPages)
                                setPaginaActual(Math.min(useEvaluationStore.getState().pageNumber, numPages))
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

                        {/* Capa 2: overlays de hallazgos */}
                        {mostrarOverlays && (
                          <CapaHallazgos />
                        )}
                      </div>
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

              <PanelDictamen />
            </aside>
          </>
        )}
      </div>
    </div>
  )
}

export default App
