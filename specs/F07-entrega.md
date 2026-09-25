# F07 · Entrega y oral

**Prioridad:** P0 · **Depende de:** todo lo anterior · **CLAUDE.md:** "Docs"

**Objetivo:** el ZIP cumple la consigna punto por punto, la guía explica el sistema completo y el oral de 5 minutos está ensayado.

## Stories

### [x] F07.1 · README final y guía completa
Como docente, quiero abrir el README y saber qué hace la app, cómo correrla y por qué se tomó cada decisión; y si quiero entender el código, que la guía me lleve de la mano.

- `README.md`, secciones en este orden: Objetivo (3 líneas + captura del menú o del gráfico), Instalación (`python -m venv .venv`, activar en Windows y Linux, `pip install -r requirements.txt`), Ejecución (`python main.py`, `pytest -q`, abrir la notebook), Estructura de archivos (tabla con los 6 módulos y su capa), Datos (formato de `productos.json` y `movimientos.csv`), Fuente externa (qué API, qué dato se usa, qué pasa sin internet), Alertas e indicadores (la regla de reposición y los tres indicadores, en palabras), Decisiones principales (5–8 bullets tomados de `docs/decisions.md`, incluida la de POO), Uso de IA (herramienta, modo de trabajo, link a `docs/registro_prompts.md`), Cómo se probó (tests + casos manuales con entrada y resultado esperado), Cómo entender el código (link a `docs/guia.md`), Limitaciones.
- `docs/guia.md`: sin `[PENDIENTE]`. Releer las secciones 3 a 7 contra el código actual y corregir lo que haya quedado viejo. Sección 5 con la tabla de errores completa. Sección 7 con los tres casos manuales del oral.
- Todo en español, sin jerga que no se pueda explicar en el oral.

**Verificar:** seguir el README en una terminal nueva desde cero y que funcione. `grep -c PENDIENTE docs/guia.md` da 0.

### [ ] F07.2 · Registro de prompts curado
Como docente, quiero ver al menos tres prompts relevantes, qué propuso la IA y qué decidió el estudiante.

- `docs/registro_prompts.md`: elegir las 3–5 entradas más relevantes de los borradores `[REVISAR]` (idealmente una aceptada, una modificada y una rechazada), completar "Decisión" y "Verificación" con palabras propias, borrar las marcas y los borradores que no aportan. La entrada 0 (setup) se queda: es el ejemplo más claro de propuesta modificada.
- Cada entrada tiene que poder defenderse en el oral: si no podés explicar por qué aceptaste algo, es señal de que hay que releer ese código con la guía.

**Verificar:** `grep -c REVISAR docs/registro_prompts.md` da 0 y hay ≥ 3 entradas.

### [ ] F07.3 · ZIP, guion y ensayo del oral
Como estudiante, quiero entregar el ZIP correcto y tener un guion de 5 minutos ensayado.

- `/entregar` verde: ZIP armado, listado, subido al campus.
- `docs/guion_oral.md`, con tiempos: 0:00 qué problema resuelve (30 s) · 0:30 demo: arrancar y ver el aviso de alertas, registrar una salida que dispara alerta, intentar una salida inválida, alertas, indicadores, gráfico, valor en USD desde la API (2:30) · 3:00 código: el diagrama de capas de la guía, recorrer `modelos.py` e `inventario.registrar_movimiento` y un test (1:00) · 4:00 uso de IA: una decisión aceptada y una rechazada (30 s) · 4:30 cierre y preguntas.
- Sección 8 de `docs/guia.md`: las preguntas probables con su respuesta en dos líneas.
- Ensayar con cronómetro al menos dos veces.

**Verificar:** el ensayo entra en 5 minutos.
