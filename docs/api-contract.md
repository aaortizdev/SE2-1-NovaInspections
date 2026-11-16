# Contrato de la API – Sprint 2

Fuente de verdad entre backend y frontend. Todo cambio se hace por pull request y lo aprueba el equipo.
Los esquemas Pydantic están en `backend/models/schemas.py` y los JSON de ejemplo en `docs/ejemplos/`
(`backend/tests/test_schemas.py` comprueba que ambos coinciden).

## Flujo (polling)

```
POST /evaluaciones              -> 201  status "pending"
POST /evaluaciones/{id}/analizar -> 202  status "in_progress"   (el análisis corre en segundo plano)
GET  /evaluaciones/{id}          -> 200  repetir cada 2 s (4 s pasados 30 s) hasta "completed" o "error"
```

Estados: `pending` → `in_progress` → `completed` | `error`. Solo desde `error` se puede volver a llamar a
`/analizar` (reintento). `idle` existe únicamente en el frontend (antes de pulsar "Analizar etiqueta").

## Endpoints

| Endpoint | Cuándo | Respuestas |
| --- | --- | --- |
| `POST /evaluaciones` (multipart: `archivo`, `normativa`, `acepto_terminos`) | Al pulsar "Analizar etiqueta" | 201 `EvaluationCreateResponse`; 400 `{"detail": "..."}` con las mismas validaciones del Sprint 1 |
| `POST /evaluaciones/{id}/analizar` | Justo después de crear, y al reintentar | 202 `EvaluationStartResponse`; 404 no existe; 409 ya está en curso o completada |
| `GET /evaluaciones/{id}` | Cada 2 s mientras el estado sea `in_progress` | 200 `EvaluationResultResponse`; 404 no existe |
| `GET /health` | Al arrancar y para diagnóstico | 200 con el modo (`mock` o `real`) y si hay API key configurada |

Mercado aceptado en el Sprint 2: solo `ecuador`. Estados Unidos queda como "Próximamente" y, como cualquier otro valor, responde 400
("Selecciona una opción válida de normativa.").

## Hallazgo (`Finding`)

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | string | `F-001`, `F-002`… asignado por el backend |
| `regla_id` | string | ID de la regla de la base regulatoria (p. ej. `EC-RTE022-SEM-01`) |
| `pagina` | int ≥ 1 | 1 para imágenes |
| `severidad` | `critico` \| `advertencia` \| `ok` | valor estricto |
| `etiqueta` | string | `Crítico`, `Advertencia` u `OK`; lo completa el backend |
| `x`, `y`, `ancho`, `alto` | número 0–100 o `null` | porcentaje de la etiqueta; los cuatro o ninguno |
| `titulo`, `elemento_evaluado`, `descripcion_hallazgo`, `recomendacion` | string | texto para el dictamen |
| `referencia_normativa` | string | lo completa el backend desde la regla |
| `confianza` | número 0–1 | |

**Conversión a `CajaOverlay`** (frontend): `{ id, pagina, x, y, ancho, alto, severidad, etiqueta }`.
Si `x` es `null`, el hallazgo se lista en el dictamen pero no se dibuja caja.

## Resumen (`Summary`)

`{ total, criticos, advertencias, conformes }`. Lo calcula el backend a partir de los hallazgos.

## Error del análisis

`{ codigo, mensaje, reintentable }` con `codigo` en: `AI_TIMEOUT`, `AI_RATE_LIMIT`, `AI_UNAVAILABLE`,
`AI_INVALID_RESPONSE`, `FILE_UNREADABLE`, `INTERNAL`. Los errores HTTP de validación siguen el formato
del Sprint 1 (`{"detail": "..."}`) para que `obtenerMensajeDeError` siga funcionando.

## Salida que se le exige a la IA (`AIOutput`)

La IA solo devuelve `hallazgos`, cada uno con `regla_id`, `pagina`, `severidad`, `caja_2d`, `titulo`,
`elemento_evaluado`, `descripcion_hallazgo`, `recomendacion` y `confianza`.

`caja_2d` = `[ymin, xmin, ymax, xmax]` en escala **0–1000** (formato `box_2d` de Gemini), o `null` si no
hay un elemento visible que señalar. El backend la convierte a porcentaje:

```
x = xmin / 10          y = ymin / 10
ancho = (xmax - xmin) / 10     alto = (ymax - ymin) / 10
```

Ejemplo: `[630, 124, 772, 409]` → `x=12.4, y=63.0, ancho=28.5, alto=14.2`.

## Cómo se muestra un hallazgo en el visor

Cada hallazgo con caja se dibuja sobre la etiqueta con tres elementos:

| Elemento | Qué muestra | De dónde sale |
| --- | --- | --- |
| Borde del cuadro | Rojo = Crítico, naranja = Advertencia, verde = OK (mismos tonos de las tarjetas de métricas: `#df2535`, `#e58400`, `#16a34a`) | `severidad` |
| Círculo con número | Número del hallazgo (1, 2, 3…), el mismo de su tarjeta en el dictamen | Posición en la lista (`F-001` → 1) |
| Texto al pasar el mouse | `Crítico · {titulo}` (por ejemplo, "Crítico · Falta el semáforo nutricional") | `etiqueta` y `titulo` |

Al hacer clic en un cuadro se resalta su tarjeta del dictamen, y al revés. Un hallazgo sin caja
(`x` = `null`) aparece solo como tarjeta. No hay campo de categoría: el `titulo` describe el tipo.

## Modo mock

Con `AI_MODE=mock` el backend devuelve 3 hallazgos de ejemplo (1 crítico, 1 advertencia, 1 OK) tras
`AI_MOCK_DELAY_S` segundos. Con `AI_MOCK_FAIL=true` el análisis termina en `error` (`AI_TIMEOUT`,
reintentable). Los textos llevan el prefijo `[MOCK]` y los ID de regla son de ejemplo.

## Ejemplos

- `docs/ejemplos/creada.json` – respuesta de `POST /evaluaciones`
- `docs/ejemplos/iniciada.json` – respuesta de `POST /evaluaciones/{id}/analizar`
- `docs/ejemplos/completada.json` – `GET /evaluaciones/{id}` terminado
- `docs/ejemplos/error.json` – `GET /evaluaciones/{id}` con error
- `docs/ejemplos/ai_output.json` – salida cruda de la IA
