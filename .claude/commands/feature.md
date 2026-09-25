---
description: Implementar una feature completa (todas sus stories) o una story
argument-hint: F03 | F03.2
---

Implementar `$ARGUMENTS` siguiendo `CLAUDE.md` y `.claude/rules/python.md`. Sin preguntas ni pausas: de punta a punta.

1. **Resolver el alcance.**
   - `F03` → todas las stories pendientes (`[ ]`) de `specs/F03-*.md`, en orden.
   - `F03.2` → solo esa story.
   - Leer ese archivo y solo las secciones de `CLAUDE.md` que cita (siempre "Stack y layout" y "Contratos"). Leer la sección de `docs/guia.md` del módulo que se toca, para no contradecirla.
2. **Por cada story:**
   1. Implementar lo mínimo que cumple los criterios de aceptación, en el módulo que corresponde a su capa. Nada más.
   2. Si es lógica pura, escribir sus tests en `tests/test_<modulo>.py` en el mismo paso.
   3. `pytest -q`. Arreglar hasta que pase.
   4. Hacer la verificación que dice "Verificar" en la story (una vez). Si la story agrega una opción de lectura al menú, agregarla a `tests/smoke_input.txt`.
   5. **Actualizar `docs/guia.md`:** la sección del módulo tocado (cada clase/método/función nueva: qué hace, qué recibe, qué devuelve, por qué está ahí y qué error lanza) y, si la story cambia el flujo, el "Recorrido de un caso". Si usa un concepto de Python por primera vez, agregarlo a la tabla "Conceptos de Python usados".
   6. Marcar la story `[x]` en el spec y en `docs/README.md`.
   7. Agregar un borrador `[REVISAR]` en `docs/registro_prompts.md` con el formato de ese archivo: prompt = el pedido de la story en una línea, propuesta = qué se implementó y qué alternativa se descartó, verificación = pasos 3 y 4. "Decisión" queda en blanco: la completa Tomás.
   8. Commit: `git add -A && git commit -m "F03.2: <qué>"`.
   9. Si pasan 20 minutos y no funciona: stub que funcione + `TODO:` en `docs/decisions.md` + commit + siguiente story.
3. **Al terminar la feature:** correr `/check`. Responder en 3–5 líneas: qué quedó hecho, qué quedó como TODO y cuál es la próxima story según `docs/README.md`.

No hacer: branches, PRs, refactors fuera de la story, tests del menú, agentes revisores, ni nada de la lista "Evitar" de `CLAUDE.md`.
