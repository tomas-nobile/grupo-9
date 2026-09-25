---
description: Checklist de entrega según la consigna y armado del ZIP
---

Revisar y arreglar lo que falte, en este orden. Marcar cada ítem en la respuesta.

1. `/check` pasa completo (sin "pendiente").
2. Requisitos técnicos de la consigna, verificados con grep o lectura:
   - ≥ 4 funciones propias con anotaciones de tipo (todas las funciones y métodos con `->` en la firma).
   - `try`/`except` presente (`grep -n "except" *.py`).
   - ≥ 2 módulos `.py` (hay 6).
   - JSON y CSV en `datos/`, con datos.
   - Fuente externa: `datos/cotizacion.json` existe y la opción `14` funciona con y sin conexión.
   - `pandas` y `matplotlib` importados y usados en `analisis.py`.
   - `graficos/*.png` existe y se ve bien (abrir uno).
   - `analisis.ipynb` ejecutada con las salidas guardadas (los gráficos se ven al abrirla sin correr nada).
3. `README.md` tiene todas las secciones de `specs/F07-entrega.md` → F07.1.
4. `docs/guia.md` completa: sin secciones vacías ni `[PENDIENTE]`, y el "Recorrido de un caso" coincide con el código actual.
5. `docs/registro_prompts.md`: ≥ 3 entradas completas, `grep -c REVISAR` da 0.
6. `requirements.txt` instala en un venv limpio: `python -m venv "$TEMP/venv-check" && "$TEMP/venv-check/Scripts/pip" install -r requirements.txt`.
7. `git status` limpio y push a `main`.
8. Armar el ZIP en la carpeta padre con **solo**: `main.py`, `inventario.py`, `modelos.py`, `persistencia.py`, `fuente_externa.py`, `analisis.py`, `analisis.ipynb`, `datos/`, `graficos/`, `tests/`, `requirements.txt`, `README.md`, `docs/guia.md`, `docs/registro_prompts.md`. Sin `.venv`, `__pycache__`, `.git`, `.claude`, `specs/`.
   Nombre: el que dice `docs/README.md` → "Entrega". Armarlo con Python (`shutil.make_archive` sobre una carpeta temporal con esos archivos copiados), no depender de `zip` en Git Bash.
9. Listar el contenido del ZIP (`python -m zipfile -l ../<NOMBRE>.zip`) y confirmar que abre y que no pesa más de unos MB.
