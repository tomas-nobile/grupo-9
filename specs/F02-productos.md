# F02 · Productos

**Prioridad:** P0 (.1, .2) · P1 (.3) · P2 (.4) · **Depende de:** F01 · **CLAUDE.md:** "Contratos", `.claude/rules/python.md`

**Objetivo:** consultar, buscar, filtrar, agregar y modificar productos, con validación de todo lo que entra por teclado y sin dejar nunca el inventario inconsistente.

## Stories

### [x] F02.1 · Buscar y filtrar
Como usuario, quiero buscar un producto por código o parte del nombre y filtrar por categoría, para encontrar rápido lo que necesito.

- `Inventario.buscar(self, texto: str) -> list[Producto]`: coincide si `texto` (sin distinguir mayúsculas) está en `codigo` o en `nombre`. Texto vacío → todos.
- `Inventario.filtrar_por_categoria(self, categoria: str) -> list[Producto]` y `Inventario.categorias(self) -> list[str]` (únicas, ordenadas).
- `main.py`: `opcion_buscar(inventario)` (`2`) pide texto y muestra resultados o "No se encontraron productos"; `opcion_filtrar_categoria(inventario)` (`3`) lista las categorías numeradas y pide una.
- Tests: búsqueda parcial e insensible a mayúsculas; sin coincidencias → `[]`; categoría inexistente → `[]`; `categorias()` sin repetidos.
- Agregar `2` y `3` al `smoke_input.txt`. Guía: 4.3 y 4.5.

**Verificar:** `python main.py`, opción `2` con "yer" encuentra la yerba.

### [ ] F02.2 · Alta con validación
Como usuario, quiero agregar un producto nuevo y que la app me avise si cargo algo mal, para no ensuciar el inventario.

- `Inventario.agregar(self, producto: Producto) -> None`: lanza `ErrorInventario` si el código ya existe. La validación de campos ya la hace `Producto.__init__`.
- `main.py`: `pedir_entero(mensaje: str) -> int` y `pedir_decimal(mensaje: str) -> float`, que repiten la pregunta hasta recibir un número válido (`try/except ValueError` con mensaje). `pedir_texto(mensaje: str) -> str` que devuelve sin espacios. `opcion_agregar_producto(inventario)` (`4`): pide campo por campo, arma el `Producto` dentro de `try`, llama a `inventario.agregar`, guarda con `persistencia.guardar_productos` y confirma. Cualquier `ErrorInventario` → muestra el mensaje y vuelve al menú sin guardar.
- Tests: agregar válido aumenta `listar()` en 1; código repetido (aun en minúsculas) lanza y no agrega.
- Guía: 4.3, 4.5 y sección 5 (manejo de errores) con los casos de entrada inválida.

**Verificar:** alta con precio "abc" repregunta; alta con código repetido muestra el error y vuelve; alta válida aparece en `1` y en `datos/productos.json`.

### [ ] F02.3 · Modificar producto
Como usuario, quiero cambiar precio, stock mínimo, nombre o categoría de un producto, para mantener el inventario al día.

- `Inventario.modificar(self, codigo: str, campo: str, valor) -> Producto`: campos permitidos `nombre`, `precio`, `stock_minimo`, `categoria`. Arma un `Producto` nuevo con el cambio (así valida el constructor) y reemplaza al viejo en la lista; devuelve el nuevo. Código inexistente o campo no permitido (incluido `stock`: "el stock se cambia con un movimiento") → `ErrorInventario`.
- `main.py`: `opcion_modificar_producto(inventario)` (`5`): pide código, muestra el producto, pide campo (lista numerada) y valor nuevo (con el `pedir_*` que corresponda), guarda.
- Tests: cambiar precio válido; precio inválido lanza y el producto queda igual; código inexistente lanza; campo `stock` lanza.
- Guía: 4.3.

**Verificar:** cambiar el precio de un producto y verlo en `1`.

### [ ] F02.4 · Baja de producto
Como usuario, quiero eliminar un producto que ya no vendo, previa confirmación.

- `Inventario.eliminar(self, codigo: str) -> Producto`: quita y devuelve el producto; inexistente → `ErrorInventario`.
- `main.py`: `opcion_eliminar_producto(inventario)` (`6`): pide código, muestra el producto, pide `s/n`, guarda.
- Tests: eliminar existente reduce la lista en 1 y `obtener` devuelve `None`; inexistente lanza.

**Verificar:** eliminar uno y ver que no aparece en `1`.
