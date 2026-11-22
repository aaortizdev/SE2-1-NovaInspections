# SCRUM artifacts

| Artifact | Location |
|---|---|
| Product backlog and board | [Jira board](https://sofware2fiecg6.atlassian.net/jira/software/projects/US/boards/3/backlog) |
| Sprint reports (burndown) | [Jira reports](https://sofware2fiecg6.atlassian.net/jira/software/projects/US/boards/3/reports/burndown?source=overview) |
| Sprint 1 plan and result | [sprint-1.md](sprint-1.md) |
| Sprint 2 plan and result | [sprint-2.md](sprint-2.md) |
| Sprint 2 kickoff decisions (Nov 15, 2026) | [../decisiones-sprint-2.md](../decisiones-sprint-2.md) |
| Release tags | [sprint-1](https://github.com/aaortizdev/SE2-1-NovaInspections/releases/tag/sprint-1) (ad8cbe8) · [sprint-2](https://github.com/aaortizdev/SE2-1-NovaInspections/releases/tag/sprint-2) (742773f) |
| Client communications | [../../Communications/README.md](../../Communications/README.md) |

## Roadmap

| Sprint | Dates (scope) | User stories | Increment |
|---|---|---|---|
| 1 | Oct 1 – Oct 21, 2026 | US-1, US-2 | Prepare the evaluation; view and navigate the label |
| 2 | Oct 22 – Nov 13, 2026 | US-3, US-4, US-5, US-6 | Integrate and configure the AI engine, validate it, show analysis status |
| 3 | Nov 23 – Dec 13, 2026 | US-7, US-8, US-9, US-10 | Findings, bounding boxes, verdict, finding details |
| 4 | Dec 14, 2026 – Jan 8, 2027 | US-11, US-12, US-13 | PDF report, history, retrieve evaluation |

## Scrum roles

| Role | Member | Sprint 1 | Sprint 2 |
|---|---|---|---|
| Product Owner | Lenín Javier Maingón | Backlog prioritization and acceptance. | Regulatory domain knowledge and acceptance. |
| Scrum Master / Developer | Ariel Ortiz | Sprint 1 planning. Repository and ceremonies, navigation shell, upload panel (with Walter), PR acceptance checklist | Sprint 2 planning; AI engine integration and configuration (US-3, US-4); analysis status (US-6); dataset validation (US-5); final verification of the 19 rules; frontend deployment on Vercel |
| Developer 3 | Walter Mirabá | Repository setup, navigation shell, upload panel and evaluation form (US-1) | Backend deployment on Render |
| Developer 1 | Genesis Michilena | Viewer engine: interactive canvas, toolbar, multi-page navigation (US-2) | Collection of the general labeling regulations (RTE INEN 022 2R, AM 5103, NTE INEN 1334-1) and drafting of their rules in the rules JSON |
| Developer 2 | Joseph Miranda | Viewer controls, overlay layer base, upload limits and frontend error handling (US-1/US-2) | Collection of the complementary regulations (NTE INEN 1334-2 and 1334-3, ARCSA-DE-2022-016, Consumer Law) and drafting of their rules in the rules JSON |
