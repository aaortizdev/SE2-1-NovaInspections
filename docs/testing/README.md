# Test plan, test cases and evidence (Sprints 1–2)

How to run the automated checks:

```bash
cd backend && pytest                      # 53 unit and integration tests
cd backend && pytest --cov=main --cov=models --cov=services --cov-report=term
cd frontend && npm run lint && npm run build
```

GitHub Actions runs the same checks on every push to main and feature/** and on every pull request to main ([.github/workflows/ci.yml](../../.github/workflows/ci.yml)).

## Risk matrix

Scale reused from the class matrix: probability (P) and impact (I) from 1 to 6, exposure E = P × I. E ≥ 20 is High, 10–19 Medium, ≤ 9 Low.

| ID | Story | Risk | Origin | P | I | E | Priority |
|---|---|---|---|---|---|---|---|
| R-01 | US-1 | User cannot upload a file in a valid format, or an invalid or corrupted file is accepted or crashes the page | Class TC-01, updated (DEF-01, DEF-02) | 4 | 5 | 20 | High |
| R-02 | US-1 | The selected market (regulation) is not applied or not displayed | Class TC-02, updated (only Ecuador active) | 2 | 4 | 8 | Low |
| R-03 | US-1 | Analyze button is not enabled after file, market and consent, or is enabled without them | Class TC-03 | 2 | 5 | 10 | Medium |
| R-04 | US-2 | Label not visible or distorted in the viewer; finding boxes misaligned with the label | Class TC-04, updated (Sprint 2 boxes) | 4 | 5 | 20 | High |
| R-05 | US-2 | Zoom in/out does not work properly | Class TC-05 | 3 | 5 | 15 | Medium |
| R-06 | US-2 | Pan does not work when zoomed in | Class TC-06 | 2 | 4 | 8 | Low |
| R-07 | US-2 | FIT adjusts the label to incorrect dimensions | Class TC-07 | 2 | 4 | 8 | Low |
| R-08 | US-2 | Viewer operations change the original uploaded file (CA-6) | Sprint 1 | 1 | 5 | 5 | Low |
| R-09 | US-3 | AI timeout, quota (429/503) or outage leaves the evaluation stuck | Sprint 2 | 5 | 6 | 30 | High |
| R-10 | US-3, US-6 | Results of a previous evaluation are shown for the current one | Sprint 2 | 3 | 6 | 18 | Medium |
| R-11 | US-4 | AI returns malformed JSON, unknown rule IDs or out-of-range boxes | Sprint 2 | 4 | 5 | 20 | High |
| R-12 | US-4 | Rules or regulatory citations are wrong or invented | Sprint 2 | 4 | 6 | 24 | High |
| R-13 | US-5 | AI findings do not match the expected results of the dataset | Sprint 2 | 4 | 6 | 24 | High |
| R-14 | US-6 | Displayed status does not match the backend status | Sprint 2 | 3 | 4 | 12 | Medium |
| R-15 | Cross | Zustand migration breaks Sprint 1 features (regression) | Sprint 2 | 4 | 5 | 20 | High |
| R-16 | Cross | Deployment configuration (CORS, VITE_API_URL, AI_MODE) breaks the deployed app | Sprint 2 | 4 | 6 | 24 | High |

## Traceability

| Story | Risk | Acceptance criteria | Test cases |
|---|---|---|---|
| US-1 | High (R-01) | CA-1 valid formats · CA-2 rejection of invalid files | TC-01 – TC-07 · IT-01 – IT-06 · UT-01, UT-02 (planned) |
| US-1 | Medium, Low (R-03, R-02) | CA-3 market · CA-4 consent · CA-5/CA-6 Analyze gate | TC-08 (decision table), TC-09, TC-10, TC-25 |
| US-2 | High (R-04) | CA-1 viewer and finding boxes | TC-01, TC-15, TC-16 |
| US-2 | Medium, Low (R-05 – R-07) | CA-2 zoom · CA-3 pan · CA-4 FIT · CA-5 pages | TC-11 – TC-14 · UT-03 (planned) |
| US-2 | Low (R-08) | CA-6 original file unchanged | TC-17 (smoke) |
| US-3 | High (R-09), Medium (R-10) | CA-1 – CA-8 communication, association, failures | TC-20 – TC-24 · IT-07 – IT-10 · test_motor_real.py (retries, fallback models, timeouts) |
| US-4 | High (R-11, R-12) | CA-1 – CA-8 rules, findings, categories, citations, structured output | UT-04 – UT-08 (AI-7) · test_reglas.py · TC-20, TC-25 · review of the 19 rules against the regulations |
| US-5 | High (R-13) | CA-1 – CA-8 dataset, comparison, iteration, criteria | AV-01 (manual evaluation of 8 labels, Nov 17) · AV-02 (re-test, Sprint 3) |
| US-6 | Medium (R-14) | CA-1 – CA-6 pending, in progress, completed, error | TC-20, TC-21, TC-24, TC-26 · IT-07 – IT-10 |
| Cross | High (R-15) | Sprint 1 features still work after the Zustand migration | TC-01 – TC-17 re-run on Nov 21, 2026 (TC-10 not run) |
| Cross | High (R-16) | Deployed frontend and backend work together in real AI mode | TC-20 · IT-01 – IT-10 on the deployed API |

## Sprint 1 functional test cases

Executed on Nov 21, 2026 on the deployed app (Vercel + Render, real AI mode) in Chrome 157 on Windows.

| ID | Story / CA | Technique | Input or condition | Expected result | Actual | Status |
|---|---|---|---|---|---|---|
| TC-01 | US-1 CA-1 | EP (valid) | Upload a valid PNG, JPG, JPEG and PDF | File card shown; label rendered in the viewer | PNG, JPG, JPEG and PDF loaded and rendered | Pass |
| TC-02 | US-1 CA-2 | EP (invalid) | Upload .gif / .txt / .webp | Toast "Formato no permitido…"; nothing loaded | Toast shown; nothing loaded (GIF, TXT, WEBP) | Pass |
| TC-03 | US-1 CA-2 | BVA | PDF of exactly 15,728,640 bytes | Accepted and rendered | Accepted and rendered | Pass |
| TC-04 | US-1 CA-2 | BVA | File of 15,728,641 bytes | Toast "El archivo no puede superar los 15 MB."; rejected | Toast shown; rejected | Pass |
| TC-05 | US-1 CA-2 | EP (invalid) | Text file renamed to .pdf | One toast; file removed; Analyze disabled; page does not go blank | One toast; removed; page OK | Pass |
| TC-06 | US-1 CA-2 | EP (invalid) | Text file renamed to .png | One toast; file removed; Analyze disabled | One toast; removed | Pass |
| TC-07 | US-1 CA-2 | EP (invalid) | PNG renamed to .jpg, then Analyze | Toast shows only "El contenido no corresponde al formato indicado." | Only that message | Pass |
| TC-08 | US-1 CA-4–6 | Decision table | 8 combinations of file × market × consent | Analyze enabled only when all three are present | Enabled only with all three (8/8 OK) | Pass |
| TC-09 | US-1 CA-3/4 | EP (invalid) | With all fields filled, "Change file" with an invalid file | Previous file, market and consent are kept | All three kept | Pass |
| TC-10 | US-1 CA-6 | Error guessing | Backend stopped, press Analyze | Toast "No se pudo conectar con el backend…" | Not run: the deployed backend cannot be stopped | Not run |
| TC-11 | US-2 CA-2/3 | Use case | Zoom with +, − and mouse wheel; drag | Zoomed label fills the whole viewer and can be panned | +, −, wheel and drag work; label fills the viewer | Pass |
| TC-12 | US-2 CA-2 | BVA | Type 24, 25, 400, 401 and letters in the zoom field; Escape | 24→25 %, 401→400 %, letters ignored, Escape restores | 24→25, 401→400, letters ignored, Escape restores | Pass |
| TC-13 | US-2 CA-4 | Use case | Press FIT after zooming | 100 % and centered | 100 % and centered | Pass |
| TC-14 | US-2 CA-5 | BVA | Multi-page PDF: first and last page | Previous disabled on page 1, Next disabled on the last page | As expected on a 3-page PDF | Pass |
| TC-15 | US-2 (DEV2-T5) | Use case | Toggle Overlays; zoom and pan; change page | Test boxes show/hide, stay attached to the label, appear only on page 1 | Real finding boxes (Sprint 2) show/hide and stay attached at 165 % and after pan | Pass |
| TC-16 | US-2 CA-1 | Regression | Switch PNG ↔ PDF several times with "Change file" | No false "corrupted file" toast | No false toast in 3 switches | Pass |
| TC-17 | US-2 CA-6 | Smoke | Compare file size/hash before and after zoom/pan | Identical | Same SHA-256 before and after | Pass |

## Unit and integration tests

| ID | Level | Target | Cases | Sprint | Result |
|---|---|---|---|---|---|
| UT-01 | Unit (FE) | obtenerMensajeDeError | string detail · list detail · non-JSON body | 1 | Not implemented (no frontend test runner yet) |
| UT-02 | Unit (FE) | file validation | type classes · 15 MB boundaries | 1 | Not implemented (no frontend test runner yet) |
| UT-03 | Unit (FE) | EntradaZoom | clamp 25–400 · non-numeric · Escape | 1 | Not implemented (no frontend test runner yet) |
| IT-01 – IT-06 | Integration (BE) | POST /evaluaciones | invalid market · consent false · wrong extension · wrong signature · empty file · > 15 MB → 400 with detail | 1 | Pass: run by hand on the deployed API on Nov 21, 2026 (6/6 return 400 with the expected detail); automated in test_api.py in Sprint 2 |
| UT-04 – UT-08 | Unit (BE) | services/postproceso.py (AI-7) | valid box · out-of-range box · null box · unknown rule · incomplete JSON | 2 | Pass (pytest, test_motor_real.py) |
| IT-07 – IT-10 | Integration (BE) | state endpoints | 201 pending · 202 in_progress · 404 unknown id · 409 analyze twice | 2 | Pass (pytest, test_api.py) and on the deployed API (201, 202, 404, 409) |
| Suite | Unit + integration (BE) | backend/tests (4 files) | test_api 11 · test_motor_real 27 · test_schemas 9 · test_reglas 6 | 2 | 53 passed, 0 failed without a local .env (52 passed, 1 failed with it: DEF-09) · coverage 95 % (Figure 11) |

## Sprint 2 functional and AI validation cases

| ID | Story | Input or condition | Expected result | Status |
|---|---|---|---|---|
| TC-20 | US-3/US-6 | Valid label, real AI mode (deployment) | pending → in_progress → completed; findings, metrics and boxes shown | Pass, run on the deployment: Nov 21, 2026, 16 s, 14 findings with boxes; re-run on Nov 22, 2026, 17 findings with boxes (Figure 12) |
| TC-21 | US-3/US-6 | AI_MOCK_FAIL=true, then "Retry analysis" | Error banner with message; retry works without uploading again | Not run by hand (production runs in real mode); covered by the integration test test_error_y_reintento_sin_volver_a_subir_el_archivo (pass) |
| TC-22 | US-6 | GET an unknown evaluation id | 404 with a clear message | Pass (404) |
| TC-23 | US-6 | Analyze an evaluation twice | 409 | Pass (409 while running and after completion) |
| TC-24 | US-3/US-6 | Change file during analysis | No state, banner or box from the previous evaluation | Pass (the UI asks to confirm the cancellation; the new file shows no previous results) |
| TC-25 | US-1/US-4 | Unsupported market sent to the backend | Rejected; UI shows the market as "Coming soon" | Pass (400; option disabled in the UI) |
| TC-26 | US-6 | Backend stopped during polling | Error state with a readable message | Not run: the deployed backend cannot be stopped |
| AV-01 | US-5 | Real AI run over the 8-label dataset (QA-4), compared by hand with the expected results (QA-2) | ≥ 7 of 8 labels with matching findings · 100 % valid JSON | Pass (Nov 17): 7 matched, 1 partial, 8/8 valid JSON; 4 rule adjustments (DEF-06) |
| AV-02 | US-5 | Re-test after the rule adjustments (QA-6) | ≥ 7 of 8 labels with matching findings · 100 % valid JSON | Deferred to Sprint 3 (second dataset evaluation) |

## Defects and retests

| ID | Found | Description | Fix | Retest |
|---|---|---|---|---|
| DEF-01 | Nov 8, 2026 (TC-05) | Uploading a corrupted PDF left the whole page blank: react-pdf throws InvalidPDFException during render | Error boundary LimiteDeErrorVisor around the PDF; toast + ejecutarBorrado() | Pass, re-run on Nov 21, 2026 (Figure 13) |
| DEF-02 | Nov 8, 2026 (TC-16) | Switching PNG → PDF sometimes showed a false "corrupted PDF" toast (stale preview URL for one render) | URL created together with the file in the selection handler | Pass, re-run on Nov 21, 2026 |
| DEF-03 | Nov 8, 2026 (TC-11) | Zoomed label was clipped to its original bounds instead of using the whole viewer | Wrapper and content forced to 100 % of the viewer (library styles overrode ours) | Pass, re-run on Nov 21, 2026 |
| DEF-04 | Nov 8, 2026 | Backend errors displayed as raw Error 400: {"detail": …} | Parse JSON and show only detail in a toast | Pass, re-run on Nov 21, 2026 |
| DEF-05 | Nov 16, 2026 (FE-10 review) | Small finding boxes were hidden under larger ones in the viewer | Boxes layered by area, smaller boxes on top (b027662) | Pass (TC-15, Figure 14) |
| DEF-06 | Nov 17, 2026 (AV-01) | Dataset evaluation showed miscalibrated rules: ING-01 skipped when the ingredient list was not visible, NUT-02 false positive on correct rounding, FEC-01 wrong severity | Conditions and severities adjusted in reglas/ecuador.json (01afe22) | Pass, affected labels re-analyzed on Nov 17, 2026 |
| DEF-07 | Nov 18, 2026 | test_motor_real.py set environment variables at import time, which leaked into the other test files | Autouse fixture that sets and restores the variables (d2157b7, PR #9) | Pass, 53/53 tests |
| DEF-08 | Nov 20, 2026 (TC-20) | The deployed app returned mock results: AI_MODE=real was missing on Render | AI_MODE and the API key set in the Render environment | Pass, TC-20 in real mode (Figure 12) |
| DEF-09 | Nov 22, 2026 (Figure 11 run) | test_503_persistente_da_ai_unavailable_tras_agotar_reintentos fails when the local .env sets AI_FALLBACK_MODEL (9 calls instead of 3); the application behaves correctly | Planned for Sprint 3: set AI_FALLBACK_MODEL inside the test | Open (Minor): 53/53 pass without a local .env, as in a clean CI environment |

## Execution summary

| Sprint | Level | Planned | Executed | Passed | Failed | Defects (open / closed) |
|---|---|---|---|---|---|---|
| 1 | Functional | 17 | 16 | 16 | 0 | 0 / 4 |
| 1 | Unit + integration | 9 | 6 (IT-01 – IT-06, by hand) | 6 | 0 | 0 / 0 |
| 2 | Functional + AI validation | 9 | 6 | 6 | 0 | 0 / 3 |
| 2 | Unit + integration (pytest) | 53 | 53 | 53 | 0 | 1 / 1 |

Backend statement coverage on the sprint-2 tag: 95 % (pytest-cov, application code only). The frontend has no automated tests yet.

## Static analysis (ESLint)

| Sprint | Run | Date · branch · SHA | Issues | Notes |
|---|---|---|---|---|
| 1 | Baseline (before correction) | Nov 8, 2026 · feature/dev1-Joseph-visor · ab3e674 | 2 errors (✖ 2 problems, 0 warnings) | react-hooks/set-state-in-effect (App.tsx, preview-URL effect) · no-constant-binary-expression (App.tsx, {false && …} metrics placeholder) |
| 1 | After correction | Nov 8, 2026 · feature/dev1-Joseph-visor · 138f48a | 1 error (✖ 1 problem, 0 warnings) | set-state-in-effect fixed; the placeholder remains (owned by the metrics task) |
| 2 | Baseline | Nov 14, 2026 · tag sprint-1 (main) · ad8cbe8 | 1 error (✖ 1 problem, 0 warnings) | no-constant-binary-expression carried over from Sprint 1 (App.tsx, metrics placeholder) |
| 2 | After correction | Nov 20, 2026 · tag sprint-2 (main) · 742773f | 0 problems | Placeholder replaced by estado === 'completed' in e4744a8 (PR #6, Nov 15); tsc -b passes |

## Evidence

| Evidence | Description |
|---|---|
| [class-risk-matrix.png](evidence/class-risk-matrix.png) | Risk matrix built in class (Group 6), reused in Table 7 |
| [fig07-eslint-sprint1-before-ab3e674.png](evidence/fig07-eslint-sprint1-before-ab3e674.png) | ESLint, Sprint 1 before correction: 2 errors (ab3e674) |
| [fig08-eslint-sprint1-after-138f48a.png](evidence/fig08-eslint-sprint1-after-138f48a.png) | ESLint, Sprint 1 after correction: 1 error (138f48a) |
| [fig09-eslint-sprint2-baseline-ad8cbe8.png](evidence/fig09-eslint-sprint2-baseline-ad8cbe8.png) | ESLint, Sprint 2 baseline: 1 error (tag sprint-1, ad8cbe8) |
| [fig10-eslint-sprint2-after-742773f.png](evidence/fig10-eslint-sprint2-after-742773f.png) | ESLint, Sprint 2 after correction: 0 problems (tag sprint-2, 742773f) |
| [fig11-pytest-coverage-742773f.png](evidence/fig11-pytest-coverage-742773f.png) | pytest with coverage on the sprint-2 tag: 53 passed, 95 % |
| [fig12-tc20-real-ai-analysis.png](evidence/fig12-tc20-real-ai-analysis.png) | TC-20 and DEF-08 retest: real AI analysis on the deployed app (Nov 22, 2026) |
| [fig13-tc05-corrupted-pdf.png](evidence/fig13-tc05-corrupted-pdf.png) | TC-05 and DEF-01 retest: corrupted PDF rejected, page not blank |
| [fig14-tc15-boxes-zoom-pan.png](evidence/fig14-tc15-boxes-zoom-pan.png) | TC-15 and DEF-05 retest: boxes aligned after zoom and pan |
| [fig15-ci-run-cb046c1.png](evidence/fig15-ci-run-cb046c1.png) | CI run #2 on main (cb046c1): frontend and backend passed |
| [fig16-ci-pytest-log.png](evidence/fig16-ci-pytest-log.png) | CI backend job log: 53 passed, 95 % coverage |
