# Sprint 2

**Sprint goal:** integrate and configure the AI analysis, validate its results and show the analysis status.

**Stories:** US-3 Integrate the AI engine, US-4 Configure the AI regulatory analysis, US-5 Validate and improve the AI analysis and US-6 Display the analysis status, 20 story points in Jira.

The plan (Nov 15, 2026) distributes 39 tasks in 6 blocks, with code freeze on Nov 18 and a re-planned delivery on Nov 22, 2026. Kickoff decisions: [../decisiones-sprint-2.md](../decisiones-sprint-2.md).

## Result

- US-3, US-4 and US-6 implemented and merged into main (PRs #4–#8, Nov 15–16, 2026).
- US-5 completed through a manual evaluation: 8 labels analyzed with the real AI and compared by hand with the expected results (7 matched, 1 partially); 4 rule adjustments merged on Nov 17.
- Deployment on Vercel (frontend) and Render (backend) in PRs #9–#10 (Nov 18–20).
- CI pipeline with GitHub Actions in PR #11 (Nov 22).
- Ahead of plan (Sprint 3): US-8 bounding boxes completed; US-7, US-9 and US-10 partially done.
- Deferred: US, MX, CO, UK and EU markets ("Coming soon"), database persistence, FE-8 PDF sharpness, label rotation and the second dataset evaluation (Sprint 3).
- Rejected: US rules (AI-4), dropped on Nov 15.
- Tag: [sprint-2](https://github.com/aaortizdev/SE2-1-NovaInspections/releases/tag/sprint-2) (742773f, PR #10, Nov 20, 2026).
- Acceptance form: pending client signature.

## Backlog by block

| Block | Tasks | Story | Owner | Status |
|---|---|---|---|---|
| 0 · Contract | S2-00 kickoff decisions and API key · S2-01 API contract docs/api-contract.md · S2-02 branches, .env.example, README | All | Ariel | Done |
| A · Backend | BE-1 Pydantic schemas · BE-2 in-memory store · BE-3 POST /evaluaciones (201 pending) · BE-4 POST …/analizar (202, 404, 409, retry) · BE-5 GET status · BE-6 mock mode · BE-7 timeouts and error mapping · BE-8 CORS and /health (D) | US-3, US-6 | Ariel | Done |
| B · Frontend | FE-1 Zustand store · FE-2 migrate App.tsx · FE-3 api.ts · FE-4 analysis orchestrator with polling · FE-5 status banner · FE-6 market selector (only Ecuador active) · FE-7 metrics panel · FE-8 PDF sharpness (D) · FE-9 abort and cleanup · FE-10 cross highlighting (D) | Pre, US-3, US-4, US-6 | Ariel | Done (FE-8 deferred) |
| C · AI engine | AI-1 AI client · AI-2 file preparation (PyMuPDF) · AI-3 engine with structured output · AI-4 US rules (21 CFR 101; dropped on Nov 15, US moved to "Coming soon") · AI-5 Ecuador rules (RTE INEN 022) · AI-6 system prompt · AI-7 post-processing · AI-8 integration | US-3, US-4 | Ariel (engine); Genesis, Joseph (regulations and rules) | Done (AI-4 dropped) |
| D · Validation | QA-1 dataset (≥ 6 labels) · QA-2 expected results · QA-3 tests/run_eval.py · QA-4 first real run · QA-5 prompt iteration · QA-6 re-test and comparison | US-5 | Ariel | Done (manual evaluation) |
| E · Closing | CL-1 end-to-end manual tests · CL-2 README · CL-3 Sprint 2 documents · CL-4 freeze, tag sprint-2, demo rehearsal | All | Ariel, Walter (deployment) | Partial (README, deployment and sprint-2 tag done) |
