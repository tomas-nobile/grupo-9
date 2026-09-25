# F04 · Alertas de reabastecimiento

**Prioridad:** P0 (.1, .2) · P1 (.3) · **Depende de:** F01, F03 · **CLAUDE.md:** "Contratos" → Alerta

**Objetivo:** la app dice qué hay que reponer, cuánto pedir y cuánto costaría. Es el corazón del TP: lo primero que se muestra en el oral.

## Stories

### [x] F04.1 · Calcular alertas
Como dueño del almacén, quiero una lista de los productos que hay que reponer con la cantidad sugerida, para armar el pedido al proveedor.

- `modelos.py`: `FACTOR_STOCK_OBJETIVO = 2`. `Producto.esta_en_alerta(self) -> bool` (`stock <= stock_minimo`), `Producto.cantidad_sugerida(self) -> int` (`stock_minimo * FACTOR_STOCK_OBJETIVO - stock`, nunca negativo), `Producto.costo_reposicion(self) -> float` (`cantidad_sugerida * precio`), `Producto.valor_stock(self) -> float` (`stock * precio`).
- `Inventario.alertas(self) -> list[Producto]`: productos en alerta ordenados por urgencia: primero `stock == 0`, después por `stock / stock_minimo` ascendente (si `stock_minimo == 0`, usar 1 para no dividir por cero). `Inventario.costo_total_reposicion(self) -> float`.
- Reemplazar en F03.2 la comparación inline por `esta_en_alerta()`.
- Tests (`test_modelos.py` y `test_inventario.py`): justo en el mínimo está en alerta; por encima no; stock 0 va primero; cantidad sugerida y costo correctos; `stock_minimo = 0` no rompe.
- Guía: 4.1, 4.3 y una explicación en palabras de la regla de reposición (por qué el doble del mínimo).

**Verificar:** `pytest -q`.

### [x] F04.2 · Mostrar alertas
Como usuario, quiero ver las alertas al entrar a la app y desde el menú, para no olvidarme de reponer.

- `main.py`: `mostrar_alertas(productos: list[Producto], costo_total: float) -> None`: tabla código · nombre · stock · mínimo · pedir · costo, con el total al pie. Si no hay: "Sin productos para reponer". `opcion_ver_alertas(inventario)` (`10`).
- Al arrancar, antes del menú: "⚠ N productos para reponer (opción 10)" o "Stock en orden".
- Agregar `10` al smoke. Guía: 4.5.

**Verificar:** `python main.py` muestra el aviso al arrancar y `10` la tabla.

### [x] F04.3 · Exportar orden de compra
Como dueño, quiero exportar las alertas a un CSV, para mandárselo al proveedor.

- `persistencia.py`: `RUTA_ORDEN_COMPRA = "datos/orden_compra.csv"`, `exportar_orden_compra(productos: list[Producto], ruta) -> int`: escribe `codigo, nombre, cantidad, costo_estimado` por producto en alerta y una última fila `TOTAL`; devuelve la cantidad de productos exportados. Error de escritura → `ErrorInventario`.
- `main.py`: `opcion_exportar_orden(inventario)` (`11`): exporta y confirma ruta y cantidad.
- Test: exportar 2 productos a `tmp_path` genera un archivo con encabezado + 2 filas + TOTAL.
- Guía: 4.2 y 4.5.

**Verificar:** `11` y abrir `datos/orden_compra.csv`.
