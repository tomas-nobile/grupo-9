---
description: Arreglar un bug rápido y commitear
argument-hint: descripción del bug
---

Bug: $ARGUMENTS

1. Reproducirlo con lo mínimo: un test en `tests/test_funciones.py` o un caso concreto en `python main.py`.
2. Encontrar la causa. No parchear el síntoma si la causa está a la vista.
3. Arreglarlo. Si es lógica pura, dejar el test que lo reproduce.
4. `pytest -q` y commit: `fix: <qué>`.
5. Si el bug vino de código propuesto por la IA, agregar una entrada `[REVISAR]` en `docs/registro_prompts.md`: son las mejores entradas para "Pruebas y corrección" del oral.
6. Responder en 2 líneas: causa y arreglo.

Timebox: 20 minutos. Si no sale, anotar `TODO:` en `docs/decisions.md` con lo que se sabe y decirlo.
