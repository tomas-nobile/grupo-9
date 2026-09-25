---
description: Verificación rápida de que todo funciona
---

Correr en orden. Si un paso depende de algo que todavía no existe (por ejemplo la notebook antes de F06.2), marcarlo como "pendiente", no como fallo.

1. `pytest -q` verde.
2. `python main.py < tests/smoke_input.txt` termina sin traceback y con código 0.
3. `python -c "import modelos, inventario, persistencia, analisis"` importa sin error. `grep -c "^def \|^    def " *.py` da 4 o más funciones/métodos con anotaciones.
4. Dirección de imports: ningún `import main` fuera de `main.py`; `modelos.py` no importa nada del proyecto; `pandas`/`matplotlib` solo en `analisis.py` y la notebook (`grep -n "^import\|^from" *.py`).
5. Si existe `analisis.ipynb`: `jupyter nbconvert --to notebook --execute --inplace analisis.ipynb` ejecuta sin error.
6. `docs/guia.md`: cada clase y función pública de `*.py` aparece nombrada en la guía (`grep -o "^def [a-z_]*\|^class [A-Za-z]*\|^    def [a-z_]*" *.py` contra la guía). Listar las que falten.
7. `grep -n "TODO" docs/decisions.md`: listar los TODOs abiertos.
8. `git status --short`: nada sin commitear.

Responder con una tabla: paso · ok/fail/pendiente · detalle en una línea. Si algo falla, proponer el `/fix` exacto.
