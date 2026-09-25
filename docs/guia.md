# Guía para entender el proyecto

Este documento explica cómo está hecho el sistema para poder defenderlo en el oral. Se completa story a story (`/feature` actualiza la sección del módulo que toca) y se cierra en F07. Las partes marcadas `[PENDIENTE]` todavía no tienen código detrás.

Cómo leerla: primero "Qué hace" y "Arquitectura" (5 minutos), después "Recorrido de un caso" siguiendo el código con el editor abierto, y por último el módulo por módulo cuando haga falta el detalle.

## 1. Qué hace

Un almacén/kiosco tiene productos con un stock y un stock mínimo. La app permite:

- ver, buscar y filtrar productos; darlos de alta, modificarlos y eliminarlos;
- registrar entradas (llega mercadería) y salidas (se vende o se consume), que son la única forma de cambiar el stock;
- ver **alertas de reabastecimiento**: qué productos están en o por debajo del mínimo, cuánto pedir y cuánto costaría;
- ver **indicadores** calculados con pandas: valor del inventario, días de cobertura por producto y productos más vendidos;
- generar un **gráfico** de stock actual contra stock mínimo;
- consultar la **cotización del dólar** en una API pública y ver el valor del inventario y el costo de reposición en USD.

Los datos viven en dos archivos: `datos/productos.json` (el inventario) y `datos/movimientos.csv` (el historial). Se cargan al arrancar y se guardan después de cada cambio. La cotización viene de internet y se guarda en `datos/cotizacion.json` como respaldo para cuando no hay conexión.

## 2. Arquitectura

Cuatro capas, un módulo por capa. Cada una solo conoce a las de abajo.

```
┌──────────────────────────────────────────────────────────────┐
│  main.py · PRESENTACIÓN                                       │
│  menú, pedir_* (input), mostrar_* (print), opcion_*           │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
┌───────────────▼───────────┐   ┌───────▼──────────────────────┐
│  inventario.py · DOMINIO   │   │  analisis.py · ANÁLISIS       │
│  clase Inventario          │◄──│  analizar_* (pandas)          │
│  búsqueda, altas, stock,   │   │  graficar_* (matplotlib)      │
│  alertas                   │   │  también lo usa la notebook   │
└───────────────┬───────────┘   └──────────────────────────────┘
                │
┌───────────────▼───────────┐   ┌──────────────────────────────┐
│  modelos.py · MODELOS      │◄──│  persistencia.py · DATOS      │
│  Producto, Movimiento,     │   │  cargar/guardar JSON y CSV    │
│  ErrorInventario           │   │  único módulo que abre archivos│
└───────────────────────────┘   └──────────────▲───────────────┘
                                               │ caché
                                ┌──────────────┴───────────────┐
                                │  fuente_externa.py · DATOS    │
                                │  cotización USD (DolarApi)    │
                                │  único módulo que usa la red  │
                                └──────────────────────────────┘
```

Por qué así:

- **Separar la pantalla de la lógica** permite probar la lógica con pytest sin simular el teclado, y reusar la lógica desde la notebook.
- **Un solo lugar que toca archivos** (`persistencia.py`) concentra todos los `try/except` de entrada/salida.
- **Un solo lugar que usa la red** (`fuente_externa.py`): si la API cambia o se cae, solo se toca ese módulo, y el resto de la app recibe un número y no sabe de dónde vino.
- **Los modelos validan en el constructor**: un `Producto` mal armado no puede existir, así que el resto del código confía en sus datos.
- **Una excepción propia** (`ErrorInventario`) hace que `main.py` maneje todos los errores de negocio con un solo `except`, mostrando el mensaje al usuario.

## 3. Recorrido de un caso: registrar una salida

`[PENDIENTE]` Se escribe en F03.2. Debe seguir el camino completo: el usuario elige la opción → `main.opcion_registrar_salida` pide código y cantidad con `pedir_*` → `Inventario.registrar_movimiento` busca el producto, valida stock suficiente, crea un `Movimiento`, descuenta el stock → `persistencia.guardar_productos` y `persistencia.agregar_movimiento` escriben los archivos → `main` muestra la confirmación y, si el producto quedó en alerta, el aviso. Y el camino con error: cantidad mayor al stock → `ErrorInventario` → mensaje → menú.

## 4. Módulo por módulo

Para cada clase, método y función: qué hace, qué recibe, qué devuelve, por qué está ahí, qué error lanza.

### 4.1 `modelos.py`

`[PENDIENTE]` F01.1.

### 4.2 `persistencia.py`

`[PENDIENTE]` F01.1, F01.2, F04.3.

### 4.3 `inventario.py`

`[PENDIENTE]` F01.1, F02, F03, F04.

### 4.4 `analisis.py`

`[PENDIENTE]` F05, F06.

### 4.5 `main.py`

`[PENDIENTE]` F01.1 y cada story que agrega una opción.

### 4.6 `analisis.ipynb`

`[PENDIENTE]` F06.2, F08.3.

### 4.7 `fuente_externa.py`

`[PENDIENTE]` F08.1. Explicar: qué es la API y qué devuelve, por qué se separa `interpretar_cotizacion` (pura) de `obtener_cotizacion` (con red), el timeout, y el camino de respaldo a la caché.

## 5. Manejo de errores

`[PENDIENTE]` Tabla: qué puede fallar · dónde se detecta · qué excepción · qué ve el usuario. Se completa a medida que aparecen casos (archivo inexistente, JSON roto, número inválido, código repetido, stock insuficiente, sin display para el gráfico, sin internet, API con respuesta inválida, sin caché de cotización).

## 6. Conceptos de Python usados y dónde

| Concepto | Dónde se ve | Nota |
|---|---|---|
| Clases, `__init__`, métodos | `modelos.py`, `inventario.py` | `[PENDIENTE]` |
| Excepción propia y `try/except` | `modelos.ErrorInventario`, `persistencia.py`, `main.py` | `[PENDIENTE]` |
| Listas y diccionarios | `Inventario.productos`, `Producto.a_dict()` | `[PENDIENTE]` |
| Funciones con anotaciones de tipo | todos los módulos | `[PENDIENTE]` |
| `for` / `while` / `if` | menú de `main.py`, búsquedas en `inventario.py` | `[PENDIENTE]` |
| Módulos e `import` | ver "Arquitectura" | `[PENDIENTE]` |
| JSON y CSV | `persistencia.py` | `[PENDIENTE]` |
| API con `requests` (GET, JSON, timeout) | `fuente_externa.py` | `[PENDIENTE]` |
| pandas (`DataFrame`, `groupby`, `merge`) | `analisis.py` | `[PENDIENTE]` |
| matplotlib | `analisis.graficar_*` | `[PENDIENTE]` |
| pytest | `tests/` | `[PENDIENTE]` |

## 7. Cómo se prueba

`[PENDIENTE]` Qué cubre cada `tests/test_<modulo>.py`, qué es el smoke y qué casos manuales se muestran en el oral (uno válido, uno inválido, uno límite).

## 8. Preguntas probables del oral

`[PENDIENTE]` Se completa en F07.3. Mínimo: por qué POO si no se vio en clase; por qué JSON para productos y CSV para movimientos; por qué la regla de reposición es `stock_minimo * 2 - stock`; qué pasa si borro `datos/productos.json`; qué pasa si no hay internet durante la demo; por qué el dólar oficial y el valor de venta; qué hace pandas que no haría con listas; qué cambiaría con más tiempo.
