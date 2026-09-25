# F01 · Esqueleto, modelos y datos de ejemplo

**Prioridad:** P0 (MVP) · **Depende de:** — · **CLAUDE.md:** "Stack y layout", "Contratos", "Comandos"

**Objetivo:** la app arranca, los modelos existen y validan, los datos se cargan y guardan, y hay datos de ejemplo realistas para demostrar todo lo demás.

## Stories

### [x] F01.1 · Modelos, persistencia de productos y menú
Como usuario, quiero correr `python main.py` y ver un menú con mis productos, para empezar a usar la app sin configurar nada.

- `requirements.txt`: `pandas`, `matplotlib`, `pytest`, `jupyter`, versiones fijadas con `==` a las que se instalen en el venv.
- `modelos.py`:
  - `class ErrorInventario(Exception)`: la única excepción propia del proyecto.
  - `class Producto` con `__init__(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int, stock_minimo: int)`. Normaliza `codigo` a mayúsculas sin espacios y valida: código y nombre no vacíos, precio > 0, stock y stock_minimo enteros ≥ 0. Lanza `ErrorInventario` con mensaje que diga qué campo y por qué. Métodos: `a_dict(self) -> dict` y `__repr__`.
  - Función `producto_desde_dict(datos: dict) -> Producto` (convierte tipos y delega la validación al constructor; una clave faltante → `ErrorInventario`).
- `persistencia.py`: `RUTA_PRODUCTOS = "datos/productos.json"`, `cargar_productos(ruta: str = RUTA_PRODUCTOS) -> list[Producto]` y `guardar_productos(productos: list[Producto], ruta: str = RUTA_PRODUCTOS) -> None`. Archivo inexistente → `ErrorInventario("No se encontró ...")`; JSON roto → `ErrorInventario("El archivo ... no es un JSON válido")`. Guardar con `ensure_ascii=False`, `indent=2`.
- `inventario.py`: `class Inventario` con `__init__(self, productos: list[Producto], movimientos: list[Movimiento] | None = None)`, `listar(self) -> list[Producto]` (copia ordenada por código) y `obtener(self, codigo: str) -> Producto | None`.
- `datos/productos.json`: 12–15 productos de almacén/kiosco en 3–4 categorías (`almacen`, `bebidas`, `limpieza`, `golosinas`). Al menos 3 con `stock <= stock_minimo` y uno con stock 0, para que las alertas tengan qué mostrar.
- `main.py`: `main()` carga productos (si falla, muestra el mensaje y sale), arma el `Inventario` y entra al `while True`. `mostrar_menu()`, `pedir_opcion() -> str`, `mostrar_productos(productos: list[Producto]) -> None` (tabla alineada con f-strings). Opciones: `1` Listar productos, `0` Salir. Opción inválida → mensaje y vuelve.
- `README.md` stub: título, qué es en una línea, cómo correr. Se completa en F07.1.
- Tests: `tests/test_modelos.py` (producto válido se crea; precio 0, stock negativo, código vacío lanzan `ErrorInventario`; `a_dict` devuelve las 6 claves; `producto_desde_dict` con clave faltante lanza). `tests/test_persistencia.py` (ruta inexistente lanza; guardar y cargar en `tmp_path` devuelve productos iguales). `tests/test_inventario.py` (`obtener` existente e inexistente).
- `docs/guia.md`: secciones 4.1, 4.2, 4.3 (lo que existe) y 4.5; primeras filas de la tabla de conceptos.

**Verificar:** `python main.py` muestra el menú, `1` lista los productos, `0` sale. `pytest -q` verde.

### [x] F01.2 · Movimientos: modelo, persistencia y datos de ejemplo
Como usuario, quiero que la app arranque con un historial de entradas y salidas, para que los indicadores y gráficos tengan datos desde el primer día.

- `modelos.py`: `class Movimiento` con `__init__(self, fecha: str, codigo: str, tipo: str, cantidad: int)`. Valida fecha ISO (`datetime.date.fromisoformat`), tipo en `("entrada", "salida")`, cantidad entero > 0. `a_dict(self) -> dict`, `__repr__`. Constantes `TIPO_ENTRADA = "entrada"`, `TIPO_SALIDA = "salida"`. Función `movimiento_desde_dict(datos: dict) -> Movimiento`.
- `persistencia.py`: `RUTA_MOVIMIENTOS = "datos/movimientos.csv"`, `cargar_movimientos(ruta) -> list[Movimiento]` (`csv.DictReader`; archivo inexistente → lista vacía, no error: un inventario nuevo no tiene historial) y `agregar_movimiento(movimiento: Movimiento, ruta) -> None` (append con `csv.DictWriter`, escribe el encabezado si el archivo no existe o está vacío).
- `datos/movimientos.csv`: encabezado y 40–60 filas de los últimos 21 días hasta hoy, coherentes con los stocks: los productos en alerta tienen más salidas que entradas. Generarlo una vez con un script descartable; se commitea el CSV, no el script.
- `main.py`: `main()` también carga movimientos y se los pasa al `Inventario`.
- Tests: `Movimiento` válido; fecha mal formada, tipo `venta`, cantidad 0 lanzan. `cargar_movimientos` con ruta inexistente devuelve `[]`; `agregar_movimiento` en `tmp_path` dos veces y `cargar_movimientos` devuelve 2 con `cantidad` como `int`.
- Guía: sección 4.1 y 4.2 actualizadas.

**Verificar:** `python -c "import persistencia; print(len(persistencia.cargar_movimientos()))"` imprime 40 o más.

### [x] F01.3 · Recorrido no interactivo (smoke)
Como desarrollador, quiero correr el menú sin tocar el teclado, para verificar en un comando que nada rompe después de cada story.

- `tests/smoke_input.txt`: una respuesta por línea; recorre cada opción de solo lectura del menú con datos válidos y termina con `0`. Cada story que agrega una opción de lectura lo actualiza.
- `pedir_opcion()` atrapa `EOFError` (se acabó el input) y devuelve `"0"`, así el programa sale limpio.
- El smoke solo recorre opciones de lectura (listar, buscar, alertas, indicadores, gráfico) para no modificar `datos/`.

**Verificar:** `python main.py < tests/smoke_input.txt` termina sin traceback; `echo $?` da `0`.
