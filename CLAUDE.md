# TP1 · Control de inventario y alertas de reabastecimiento

App de consola en Python para un almacén/kiosco: registra productos y movimientos de stock, avisa qué hay que reponer y cuánto pedir, y muestra indicadores y un gráfico. Es el **Trabajo Práctico 1** de *Elementos de Programación IA y Low Code* (docente Esteban Calcagno). **Entrega por el campus y oral individual de 5 minutos: viernes 2/10/2026.** La consigna completa está en `docs/Consigna_tp1.pdf`; la rúbrica y el checklist están resumidos en `docs/README.md`.

## Modo de trabajo: limpio y explicable

No es un producto: es un TP que hay que **defender en un oral**. Todo lo que se escribe tiene que poder explicarse línea por línea, y `docs/guia.md` tiene que explicarlo. Reglas:

1. **No preguntar.** Ante una decisión, elegir la opción más simple que cumpla los criterios de aceptación de la story, anotarla en una línea en `docs/decisions.md` y seguir. Parar solo si la decisión contradice la consigna.
2. **Trabajar en `main`.** Sin branches, PRs ni issues. **Un commit por story**: `F03.2: salidas de stock con validación`.
3. **Leer solo lo necesario:** el `.md` de la feature y las secciones de este archivo que cita. No leer todos los specs por las dudas.
4. **Verificación mínima por story:**
   - Siempre: `pytest -q` antes de commitear.
   - Lógica pura (modelos, inventario, análisis): tests en `tests/test_<modulo>.py`, escritos junto con el código, no antes.
   - Menú: correr `python main.py` una vez y recorrer la opción nueva. Sin tests del menú.
5. **La guía se escribe con el código.** Cada story que agrega una clase, método o función actualiza su sección en `docs/guia.md` (qué hace, qué recibe, qué devuelve, por qué está ahí). Sin esto la story no está terminada.
6. **Timebox de 20 minutos.** Si algo no sale, dejar un stub que funcione, anotar `TODO:` en `docs/decisions.md` y pasar a la siguiente story.
7. **No refactorizar lo que funciona** ni agregar abstracciones "para después". Una clase por concepto real (producto, movimiento, inventario), no por si acaso.
8. **Registro de IA:** al cerrar cada story, dejar un borrador `[REVISAR]` en `docs/registro_prompts.md` (formato en ese archivo). Tomás decide si fue aceptado, modificado o rechazado.

## Qué se puede usar

POO está fuera del programa de la cursada pero es una decisión del proyecto (ver `docs/decisions.md`): la usamos porque ordena el código y se puede explicar. Todo lo demás sale de las clases 1–7 y de lo que pide la consigna.

**Permitido:** clases con `__init__`, atributos y métodos; una excepción propia (`ErrorInventario`); `@property` y `@classmethod` solo si simplifican de verdad (y se explican en la guía); variables y tipos básicos, `input`/`print`, f-strings, `if/elif/else`, `for`/`while`/`range`, listas, tuplas, diccionarios, funciones con **anotaciones de tipo** (`list[Producto]`, `str | None`), módulos propios, `try`/`except`, `json`, `csv`, `datetime`, `os`, `requests`, `pandas`, `matplotlib`, `monkeypatch` de pytest para simular la API en los tests. Una list comprehension simple está bien.

**Evitar:** herencia (salvo `ErrorInventario(Exception)`), `dataclass`, `lambda`, decoradores propios, generadores, `typing` avanzado (`TypedDict`, `Protocol`, genéricos), comprehensions anidadas, `argparse`, `*args`/`**kwargs`, dunder methods más allá de `__init__` y `__repr__`, librerías que no estén en `requirements.txt`.

## Docs

| Archivo | Para qué |
|---|---|
| `docs/README.md` | Índice de features, plan por día, estado de cada story, orden de corte, rúbrica y checklist de la consigna |
| `specs/FNN-*.md` | Una feature por archivo, con sus stories y criterios de aceptación |
| `docs/guia.md` | **Guía para entender el proyecto**: arquitectura, recorrido de un caso, módulo por módulo, conceptos usados, preguntas del oral. Se completa story a story |
| `docs/decisions.md` | Decisiones y TODOs, una línea cada uno |
| `docs/registro_prompts.md` | Registro de uso de IA que pide la consigna |
| `docs/Consigna_tp1.pdf` | Consigna original |
| `README.md` | Entregable: objetivo, cómo correr, decisiones (se completa en F07) |

## Stack y layout

Python 3.12 · stdlib (`json`, `csv`, `datetime`, `os`) · `requests` (API externa, F08) · `pandas` · `matplotlib` · `pytest` · `jupyter` para la notebook. Entorno: `python -m venv .venv` + `pip install -r requirements.txt`.

Cuatro capas, un módulo por capa, sin paquetes (todo en la raíz para que `python main.py` funcione sin configurar nada):

