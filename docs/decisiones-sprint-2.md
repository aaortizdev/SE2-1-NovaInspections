# Decisiones del Sprint 2 (reunión de arranque, domingo 15/11/2026)

- **Flujo de estados:** polling. `POST /evaluaciones` (pending) → `POST /evaluaciones/{id}/analizar`
  (in_progress, análisis en segundo plano) → `GET /evaluaciones/{id}` cada 2 s hasta `completed` o `error`.
- **Mercados del sprint:** solo Estados Unidos (FDA) y Ecuador (ARCSA / RTE INEN 022). Los demás quedan en el
  selector como "Próximamente" y el backend los rechaza.
- **Proveedor de IA:** Gemini (SDK `google-genai`), modelo `gemini-3.8-flash`, configurable con `AI_MODEL`.
  La API key la gestiona una sola persona del equipo y vive solo en `backend/.env` (nunca en el repositorio).
- **Cajas:** la IA devuelve `box_2d` = `[ymin, xmin, ymax, xmax]` en escala 0–1000; el backend lo convierte a
  porcentaje (0–100) para el visor.
- **Resumen:** lo calcula el backend; la IA no cuenta.
- **Reglas regulatorias:** las redactan y verifican dos personas del equipo (EE. UU. y Ecuador), con ID por
  regla y fuente oficial enlazada.
- **Modo mock:** `AI_MODE=mock` permite desarrollar y hacer la demostración sin llamar a la IA.
- **Datos de prueba:** solo etiquetas públicas o propias; el nivel gratuito de Google puede usar lo enviado
  para mejorar sus productos.
- **Criterios de validación (US-5):** ≥ 85 % de coincidencia en hallazgos (mismo `regla_id` y misma
  severidad), 100 % de JSON válido y ≥ 70 % de cajas con IoU ≥ 0,3.
- **Persistencia:** evaluaciones en memoria, un solo worker; base de datos queda para el Sprint 3.
