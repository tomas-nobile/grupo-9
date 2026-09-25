# F08 · Fuente externa: cotización del dólar

**Prioridad:** P0 (.1, .2) · P2 (.3) · **Depende de:** F01, F04.1, F05.1 · **CLAUDE.md:** "Stack y layout", "Contratos" → Cotización, "Gotchas"

**Objetivo:** la app consulta una API pública para obtener la cotización del dólar y muestra el valor del inventario y el costo de reposición en USD. Si no hay internet, usa la última cotización guardada y lo avisa. Cubre el requisito "fuente de datos externa mediante API" de la consigna y da un caso claro de manejo de errores para el oral.

**API:** [DolarApi](https://dolarapi.com), gratuita, sin clave. `GET https://dolarapi.com/v1/dolares/oficial` responde:

```json
{"moneda": "USD", "casa": "oficial", "nombre": "Oficial", "compra": 1495, "venta": 1545, "fechaActualizacion": "2026-09-25T18:00:00.000Z"}
```

Se usa `venta` (lo que cuesta comprar un dólar), porque el indicador responde "cuántos dólares vale lo que tengo en stock".

## Stories

### [x] F08.1 · Obtener la cotización con respaldo local
Como dueño, quiero que la app traiga la cotización del día sola, y que siga funcionando si no hay internet.

- `requirements.txt`: agregar `requests` con versión fijada.
- `fuente_externa.py` (capa DATOS):
  - Constantes `URL_COTIZACION = "https://dolarapi.com/v1/dolares/oficial"` y `TIMEOUT_SEGUNDOS = 5`.
  - `interpretar_cotizacion(datos: dict) -> dict`: función pura. Valida que existan `venta` y `fechaActualizacion`, que `venta` sea número > 0, y devuelve `{"venta": float, "fecha": "YYYY-MM-DD", "origen": "api"}`. Si algo falta o es inválido lanza `ErrorInventario("La API devolvió una cotización inválida")`.
  - `obtener_cotizacion(ruta_cache: str = RUTA_COTIZACION) -> dict`: hace `requests.get(URL_COTIZACION, timeout=TIMEOUT_SEGUNDOS)`, `raise_for_status()`, `.json()`, `interpretar_cotizacion`, guarda la caché con `persistencia.guardar_cotizacion` y devuelve el dict. Si falla la red (`requests.RequestException`), la respuesta no es JSON (`ValueError`) o la cotización es inválida (`ErrorInventario`): carga la caché con `persistencia.cargar_cotizacion`, cambia `origen` a `"cache"` y la devuelve. Si tampoco hay caché, lanza `ErrorInventario("No se pudo obtener la cotización y no hay una guardada")`.
- `persistencia.py`: `RUTA_COTIZACION = "datos/cotizacion.json"`, `guardar_cotizacion(cotizacion: dict, ruta) -> None`, `cargar_cotizacion(ruta) -> dict` (archivo inexistente o roto → `ErrorInventario`). `persistencia.py` sigue siendo el único módulo que abre archivos; `fuente_externa.py` es el único que usa la red.
- `datos/cotizacion.json`: se commitea una caché inicial, así la demo funciona aunque en el aula no haya wifi.
- Tests (`tests/test_fuente_externa.py`):
  - `interpretar_cotizacion` con la respuesta de ejemplo de arriba devuelve `venta` 1545.0 y fecha `2026-09-25`.
  - Sin `venta`, con `venta` 0 o con `venta` texto lanza `ErrorInventario`.
  - Con `monkeypatch` reemplazando `requests.get` por una función que lanza `requests.ConnectionError` y una caché en `tmp_path`: devuelve la caché con `origen == "cache"`.
  - Lo mismo sin caché: lanza `ErrorInventario`.
  - Los tests nunca llaman a la API real.
- Guía: sección 4.7 (`fuente_externa.py`), 4.2 (funciones nuevas de caché), filas nuevas en la tabla de errores (sin internet, API caída, respuesta inválida, sin caché) y fila "API con `requests`" en la tabla de conceptos, explicando qué es un GET, qué es el timeout y por qué hay caché.

**Verificar:** `python -c "import fuente_externa; print(fuente_externa.obtener_cotizacion())"` imprime `origen: api`. Con el wifi apagado imprime `origen: cache`.

### [x] F08.2 · Valores en dólares en el menú
Como dueño, quiero ver cuánto vale mi inventario y cuánto cuesta reponer en dólares, para comparar con precios de proveedores o con meses anteriores.

- `analisis.py`: `analizar_valor_inventario(inventario, cotizacion: float | None = None) -> pd.DataFrame` suma la columna `valor_usd = valor / cotizacion` cuando se pasa cotización. `analisis.py` no llama a la API: recibe el número por parámetro, así se testea sin red.
- `main.py`: `opcion_ver_valor_usd(inventario)` (`14`):
  - Llama a `fuente_externa.obtener_cotizacion()` dentro de `try/except ErrorInventario`.
  - Muestra la cotización, su fecha y su origen: "Cotización oficial: $1545 (API, 2026-09-25)" o "(guardada del 2026-09-20, sin conexión)".
  - Muestra el valor total del inventario en pesos y en USD, la tabla por categoría con ambas columnas y el costo total de reposición (F04.1) en pesos y en USD.
  - Si falla sin caché, muestra el mensaje y vuelve al menú sin romper.
- Test (`tests/test_analisis.py`): con cotización 1000 y un inventario de valor 50000, `valor_usd` da 50.0; sin cotización la columna no existe.
- Agregar `14` al smoke. El smoke puede usar la red; si no hay, pasa igual por la caché.
- Guía: 4.4, 4.5 y actualizar el diagrama de la sección 2 con `fuente_externa.py`.

**Verificar:** `python main.py`, opción `14` con y sin wifi.

### [ ] F08.3 · Cotización en la notebook (P2)
Como estudiante, quiero mostrar en la notebook de dónde vienen los datos externos.

- `analisis.ipynb`: celda después de los indicadores que llama a `fuente_externa.obtener_cotizacion()`, muestra el dict y la tabla de valor por categoría con `valor_usd`. Una línea de markdown que explique la caché.
- Guía: 4.6.

**Verificar:** la notebook ejecuta completa con `nbconvert`.
