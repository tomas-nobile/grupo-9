# Guion del oral (5 minutos)

Antes de empezar:

- dejar abiertos una terminal en la carpeta del proyecto con el venv activado, el editor con `inventario.py` y `docs/guia.md`, y `graficos/stock_vs_minimo.png`;
- correr `git checkout datos/` para arrancar con los datos de ejemplo.

## 0:00 · El problema (30 s)

"Un almacén necesita saber qué reponer antes de quedarse sin stock. Mi app registra productos y movimientos, avisa qué hay que pedir, cuánto y cuánto cuesta, y calcula indicadores para decidir mejor."

## 0:30 · Demo (2:30)

1. `python main.py`. Aparece el aviso: "ALERTA: 5 productos para reponer".
2. **Opción 10:** las alertas. "El agua está primera porque no tiene stock. Se sugiere pedir hasta el doble del mínimo. Hay que invertir $ 138.900."
3. **Opción 8, `A002`, `15`:** una venta de azúcar. El stock pasa de 25 a 10 y aparece la alerta nueva. "Quedó justo en el mínimo, y la regla es menor o igual."
4. **Opción 8, `A002`, `999`:** "Stock insuficiente". "La validación está en la clase `Inventario`, antes de tocar nada. No se guardó nada."
5. **Opción 12:** los indicadores. "Valor del inventario, días de cobertura y más vendidos, todos con pandas. La yerba dura 6 días al ritmo actual."
6. **Opción 13 → 1 → s:** el gráfico. "En rojo, lo que hay que reponer. La marca negra es el mínimo."
7. **Opción 14:** en dólares. "La cotización viene de una API. Si no hay internet, usa la última guardada y lo avisa."

## 3:00 · Código (1:00)

- Mostrar el diagrama de capas de `docs/guia.md`, sección 2. "`main.py` solo habla con el usuario. La lógica está en `Inventario`, los datos en `persistencia`, el análisis en `analisis`."
- Mostrar `Inventario.registrar_movimiento`: "valida, resta y registra. Es la única forma de cambiar el stock."
- Mostrar un test: `test_salida_mayor_al_stock_lanza_y_no_cambia`. Correr `pytest -q` y mostrar los 77 tests en verde.

## 4:00 · Uso de IA (30 s)

"Usé Claude Code con especificaciones por feature. Modifiqué su propuesta inicial: le pedí POO y una guía para poder explicar el código. Rechacé el hook automático de prompts. Un error que cometió fue un salto de línea que rompió `main.py`. Los tests pasaban igual porque no cubren el menú. Lo detectó el smoke. Está todo en `docs/registro_prompts.md`."

## 4:30 · Cierre y preguntas

"Lo que mejoraría: que el mínimo se ajuste solo según la cobertura, y guardar los dos archivos de forma atómica."

Las respuestas a las preguntas probables están en `docs/guia.md`, sección 8.
