# Sprint 1

**Sprint goal:** allow users to prepare an evaluation and inspect the uploaded label.

**Stories:** US-1 Prepare the label evaluation (CA-1 to CA-6) and US-2 View and navigate the label (CA-1 to CA-7), 16 story points in Jira.

## Result

- US-1 completed (CA-1 to CA-6).
- US-2 completed (CA-1 to CA-6); CA-7 (viewer usable during the evaluation) moved to Sprint 2 because it depends on the analysis flow.
- The 1:1 zoom button was rejected (team decision).
- SM-T4 was handled asynchronously: no meetings, confirmations via WhatsApp.
- The increment was developed between Oct 27 and Nov 8, 2026, later than planned (Oct 1–21); the delay was absorbed by moving the Sprint 2 delivery to Nov 22, 2026.
- Tag: [sprint-1](https://github.com/aaortizdev/SE2-1-NovaInspections/releases/tag/sprint-1) (ad8cbe8, PR #3, Nov 14, 2026). Not deployed in Sprint 1; demonstrated locally.
- Acceptance form: pending client signature.

## Backlog and status

| Task | Description | Owner | Status |
|---|---|---|---|
| SM-T1 | GitHub repository, main and feature/* branches with pull-request merges, base environment variables | Ariel, Walter | Done |
| SM-T2 | Navigation shell from Figma (dark sidebar, logo, Detector access) | Ariel, Walter | Done |
| SM-T3 | Validate immutability of the original file under zoom/pan (US-2 CA-6) | Ariel, Walter | Done |
| SM-T4 | Agile ceremonies and QA acceptance checklist on each PR | Ariel | Partial (no meetings; confirmations via WhatsApp) |
| DEV3-T1 | Dropzone with strict .pdf/.png/.jpg filter and visual rejection (US-1 CA-1, CA-2) | Walter, Ariel | Done |
| DEV3-T2 | File card: type icon, name, remove (×) and "Change file" | Walter, Ariel | Done |
| DEV3-T3 | Market/regulation selector: FDA, EFSA, FSA, COFEPRIS, INVIMA, ARCSA (US-1 CA-3) | Walter, Ariel | Done |
| DEV3-T4 | Consent checkbox and gate that keeps "Analizar etiqueta" disabled until file + market + consent (US-1 CA-4 to CA-6) | Walter, Ariel | Done |
| DEV1-T1 | Interactive canvas with react-zoom-pan-pinch, free drag (US-2 CA-1, CA-3) | Genesis | Done |
| DEV1-T2 | Viewer toolbar: file name, −, +, zoom %, FIT (US-2 CA-2, CA-4) | Genesis | Done |
| DEV1-T3 | Multi-page navigation controls (US-2 CA-5) | Genesis | Done |
| DEV2-T4 | Polish floating controls, manual zoom input, file interaction in the viewer | Joseph | Done |
| DEV2-T5 | Overlay layer base ("Layer 2") and green Overlays toggle | Joseph | Done |
| DEV2-T6 | 15 MB limit, toasts for invalid/corrupted files and backend errors, keep terms/market on rejected change, accept .jpeg | Joseph | Done |
| Pre-S2 | PDF-to-canvas pipeline with pdfjs-dist (react-pdf) | — | Done (advanced) |
| Pre-S2 | Global evaluation store (Zustand) | — | Moved to Sprint 2 (PRE-T1/FE-1) |

## Commit history

| Date | SHA | Author | Commit |
|---|---|---|---|
| Oct 27, 2026 | 487221a | StevenMiraba | Add initial frontend and backend integration |
| Oct 29, 2026 | 7604fb6 | aaortizdev | Merge pull request #1 from aaortizdev/feature/MirabaDev1 |
| Oct 31, 2026 | 2a58977 | aaortizdev | feat(frontend): redesign interface with resizable panels and new header |
| Oct 31, 2026 | 665a840 | aaortizdev | feat(US-1): add confirmation overlay |
| Oct 31, 2026 | 46c555c | aaortizdev | feat(upload): toggle file change button visibility using analysis status |
| Nov 8, 2026 | 4b3a45b | GenesisMichilena | chore: instalar react-pdf y react-zoom-pan-pinch |
| Nov 8, 2026 | 0e5fa0e, 25c1028 | GenesisMichilena | feat(visor): implementar zoom, pan y barra de herramientas para US-2 |
| Nov 8, 2026 | a1ea2c9 | GenesisMichilena | feat(frontend): implementar visor interactivo, zoom y barra de herramientas |
| Nov 8, 2026 | 64c2f17 … 138f48a | Joseph Miranda | 9 commits on feature/dev1-Joseph-visor (DEV2-T4 to DEV2-T6, see Section 9) · PR #3 (ad8cbe8, merged Nov 14, 2026) |
