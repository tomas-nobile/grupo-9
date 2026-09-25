# Registro de uso de IA

Lo pide la consigna: al menos tres prompts relevantes con su respuesta, qué se aceptó, modificó o rechazó, y cómo se comprobó que el código funcionaba. Herramienta: **Claude Code** (modelo Claude Fable 5.1) con el modo de trabajo descripto en `CLAUDE.md`: la IA implementa story por story a partir de `specs/`, y cada decisión relevante queda acá o en `docs/decisions.md`.

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
