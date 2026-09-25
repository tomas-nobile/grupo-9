# F05 · Indicadores con pandas

**Prioridad:** P0 (.1–.3) · P2 (.4) · **Depende de:** F01, F04 · **CLAUDE.md:** `.claude/rules/python.md` → `analisis.py`

**Objetivo:** al menos tres indicadores útiles calculados con pandas, mostrados en el menú y reutilizables desde la notebook. Cada función `analizar_*` recibe el `Inventario`, arma los `DataFrame` adentro (`productos_a_dataframe`, `movimientos_a_dataframe`) y devuelve un `DataFrame`: nada de pandas en `main.py`.

## Stories

### [x] F05.1 · Valor del inventario
Como dueño, quiero saber cuánta plata tengo inmovilizada en stock, total y por categoría.

- `analisis.py`: `productos_a_dataframe(inventario: Inventario) -> pd.DataFrame` y `movimientos_a_dataframe(inventario: Inventario) -> pd.DataFrame` (columna `fecha` como `datetime`). `analizar_valor_inventario(inventario) -> pd.DataFrame`: columna `valor = precio * stock`, `groupby("categoria")` con suma de `valor` y cantidad de productos, ordenado por valor descendente. `valor_total_inventario(inventario) -> float`.
- Tests (`tests/test_analisis.py`): 3 productos en 2 categorías → totales por categoría y total correctos.
- Guía: 4.4 y fila de pandas en la tabla de conceptos.

**Verificar:** `pytest -q`.

### [ ] F05.2 · Consumo diario y días de cobertura
Como dueño, quiero saber cuántos días me dura el stock de cada producto al ritmo actual de ventas, para reponer antes de quedarme sin nada.

- `analizar_cobertura(inventario, dias: int = 30) -> pd.DataFrame`: salidas de los últimos `dias`, `groupby("codigo")` suma de `cantidad` / `dias` = `consumo_diario`; `merge` con productos (`how="left"`, consumo 0 si no hubo salidas); `dias_cobertura = stock / consumo_diario` (consumo 0 → `NaN`, mostrar como "sin ventas"). Columnas: `codigo, nombre, stock, consumo_diario, dias_cobertura`, ordenado por `dias_cobertura` ascendente con los `NaN` al final.
- Tests: producto con 30 unidades vendidas en 30 días y stock 10 → consumo 1.0, cobertura 10; producto sin salidas → consumo 0 y cobertura `NaN`; una salida de hace 40 días no cuenta.
- Guía: 4.4 y explicación en palabras de qué agrega este indicador sobre la alerta simple.

**Verificar:** `pytest -q`.

### [ ] F05.3 · Productos más vendidos
Como dueño, quiero ver el ranking de los productos que más salen, para priorizar qué nunca puede faltar.

- `analizar_mas_vendidos(inventario, top: int = 5) -> pd.DataFrame`: salidas por `codigo`, suma de `cantidad`, `merge` con nombre y categoría, ordenado descendente, `head(top)`.
- Test: con 3 productos y salidas conocidas, el orden del ranking es el esperado y `top=2` devuelve 2.
- Guía: 4.4.

**Verificar:** `pytest -q`.

### [ ] F05.4 · Menú de indicadores
Como usuario, quiero ver los tres indicadores juntos desde el menú.

- `main.py`: `opcion_ver_indicadores(inventario)` (`12`): valor total y tabla por categoría (F05.1), cobertura de los 10 más urgentes (F05.2) y top 5 (F05.3). Usar `df.to_string(index=False)` con `float_format` de 2 decimales.
- P2, si sobra tiempo: `analizar_sin_movimiento(inventario, dias: int = 30) -> pd.DataFrame`, productos sin salidas en el período (stock muerto), agregado a la misma pantalla.
- Agregar `12` al smoke. Guía: 4.5.

**Verificar:** `12` muestra las tres tablas legibles en una pantalla.
