import { create } from 'zustand'
import type { EstadoEvaluacion, Hallazgo, Resumen } from '../types/evaluation'

type State = {
  fileData: File | null
  fileName: string
  fileType: string
  previewUrl: string | null
  selectedRegulation: string
  termsAccepted: boolean
  zoomScale: number // porcentaje (100 = 100 %)
  pageNumber: number
  numPages: number
  evaluationId: string | null
  evaluationStatus: EstadoEvaluacion
  errorMessage: string
  findings: Hallazgo[]
  metrics: Resumen | null
  processWarnings: string[]
  selectedFindingId: string | null
}

type Actions = {
  setFile: (file: File, previewUrl: string) => void
  setRegulation: (regulation: string) => void
  setTermsAccepted: (accepted: boolean) => void
  setZoomScale: (scale: number) => void
  setPageNumber: (page: number) => void
  setNumPages: (pages: number) => void
  beginEvaluation: () => void
  setEvaluationId: (id: string | null) => void
  setStatus: (status: EstadoEvaluacion, errorMessage?: string) => void
  setResults: (findings: Hallazgo[], metrics: Resumen | null, warnings: string[]) => void
  selectFinding: (id: string | null) => void
  resetEvaluation: () => void
  clearAll: () => void
}

const evaluacionInicial = {
  evaluationId: null,
  evaluationStatus: 'idle' as EstadoEvaluacion,
  errorMessage: '',
  findings: [] as Hallazgo[],
  metrics: null as Resumen | null,
  processWarnings: [] as string[],
  selectedFindingId: null as string | null,
}

const visorInicial = {
  zoomScale: 100,
  pageNumber: 1,
  numPages: 1,
}

const estadoInicial: State = {
  fileData: null,
  fileName: '',
  fileType: '',
  previewUrl: null,
  selectedRegulation: '',
  termsAccepted: false,
  ...visorInicial,
  ...evaluacionInicial,
}

export const useEvaluationStore = create<State & Actions>((set) => ({
  ...estadoInicial,

  setFile: (file, previewUrl) =>
    set({
      fileData: file,
      fileName: file.name,
      fileType: file.type,
      previewUrl,
      ...visorInicial,
      ...evaluacionInicial,
    }),
  setRegulation: (selectedRegulation) => set({ selectedRegulation }),
  setTermsAccepted: (termsAccepted) => set({ termsAccepted }),
  setZoomScale: (zoomScale) => set({ zoomScale }),
  setPageNumber: (page) => set({ pageNumber: Math.max(1, page) }),
  setNumPages: (numPages) => set({ numPages }),

  // Limpia resultados previos y marca el envío como "pending".
  beginEvaluation: () =>
    set({ ...evaluacionInicial, evaluationStatus: 'pending' }),
  setEvaluationId: (evaluationId) => set({ evaluationId }),
  setStatus: (evaluationStatus, errorMessage = '') => set({ evaluationStatus, errorMessage }),
  setResults: (findings, metrics, processWarnings) =>
    set({
      findings,
      metrics,
      processWarnings,
      evaluationStatus: 'completed',
      errorMessage: '',
      selectedFindingId: null,
    }),
  selectFinding: (selectedFindingId) => set({ selectedFindingId }),
  resetEvaluation: () => set({ ...evaluacionInicial }),
  clearAll: () => set({ ...estadoInicial }),
}))
