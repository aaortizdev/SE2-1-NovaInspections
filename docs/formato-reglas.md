# Reglas regulatorias – formato y verificación

Las reglas viven en `backend/reglas/ecuador.json` (19 reglas en el Sprint 2). Estados Unidos queda como "Próximamente":
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

Revisadas el 16/11/2026 contra los textos que entregó el equipo:

- **Nivel 1 (requisitos obligatorios y semáforo):** RTE INEN 022 (2R), Resolución 14 511 de 2014; Acuerdo Ministerial 5103 (Reglamento Sanitario Sustitutivo de Etiquetado, que deroga el Acuerdo 4522); NTE INEN 1334-1:2014 (cuarta revisión), que el RTE 022 exige en su numeral 5.1.
- **Nivel 2 (tabla nutricional y declaraciones):** NTE INEN 1334-2 (tercera revisión; la copia disponible lleva fecha "2016-xx") y NTE INEN 1334-3:2011.
- **Nivel 3 (comercialización):** Resolución ARCSA-DE-2022-016-AKRG (Disposiciones Generales Décima y Décima Primera, Art. 19) y Ley Orgánica de Defensa del Consumidor (Arts. 10, 13 y 14).
- La copia de la NTE INEN 1334-1:2014 numera la sección de fechas como 5.1.7 aunque va entre 5.4.6 y 5.4.8; las reglas la citan como 5.4.7.
- La NTE INEN 1334-2 lista como obligatorios energía, grasa total, saturada, colesterol, sodio, carbohidratos, fibra y proteína; los azúcares son voluntarios salvo que haya una declaración sobre carbohidratos.
- Medidas que la IA no puede comprobar en una imagen (área del semáforo en cm², colores CMYK exactos, tipografía) solo se reportan si el incumplimiento es evidente.
- Esto es una guía técnica para el MVP y no constituye asesoría legal.

## Lista de reglas

### Ecuador (ARCSA / INEN)

| ID | Regla | Referencia | Severidad | Estado |
| --- | --- | --- | --- | --- |
| `EC-RTE022-NOM-01` | Nombre del alimento | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.1.1 y 5.4.1.2 | critico | verificada |
| `EC-RTE022-ING-01` | Lista de ingredientes con título 'Ingredientes' | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.2.1 a) y b) | critico | verificada |
| `EC-RTE022-ALE-01` | Declaración 'CONTIENE' de alérgenos | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.2.2 b) y Anexo C.1 | critico | verificada |
| `EC-RTE022-NET-01` | Contenido neto en el panel principal en unidades SI | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.3.1 y 5.8.6 | critico | verificada |
| `EC-RTE022-FAB-01` | Fabricante, envasador o importador | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.4.1 y 5.4.4.2 | critico | verificada |
| `EC-RTE022-ORI-01` | Ciudad y país de origen | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.5.1 y 5.4.5.2 | critico | verificada |
| `EC-RTE022-LOT-01` | Identificación del lote | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.6.1 | advertencia | verificada |
| `EC-RTE022-FEC-01` | Fecha de vencimiento y condiciones de conservación | NTE INEN 1334-1:2014 (4R), exigida por el RTE INEN 022 (2R) 5.1, 5.4.7.1 (impreso como 5.1.7.1) y 5.4.7.2 | critico | verificada |
| `EC-RTE022-IDI-01` | Información obligatoria en castellano y legible | NTE INEN 1334-1:2014 (4R); Ley Orgánica de Defensa del Consumidor; RTE INEN 022 (2R), 1334-1: 5.7.1 y 5.8.3; LODC Art. 10; RTE 4.3 | critico | verificada |
| `EC-RTE022-SEM-01` | Semáforo nutricional presente | RTE INEN 022 (2R); Acuerdo Ministerial 5103, RTE 5.5.4 y 5.5.5; AM 5103 Art. 12 | critico | verificada |
| `EC-RTE022-SEM-02` | Formato y ubicación del semáforo | RTE INEN 022 (2R); Acuerdo Ministerial 5103, RTE 5.5.5, 5.5.5.1, 5.5.5.2 y 5.5.14.3; AM 5103 Anexo 1 | advertencia | verificada |
| `EC-RTE022-SEM-03` | Niveles del semáforo coherentes con la tabla nutricional | RTE INEN 022 (2R); Acuerdo Ministerial 5103, RTE 5.5.1 Tabla 1 y 5.5.14.1; AM 5103 Art. 9 | advertencia | verificada |
| `EC-RTE022-MSJ-01` | Mensajes de advertencia obligatorios | RTE INEN 022 (2R); Acuerdo Ministerial 5103, RTE 5.2, 5.5.7, 5.5.9, 5.5.10, 5.5.11 y 5.5.14.3 j); AM 5103 Arts. 15, 17, 18, 20 y 22 | critico | verificada |
| `EC-RTE022-NUT-01` | Tabla nutricional con los nutrientes obligatorios | NTE INEN 1334-2 (3R), exigida por el RTE INEN 022 (2R) 5.1; Ley Orgánica de Defensa del Consumidor, 1334-2: 4.2.1, 4.2.2, 4.4.2, 4.4.12 y 4.9.2; LODC Art. 14 g) | critico | verificada |
| `EC-RTE022-NUT-02` | Coherencia de los valores nutricionales | NTE INEN 1334-2 (3R), 4.3.1, 4.4.5, 4.4.6 y Tabla 5 | advertencia | verificada |
| `EC-RTE022-CLA-01` | Declaraciones prohibidas o engañosas | NTE INEN 1334-1:2014 (4R); RTE INEN 022 (2R); Acuerdo Ministerial 5103; NTE INEN 1334-3:2011, 1334-1: 5.2; RTE 5.5.15; AM 5103 Art. 7; 1334-3: 5.1.3 y 5.1.4.2 | critico | verificada |
| `EC-RTE022-CLA-02` | Declaraciones nutricionales dentro de los umbrales | NTE INEN 1334-3:2011, 4.4, 5.1.1 y Tabla 1 | advertencia | verificada |
| `EC-RTE022-RSA-01` | Notificación Sanitaria o Código BPM | NTE INEN 1334-1:2014 (4R); Ley Orgánica de Defensa del Consumidor; Resolución ARCSA-DE-2022-016-AKRG, 1334-1: 5.4.11; LODC Art. 14 f); ARCSA Disposiciones Generales Décima y Décima Primera | critico | verificada |
| `EC-RTE022-PVP-01` | Precio de venta al público (PVP) | Ley Orgánica de Defensa del Consumidor; NTE INEN 1334-1:2014 (4R), LODC Art. 14 j); 1334-1: 5.8.2 | advertencia | verificada |
