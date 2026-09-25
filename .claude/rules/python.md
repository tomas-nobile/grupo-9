---
paths:
  - "*.py"
  - "tests/**"
---

# Python

- Respetar las capas de `CLAUDE.md` → "Stack y layout" y la dirección de los imports. Si algo no encaja en ninguna capa, va en la más baja que lo pueda contener, no en `main.py`.
- `main.py`: solo el menú (`while True` + `if/elif`), funciones `pedir_*` que envuelven `input()` con `try/except ValueError`, funciones `mostrar_*` que imprimen tablas con f-strings y anchos fijos, y una función `main()` que arma el `Inventario` y corre el loop. Cada opción del menú es una función `opcion_<nombre>(inventario)` de 5–15 líneas.
- `modelos.py`: clases `Producto` y `Movimiento` con `__init__` que valida y lanza `ErrorInventario`, métodos de una responsabilidad (`esta_en_alerta`, `cantidad_sugerida`, `valor_stock`), `a_dict()` para persistir y `__repr__` corto para debug. Sin herencia ni dataclasses.
- `inventario.py`: clase `Inventario` que guarda `self.productos: list[Producto]` y `self.movimientos: list[Movimiento]`. Todo cambio de stock pasa por `registrar_movimiento`. Los métodos que modifican validan primero y lanzan `ErrorInventario` si algo falla, sin dejar el estado a medias. Los métodos de consulta devuelven listas nuevas, no modifican.
- `persistencia.py`: funciones puras de entrada/salida (`cargar_productos(ruta) -> list[Producto]`, `guardar_productos(productos, ruta) -> None`, …). Único lugar con `open()`. Atrapa `FileNotFoundError`, `json.JSONDecodeError`, `OSError` y relanza `ErrorInventario` con mensaje en español. Rutas por parámetro, con las constantes por defecto (`RUTA_PRODUCTOS`) arriba del módulo.
- `fuente_externa.py`: único módulo que importa `requests`. Separar la parte pura (`interpretar_cotizacion(datos: dict) -> dict`, testeable sin red) de la parte con red (`obtener_cotizacion`). Siempre `timeout`. Atrapar `requests.RequestException` y `ValueError` y caer a la caché; la caché se lee y escribe a través de `persistencia.py`.
- `analisis.py`: funciones `analizar_*` reciben un `Inventario` (o listas), arman el `DataFrame` adentro con `[p.a_dict() for p in ...]` y devuelven un `DataFrame` o un número. Funciones `graficar_*` guardan en `graficos/<nombre>.png` con título, ejes con etiqueta, leyenda si hay más de una serie, `plt.tight_layout()`, y devuelven la ruta. Nada de pandas fuera de este módulo y la notebook.
- Cada clase, método y función: nombre en español (`snake_case`, clases en `PascalCase`), anotaciones de tipo en parámetros y retorno, docstring de una línea que diga qué hace. Si necesita más de una línea para explicarse, va a `docs/guia.md`.
- `try/except` en los bordes: archivos en `persistencia.py`, red en `fuente_externa.py`, conversión de `input` en `main.py`, `ErrorInventario` en las `opcion_*` de `main.py`. Nunca `except:` a secas ni `except Exception`.
- Constantes en mayúsculas arriba del módulo. Sin números mágicos en la lógica: `FACTOR_STOCK_OBJETIVO = 2`.
- Tests: `tests/test_<modulo>.py`, funciones `test_<que>_<caso>`, objetos armados en el test (una función `_producto(**cambios)` de ayuda por archivo está bien), archivos en `tmp_path`. Por método o función importante: un caso normal, uno límite y uno inválido (`pytest.raises(ErrorInventario)`).
- Ver la lista "Evitar" de `CLAUDE.md` → "Qué se puede usar".
