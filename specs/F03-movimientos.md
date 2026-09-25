# F03 · Movimientos de stock

**Prioridad:** P0 (.1, .2) · P1 (.3) · **Depende de:** F01, F02.2 · **CLAUDE.md:** "Contratos"

**Objetivo:** el stock cambia solo a través de movimientos registrados con fecha, y una salida nunca deja stock negativo.

## Stories

### [x] F03.1 · Registrar entrada
Como usuario, quiero registrar que llegó mercadería, para que el stock suba y quede en el historial.

- `Inventario.registrar_movimiento(self, codigo: str, tipo: str, cantidad: int, fecha: str | None = None) -> Movimiento`: `fecha` por defecto hoy (`datetime.date.today().isoformat()`). Busca el producto (inexistente → `ErrorInventario`), crea el `Movimiento` (que valida tipo y cantidad), aplica el cambio a `producto.stock`, lo agrega a `self.movimientos` y lo devuelve. Todo valida antes de tocar nada.
- `main.py`: `opcion_registrar_entrada(inventario)` (`7`): pide código y cantidad, llama a `registrar_movimiento(codigo, TIPO_ENTRADA, cantidad)`, y si no hubo error guarda productos y agrega el movimiento al CSV con `persistencia`.
- Tests: entrada suma stock y agrega un movimiento; cantidad 0 lanza y no cambia nada; código inexistente lanza.
- Guía: 4.3 y 4.5.

**Verificar:** registrar una entrada, ver el stock nuevo en `1` y la fila nueva al final de `datos/movimientos.csv`.

### [x] F03.2 · Registrar salida
Como usuario, quiero registrar una venta o consumo, y que la app no me deje sacar más de lo que hay.

- `registrar_movimiento` con `tipo = TIPO_SALIDA`: si `cantidad > producto.stock` lanza `ErrorInventario("Stock insuficiente de <nombre>: hay N, se pidieron M")` sin cambiar nada.
- `main.py`: `opcion_registrar_salida(inventario)` (`8`). Si después de la salida `producto.esta_en_alerta()` (F04.1; hasta entonces comparar `stock <= stock_minimo`), imprimir "⚠ <nombre> quedó en el mínimo o por debajo (stock N, mínimo M)".
- Tests: salida resta; salida mayor al stock lanza y el stock queda intacto; salida que deja stock exactamente 0 es válida.
- Guía: **sección 3 "Recorrido de un caso"** completa con este flujo (camino feliz y camino con error), 4.3 y 5.

**Verificar:** intentar sacar 999 de un producto muestra el error; sacar la cantidad justa deja 0 y muestra el aviso.

### [ ] F03.3 · Ver historial
Como usuario, quiero ver los últimos movimientos, o los de un producto, para entender qué pasó con el stock.

- `Inventario.movimientos_de(self, codigo: str | None = None, ultimos: int = 20) -> list[Movimiento]`: filtra por código si se pasa y devuelve los últimos `ultimos` (los más recientes están al final de la lista).
- `main.py`: `mostrar_movimientos(movimientos: list[Movimiento])` (tabla fecha · código · tipo · cantidad) y `opcion_ver_movimientos(inventario)` (`9`): pide código (Enter = todos).
- Tests: filtro por código; `ultimos=2` devuelve los 2 últimos en orden.
- Agregar `9` al smoke. Guía: 4.3 y 4.5.

**Verificar:** `9` con Enter muestra 20 filas; con un código muestra solo las suyas.