```
main.py            PRESENTACIÓN: menú de consola, funciones pedir_*/mostrar_*. No tiene lógica de negocio
inventario.py      DOMINIO: clase Inventario (colección de productos y movimientos, búsqueda, altas, movimientos, alertas)
modelos.py         MODELOS: clases Producto y Movimiento (datos + validación), excepción ErrorInventario
persistencia.py    DATOS: cargar/guardar JSON y CSV, exportar orden de compra, caché de cotización. Único módulo que abre archivos
fuente_externa.py  DATOS: cotización del dólar desde DolarApi con requests, con respaldo en caché. Único módulo que usa la red
analisis.py        ANÁLISIS: funciones analizar_* (pandas) y graficar_* (matplotlib). Lo usan main.py y la notebook
analisis.ipynb     exploración con pandas + gráficos + conclusiones (importa persistencia, analisis y fuente_externa)
datos/productos.json     inventario (lista de dicts)
datos/movimientos.csv    historial de entradas y salidas
datos/cotizacion.json    última cotización obtenida de la API (caché, se commitea para que la demo ande sin wifi)
graficos/                PNG generados por la app (se commitean: van en el ZIP)
tests/test_<modulo>.py   pytest, un archivo por módulo de lógica (modelos, inventario, persistencia, fuente_externa, analisis)
tests/smoke_input.txt    entradas para recorrer el menú sin teclado
docs/  specs/            ver arriba
```

**Dependencias entre módulos (solo hacia abajo):** `main` → `inventario`, `persistencia`, `fuente_externa`, `analisis` · `inventario` → `modelos` · `persistencia` → `modelos` · `fuente_externa` → `persistencia`, `modelos` · `analisis` → `inventario`, `modelos`. `modelos` no importa nada del proyecto. `analisis` no llama a la API: recibe la cotización por parámetro.

**Idioma:** todo en español (identificadores, comentarios, mensajes, docs). Identificadores sin tildes ni ñ (`calcular_reposicion`, no `calcular_reposición`). Clases en `PascalCase`, todo lo demás en `snake_case`.

## Comandos

| Comando | Qué hace |
|---|---|
| `python main.py` | Corre la app (menú interactivo) |
| `pytest -q` | Tests de lógica pura. Correr antes de cada commit |
| `python main.py < tests/smoke_input.txt` | Recorrido no interactivo del menú (F01.3), tiene que terminar sin traceback |
| `jupyter notebook analisis.ipynb` | Abre la notebook |
| `jupyter nbconvert --to notebook --execute --inplace analisis.ipynb` | Ejecuta la notebook completa y guarda las salidas |

Slash commands de Claude Code: `/feature F03` (o `F03.2`), `/fix <bug>`, `/next`, `/check`, `/entregar`.

Shell: **Git Bash en Windows**. Usar `/` en paths y `python` (no `py`, no `python3`).

## Contratos (no cambiar sin anotarlo en `docs/decisions.md`)

**Producto** (`modelos.Producto`; en `datos/productos.json` es una lista de dicts con las mismas claves):
```json
{"codigo": "A001", "nombre": "Yerba 500g", "categoria": "almacen", "precio": 2500.0, "stock": 12, "stock_minimo": 10}
```
- `codigo` único, str, en mayúsculas. `precio` float > 0. `stock` y `stock_minimo` int ≥ 0. El constructor valida y lanza `ErrorInventario` con un mensaje claro si algo está mal.

**Movimiento** (`modelos.Movimiento`; en `datos/movimientos.csv`, con encabezado):
```
fecha,codigo,tipo,cantidad
2026-09-20,A001,salida,3
```
- `fecha` ISO `YYYY-MM-DD`. `tipo` es `entrada` o `salida`. `cantidad` int > 0. Una salida nunca deja el stock negativo (lo controla `Inventario.registrar_movimiento`, no el modelo).

**Errores:** la lógica (modelos, inventario, persistencia) lanza `ErrorInventario`; `main.py` la atrapa con `try/except`, muestra el mensaje y vuelve al menú. Los errores de archivo (`FileNotFoundError`, `json.JSONDecodeError`, `OSError`) se atrapan en `persistencia.py` y se relanzan como `ErrorInventario` con un mensaje en español.

**Cotización** (`fuente_externa.obtener_cotizacion()`, caché en `datos/cotizacion.json`):
```json
{"venta": 1545.0, "fecha": "2026-09-25", "origen": "api"}
```
- Fuente: `GET https://dolarapi.com/v1/dolares/oficial`, sin clave, se usa el campo `venta`. `origen` es `api` o `cache`. Si la API falla se usa la caché; si no hay caché, `ErrorInventario`. Detalle en `specs/F08-cotizacion-dolar.md`.

**Alerta:** un producto está en alerta cuando `stock <= stock_minimo` (`Producto.esta_en_alerta()`). Cantidad sugerida a pedir = `stock_minimo * 2 - stock` (`Producto.cantidad_sugerida()`; el stock objetivo es el doble del mínimo). Detalle en `specs/F04-alertas.md`.

## Gotchas

- `input()` siempre devuelve str: convertir con `int()`/`float()` dentro de `try/except ValueError` en las funciones `pedir_*` de `main.py`.
- Guardar JSON con `ensure_ascii=False` e `indent=2` para que se lea bien en el oral.
- `matplotlib` desde consola: siempre `plt.savefig()` a `graficos/` antes de `plt.show()`. En los tests usar `matplotlib.use("Agg")`.
- Los tests nunca leen `datos/`: usan objetos armados en el test y `tmp_path` de pytest para archivos.
- El smoke (`tests/smoke_input.txt`) solo recorre opciones de lectura, así no modifica `datos/` (salvo la caché de cotización, que se refresca sola).
- `requests.get` siempre con `timeout`: sin él, una red caída cuelga el menú. Los tests nunca llaman a la API real: usan `monkeypatch`.
