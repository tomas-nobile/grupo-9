# F06 · Gráfico y notebook

**Prioridad:** P0 (.1, .2) · P2 (.3) · **Depende de:** F04, F05 · **CLAUDE.md:** "Gotchas" → matplotlib

**Objetivo:** una visualización clara y pertinente (stock vs. mínimo con los productos en alerta resaltados) generada desde la app, y una notebook que explora los datos con pandas y saca conclusiones.

## Stories

### [x] F06.1 · Gráfico stock vs. mínimo
Como dueño, quiero ver de un vistazo qué productos están por debajo del mínimo.

- `analisis.py`: `RUTA_GRAFICOS = "graficos"`. `graficar_stock_vs_minimo(inventario, ruta: str = "graficos/stock_vs_minimo.png") -> str`: barras horizontales con `stock` por producto (etiqueta `nombre`), ordenadas por `stock / stock_minimo`; barra roja si `esta_en_alerta()`, verde si no; marca del `stock_minimo` de cada producto (un punto negro sobre la barra); título "Stock actual vs. stock mínimo", ejes con etiqueta, leyenda (En alerta / OK / Mínimo), `tight_layout`, `savefig(ruta, dpi=120)`, `plt.close()`; devuelve `ruta`. Crea la carpeta con `os.makedirs(exist_ok=True)`.
- `main.py`: `opcion_generar_grafico(inventario)` (`13`): guarda, imprime la ruta e intenta `plt.show()` dentro de `try`; si falla (sin display), avisa que quedó el PNG.
- Test: con 3 productos y `ruta` en `tmp_path` crea el archivo (`os.path.exists`). `matplotlib.use("Agg")` al inicio de `tests/test_analisis.py`.
- Agregar `13` al smoke. Guía: 4.4, 4.5 y fila de matplotlib.

**Verificar:** abrir `graficos/stock_vs_minimo.png`: se distinguen los rojos y se lee cada nombre.

### [ ] F06.2 · Notebook de análisis
Como estudiante, quiero una notebook que muestre la exploración con pandas y las conclusiones, porque la consigna la pide y sirve para explicar los datos en el oral.

- `analisis.ipynb` en la raíz. Celdas, en este orden, con una celda markdown de una o dos líneas antes de cada bloque:
  1. Título, objetivo, `import persistencia, analisis` + `from inventario import Inventario`, carga de `datos/` y armado del `Inventario`.
  2. `DataFrame` de productos (`analisis.productos_a_dataframe`): `head()`, `describe()`, cantidad por categoría.
  3. `DataFrame` de movimientos: entradas vs. salidas totales, salidas por día (gráfico de línea hecho en la notebook).
  4. Los tres indicadores de F05 llamando a las funciones `analizar_*` (no repetir la lógica).
  5. Gráfico de F06.1 (llamando a `graficar_stock_vs_minimo` y mostrándolo) y un segundo gráfico propio de la notebook: valor de inventario por categoría (barras).
  6. Conclusiones en markdown: qué productos hay que reponer ya, cuál es el más vendido, cuánta plata hay en stock, qué decisión tomaría el dueño.
- Ejecutar completa y guardar con las salidas (`jupyter nbconvert --to notebook --execute --inplace analisis.ipynb`).
- Guía: 4.6.

**Verificar:** `/check` paso 5 pasa; abrir la notebook y ver los gráficos renderizados.

### [x] F06.3 · Gráfico de salidas por día (P2)
Como dueño, quiero ver la evolución de las ventas en el último mes.

- `graficar_salidas_por_dia(inventario, dias: int = 30, ruta: str = "graficos/salidas_por_dia.png") -> str`: línea de suma de salidas por fecha.
- `main.py`: la opción `13` pregunta cuál de los dos gráficos generar.

**Verificar:** abrir el PNG.
