# Reglas regulatorias – formato y verificación

Las reglas viven en `backend/reglas/ecuador.json` (10 reglas en el Sprint 2). Estados Unidos queda como "Próximamente":
el archivo se creará cuando entre al alcance y se activará en `MERCADOS_ACTIVOS` (`backend/models/reglas.py`).
El archivo es una lista de objetos. Se valida con:

```
cd backend
python scripts/validar_reglas.py
python tests/test_reglas.py
```

## Campos de una regla

| Campo | Qué es |
| --- | --- |
| `id` | Único, formato `PAIS-NORMA-TEMA-NN` (`US-FDA-NET-01`, `EC-RTE022-SEM-01`). Es el `regla_id` que devuelve la IA. No se reutiliza ni se renumera. |
| `norma` y `referencia` | El backend los une en `referencia_normativa` del hallazgo (la IA no escribe citas). |
| `titulo` | Nombre corto de la regla. |
| `requisito` | Qué exige la norma, en lenguaje claro y fiel al texto. |
| `como_verificar` | Qué debe mirar la IA en la imagen. Entra al prompt. |
| `cumple_si` / `incumple_si` | Condiciones concretas que se pueden decidir mirando una foto. Entran al prompt. |
| `severidad_si_incumple` | `critico` o `advertencia`. La define el equipo, no la IA. |
| `aplica_si` | Cuándo la regla corresponde y cuándo no evaluarla. |
| `cita_fuente` | Frase breve del texto oficial en que se apoya. Sirve para verificar. |
| `fuente_url` | Enlace al texto oficial. |
| `estado` | `pendiente_revision` o `verificada`. |
| `verificada_por` | Nombre de quien comparó la regla con la fuente. Obligatorio si el estado es `verificada`. |

## Cómo se verifica una regla

1. Abre el `fuente_url` y busca el numeral de `referencia`.
2. Comprueba que `cita_fuente` aparece en el texto y que `requisito` no dice más ni menos que la norma.
3. Comprueba que `cumple_si` e `incumple_si` se pueden decidir mirando una foto de la etiqueta.
4. Comprueba que `severidad_si_incumple` y `aplica_si` son razonables.
5. Si todo coincide, cambia `estado` a `"verificada"` y escribe tu nombre en `verificada_por`. Si no, corrige el texto.
6. Ejecuta `python scripts/validar_reglas.py`.

El motor solo usa reglas `verificada`. En desarrollo se pueden incluir todas con `REGLAS_INCLUIR_PENDIENTES=true` en `backend/.env`.

## Fuentes y límites

- **Ecuador:** NTE INEN 1334-1:2011 (rotulado general, que remite el RTE INEN 022) y el Reglamento Sanitario de Etiquetado de Alimentos Procesados (Acuerdo 4522, texto de junio de 2014 en la web de ARCSA).
- El texto oficial del RTE INEN 022 (2R) no pudo leerse directamente (el sitio del INEN bloquea la lectura automática y la modificatoria publicada en ARCSA solo trae los numerales 9.1 y 9.2). Hay que confirmar contra la versión vigente que los numerales de la NTE INEN 1334-1 siguen aplicando.
- Pendientes para una siguiente ronda: tabla nutricional (NTE INEN 1334-2), registro sanitario, advertencia "CONTIENE TRANSGÉNICOS" (Art. 22 del Acuerdo 4522).
- Esto es una guía técnica para el MVP y no constituye asesoría legal.

## Lista de reglas (para revisar)

### Ecuador (ARCSA / INEN)

| ID | Regla | Referencia | Severidad | Estado |
| --- | --- | --- | --- | --- |
| `EC-RTE022-NOM-01` | Nombre del alimento | NTE INEN 1334-1:2011 (rotulado general, referida por el RTE INEN 022), 5.1.1 | critico | pendiente_revision |
| `EC-RTE022-ING-01` | Lista de ingredientes con título 'Ingredientes' | NTE INEN 1334-1:2011, 5.1.2.1 a) y b) | advertencia | pendiente_revision |
| `EC-RTE022-ALE-01` | Declaración 'CONTIENE' de alérgenos | NTE INEN 1334-1:2011, 5.1.2.2 b) y Anexo C.1 | critico | pendiente_revision |
| `EC-RTE022-NET-01` | Contenido neto en el panel principal en unidades SI | NTE INEN 1334-1:2011, 5.1.3.1 | critico | pendiente_revision |
| `EC-RTE022-FAB-01` | Fabricante, envasador o importador | NTE INEN 1334-1:2011, 5.1.4.1 y 5.1.4.2 | critico | pendiente_revision |
| `EC-RTE022-ORI-01` | País de origen | NTE INEN 1334-1:2011, 5.1.5.1 | critico | pendiente_revision |
| `EC-RTE022-LOT-01` | Identificación del lote | NTE INEN 1334-1:2011, 5.1.6.1 | advertencia | pendiente_revision |
| `EC-RTE022-FEC-01` | Fecha de vencimiento y condiciones de conservación | NTE INEN 1334-1:2011, 5.1.7.1 y 5.1.7.2 | advertencia | pendiente_revision |
| `EC-RTE022-SEM-01` | Semáforo nutricional visible en el panel principal | Reglamento Sanitario de Etiquetado de Alimentos Procesados (Acuerdo Ministerial 4522), Art. 12 y Anexo 1 | critico | pendiente_revision |
| `EC-RTE022-IDI-01` | Información obligatoria en español y legible | NTE INEN 1334-1:2011, 5.4.1 y 5.5.3 | critico | pendiente_revision |
