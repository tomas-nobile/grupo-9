# Registro de uso de IA

Lo pide la consigna: al menos tres prompts relevantes con su respuesta, qué se aceptó, modificó o rechazó, y cómo se comprobó que el código funcionaba. Herramienta: **Claude Code** (modelos Claude Fable 5.1 para el setup y Claude Opus 5.5 para la implementación) con el modo de trabajo descripto en `CLAUDE.md`: la IA implementa story por story a partir de `specs/`, y cada decisión relevante queda acá o en `docs/decisions.md`.

Las entradas marcadas `[REVISAR]` son borradores que deja `/feature` al cerrar una story: hay que completar "Decisión" con palabras propias y borrar la marca. Al entregar (F07.2) quedan las 3–5 más relevantes, idealmente una aceptada, una modificada y una rechazada.

## Formato

```
### N · <story o tema> · <fecha>
**Prompt:** el pedido, textual o resumido en una línea.
**Propuesta de la IA:** qué propuso o implementó, en 3–5 líneas. Si fue código: qué clases/funciones y qué enfoque. Qué alternativa descartó.
**Decisión:** aceptada / modificada (qué cambié y por qué) / rechazada (por qué).
**Verificación:** cómo comprobé que funciona: test, caso probado a mano con entrada y resultado esperado vs. obtenido.
```

---

### 0 · Setup del proyecto · 2026-09-25
**Prompt:** "Tengo que hacer un proyecto de control de inventario y alertas de reabastecimiento siguiendo la consigna. Armá `.claude` y `CLAUDE.md` tomando como referencia el repo everyone-makes-subs. Haceme preguntas y confirmemos antes de terminar. Armá el git también."
**Propuesta de la IA:** leyó la consigna y el repo de referencia, hizo dos rondas de preguntas (interfaz, fuente externa, dominio, idioma, workflow, registro de prompts, GitHub, tests) y propuso: menú CLI, dos módulos (`main.py` + `funciones.py`), sin clases porque POO no está en el cronograma, hook para registrar prompts automáticamente, specs F01–F07, git + repo público.
**Decisión:** modificada. Acepté el menú CLI, el dominio almacén, el español, el workflow con specs y comandos, y pytest. Rechacé la fuente externa (API del dólar), el hook automático de prompts y las GitHub Actions: para un proyecto chico no hacen falta. Cambié dos cosas sobre la propuesta: **usar POO aunque no esté en el programa** y separar en más módulos, porque hay que explicar cómo funciona y así cada concepto tiene un lugar; y pedí una guía en `docs/guia.md` que explique el sistema.
**Verificación:** revisé la estructura propuesta antes de que se creara y el commit inicial en `git log`. La verificación real de cada decisión viene con las stories.

### 1 · Agregar una fuente externa · 2026-09-25
**Prompt:** "Agregá una fuente externa o API, agregalo como feature."
**Propuesta de la IA:** probó que DolarApi respondiera sin clave y escribió el spec F08. Propone un módulo nuevo `fuente_externa.py`, que es el único que usa la red. Pide `GET /v1/dolares/oficial` con `requests`, con un timeout de 5 segundos. Si falla, usa una caché en `datos/cotizacion.json`, y se commitea una caché inicial para que la demo ande sin wifi. Con el valor de venta se muestran el inventario y la reposición en dólares. Descartó Fake Store API (productos genéricos, no de almacén) y un CSV de proveedor (no es una API).
**Decisión:** [REVISAR] completar: ¿aceptada tal cual o modificada? Por qué el dólar y no otra fuente.
**Verificación:** 7 tests en `tests/test_fuente_externa.py` simulan la API con `monkeypatch`: respuesta válida, venta 0, venta texto, sin internet con caché y sin internet sin caché. A mano, `obtener_cotizacion()` devolvió `origen: api` con la API real y `origen: cache` con una URL inválida.

### 2 · Implementar las features: cambio en el diseño del menú · 2026-09-25
**Prompt:** "Implementá las features." La IA implementó las 23 stories, con un commit por story.
**Propuesta de la IA:** el spec pedía un menú `while True` con un `if/elif` por opción y un `try/except` en cada opción. La IA lo cambió durante F02.1. Ahora hay una lista `OPCIONES` de tuplas `(tecla, texto, función)`, una función `ejecutar_opcion` que busca la tecla y llama a la función, y **un solo** `try/except ErrorInventario` en el loop de `main()`. El argumento: con 15 opciones, el `if/elif` era largo, y el manejo de errores se repetía 15 veces.
**Decisión:** [REVISAR] completar. El cambio respecto del spec está anotado en `docs/decisions.md`. Guardar funciones en una lista no se vio en clase, así que conviene poder explicarlo; está en la guía, sección 4.5.
**Verificación:** el smoke (`python main.py < tests/smoke_input.txt`) recorre todas las opciones de consulta. A mano, la opción `99` muestra "Opción inválida" y vuelve al menú. Un código inexistente en la opción 5 muestra el error y vuelve al menú, sin cortar el programa.

### 3 · Error detectado al probar: tildes rotas en Windows · 2026-09-25
**Prompt:** durante F01.1, al correr `python main.py` con la entrada redirigida desde un archivo.
**Propuesta de la IA:** la salida mostraba `Opci�n` en vez de `Opción`. Con la salida redirigida, que es lo que pasa también en Git Bash, Python en Windows usa la codificación cp1252 y la terminal espera UTF-8. La IA agregó `sys.stdout.reconfigure(encoding="utf-8")` al principio de `main()`. Además cambió el símbolo ⚠ del spec por el texto `ALERTA:`, que se ve igual en cualquier terminal.
**Decisión:** [REVISAR] completar.
**Verificación:** se volvió a correr el mismo comando y las tildes salieron bien. Este problema no lo detectan los tests, porque no imprimen: solo aparece corriendo la app.

### 4 · Error de la IA: salto de línea que rompió `main.py` · 2026-09-25
**Prompt:** durante F05.4, la IA agregó la pantalla de indicadores con un script que editaba `main.py`.
**Propuesta de la IA:** quiso escribir `print(f"\n1) VALOR...")`, pero el script convirtió el `\n` en un salto de línea real dentro del f-string, y `main.py` quedó con un `SyntaxError`. **Los 65 tests siguieron pasando**, porque ningún test importa `main.py`. El error apareció al correr la app. La IA lo corrigió reemplazando cada `\n` por un `print()` vacío antes del título, que además se lee mejor.
**Decisión:** [REVISAR] completar: la corrección se aceptó. La lección es que los tests no cubren el menú, y por eso existe el smoke, que hay que correr siempre.
**Verificación:** con `python main.py` y la opción 12 se ven las tablas. El smoke termina sin errores.
