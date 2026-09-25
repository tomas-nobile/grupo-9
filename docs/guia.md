# Guía para entender el proyecto

Este documento explica cómo está hecho el sistema para poder defenderlo en el oral. Conviene leerlo con el editor abierto al lado.

Cómo leerla: primero "Qué hace" y "Arquitectura" (5 minutos). Después, el "Recorrido de un caso", siguiendo el código función por función. El detalle de cada módulo queda para cuando haga falta.

## 1. Qué hace

Un almacén o kiosco tiene productos. Cada uno tiene un **stock** (cuántas unidades hay) y un **stock mínimo** (por debajo de eso hay que reponer). La app es un menú de consola que permite:

- ver, buscar y filtrar productos, y darlos de alta, modificarlos y eliminarlos (opciones 1 a 6);
- registrar **entradas** (llegó mercadería) y **salidas** (se vendió), que son la única forma de cambiar el stock (7 a 9);
- ver las **alertas de reabastecimiento**: qué hay que reponer, cuánto pedir y cuánto cuesta, y exportarlo como orden de compra (10 y 11);
- ver **indicadores** calculados con pandas: valor del inventario, días de cobertura, más vendidos y productos sin ventas (12);
- generar **gráficos** con matplotlib (13);
- consultar la **cotización del dólar** en una API pública y ver el inventario en dólares (14).

Los datos viven en `datos/`. Los productos se guardan en `productos.json` y el historial de movimientos en `movimientos.csv`. La última cotización del dólar queda en `cotizacion.json`, como respaldo para cuando no hay internet.

## 2. Arquitectura

Hay cinco módulos, uno por responsabilidad. Cada uno solo usa a los que están más abajo en el dibujo.

```
┌──────────────────────────────────────────────────────────────┐
│  main.py · PRESENTACIÓN                                       │
│  menú, leer/pedir_* (input), mostrar_* (print), opcion_*      │
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

- **La pantalla está separada de la lógica.** `main.py` solo pregunta y muestra. Por eso la lógica se prueba con pytest sin simular el teclado, y la notebook la reusa tal cual.
- **Un solo módulo toca archivos.** `persistencia.py` concentra todos los `try/except` de lectura y escritura.
- **Un solo módulo usa la red.** Si la API cambia o se cae, solo se toca `fuente_externa.py`. El resto de la app recibe un número y no sabe de dónde vino.
- **Los modelos validan en el constructor.** Un `Producto` con precio negativo no puede existir, así que el resto del código confía en los datos que recibe.
- **Hay una excepción propia.** `ErrorInventario` hace que `main.py` maneje todos los errores de negocio con un solo `except`, mostrando el mensaje al usuario.

**Por qué POO si no se vio en la cursada.** El problema tiene tres conceptos claros: producto, movimiento e inventario. Una clase junta los datos de cada uno con lo que se puede hacer con ellos. Por ejemplo, un producto sabe si está en alerta (`producto.esta_en_alerta()`), en vez de tener una función suelta que recibe un diccionario. Se usó solo lo básico: clases con `__init__`, atributos y métodos. No hay herencia, salvo que `ErrorInventario` extiende `Exception`.

## 3. Recorrido de un caso: registrar una salida

Es el caso que mejor muestra el sistema, porque pasa por todas las capas. Supongamos que se vendieron 15 kilos de azúcar (código `A002`, stock 25, mínimo 10).

**Camino feliz**

1. `main()` está en el `while True`. Muestra el menú con `mostrar_menu()` y lee la opción con `leer("Opción: ")`. El usuario escribe `8`.
2. `ejecutar_opcion("8", inventario)` recorre la lista `OPCIONES`, encuentra la tupla `("8", "Registrar salida de stock", opcion_registrar_salida)` y llama a `opcion_registrar_salida(inventario)`.
3. `opcion_registrar_salida` llama a `registrar_y_guardar(inventario, TIPO_SALIDA)`, que se comparte con la opción de entradas:
   - `pedir_texto("Código: ")` lee `a002`, y `inventario.obtener_o_error("a002")` devuelve el objeto `Producto` del azúcar. Se muestra el stock actual.
   - `pedir_entero("Cantidad de salida: ", minimo=1)` repregunta hasta recibir un entero mayor o igual a 1. Si se escribe `abc`, el `int()` lanza `ValueError`, se atrapa y se vuelve a preguntar.
4. `inventario.registrar_movimiento("A002", "salida", 15)`, en `inventario.py`:
   - busca el producto con `obtener_o_error`;
   - como no se pasó fecha, usa la de hoy;
   - crea `Movimiento(fecha, "A002", "salida", 15)`, cuyo constructor valida la fecha, el tipo y que la cantidad sea un entero mayor a 0;
   - como es una salida, controla que `15 <= stock`, y como 15 es menor que 25, resta: el stock queda en 10;
   - agrega el movimiento a `self.movimientos` y lo devuelve.
5. De vuelta en `registrar_y_guardar`:
   - `persistencia.guardar_productos(inventario.productos)` reescribe `productos.json` con el stock nuevo;
   - `persistencia.agregar_movimiento(...)` agrega una línea al final de `movimientos.csv`.
6. `opcion_registrar_salida` pregunta `producto.esta_en_alerta()`. Da `10 <= 10`, o sea `True`, y se imprime `ALERTA: Azúcar 1kg quedó en el mínimo o por debajo`.
7. Se vuelve al `while True` de `main()`.

**Camino con error: cantidad mayor al stock**

En el paso 4, si se piden 999 unidades, `registrar_movimiento` lanza `ErrorInventario("Stock insuficiente de Azúcar 1kg: hay 25, se pidieron 999.")` **antes de tocar el stock**. La excepción no se atrapa en `registrar_y_guardar` ni en `opcion_registrar_salida`, así que sube hasta el `try/except ErrorInventario` del loop de `main()`. Ahí se imprime `Error: Stock insuficiente...` y se vuelve al menú. Como la excepción cortó la ejecución antes del paso 5, **no se guarda nada**.

## 4. Módulo por módulo

### 4.1 `modelos.py`: los datos y sus reglas

No importa nada del proyecto. Es la base de todo.

| Nombre | Qué es / qué hace |
|---|---|
| `TIPO_ENTRADA`, `TIPO_SALIDA`, `TIPOS_MOVIMIENTO` | Constantes para no escribir `"salida"` a mano en todos lados: un error de tipeo sería un bug silencioso. |
| `FACTOR_STOCK_OBJETIVO = 2` | Al reponer se apunta a tener el doble del mínimo. |
| `class ErrorInventario(Exception)` | Error de negocio con un mensaje para el usuario. Heredar de `Exception` es lo que permite hacer `raise` y `except`. |
| `_validar_texto(valor, campo) -> str` | Devuelve el texto sin espacios en los bordes. Si está vacío, lanza `ErrorInventario`. El `_` inicial indica que es de uso interno del módulo. |
| `_validar_entero_no_negativo(valor, campo) -> int` | Exige un entero mayor o igual a 0. Usa `type(valor) is not int` para rechazar también `2.5`. |
| `class Producto` | Un producto: `codigo`, `nombre`, `categoria`, `precio`, `stock`, `stock_minimo`. |
| `Producto.__init__(...)` | Se ejecuta al crear el objeto. Valida cada campo y normaliza: el código va en mayúsculas y sin espacios, la categoría en minúsculas y el precio como float. Si algo está mal, lanza `ErrorInventario` y el objeto no se crea. |
| `Producto.a_dict() -> dict` | Convierte el objeto en diccionario con las claves del JSON. Lo usan `persistencia` para guardar y `analisis` para armar el DataFrame. |
| `Producto.esta_en_alerta() -> bool` | Devuelve `stock <= stock_minimo`. |
| `Producto.cantidad_sugerida() -> int` | Calcula `stock_minimo * 2 - stock`, y nunca devuelve un número negativo (`max(..., 0)`). |
| `Producto.costo_reposicion() -> float` | Devuelve cantidad sugerida por precio. |
| `Producto.valor_stock() -> float` | Devuelve stock por precio: la plata inmovilizada en ese producto. |
| `producto_desde_dict(datos) -> Producto` | Arma un `Producto` a partir de un diccionario leído del JSON. Convierte los tipos con `float()` e `int()`. Una clave faltante (`KeyError`) o un número inválido (`ValueError`) se convierte en `ErrorInventario`. |
| `class Movimiento` | Una entrada o salida: `fecha`, `codigo`, `tipo`, `cantidad`. |
| `Movimiento.__init__(...)` | Valida la fecha con `datetime.date.fromisoformat` (formato `AAAA-MM-DD`), el tipo (`entrada`/`salida`) y la cantidad (entero mayor a 0). |
| `Movimiento.a_dict() -> dict` | Devuelve la fila del CSV como diccionario. |
| `movimiento_desde_dict(datos) -> Movimiento` | Arma un `Movimiento` desde una fila del CSV. En el CSV todo es texto, por eso se convierte la cantidad con `int()`. |

**La regla de reposición, en palabras.** Un producto necesita reposición cuando le queda el mínimo o menos. Se pide lo necesario para llegar al **doble del mínimo**. Así queda un colchón igual al mínimo antes de la próxima alerta y no hay que pedir todas las semanas. Ejemplo: yerba con stock 6 y mínimo 10. Está en alerta, y se piden 20 - 6 = 14 unidades.

### 4.2 `persistencia.py`: archivos

Es el único módulo con `open()`. Las rutas se arman desde la carpeta del propio archivo (`CARPETA_BASE`), así la app funciona aunque se ejecute desde otra carpeta.

| Nombre | Qué hace | Errores |
|---|---|---|
| `cargar_productos(ruta) -> list[Producto]` | Lee el JSON, controla que sea una lista y convierte cada dict con `producto_desde_dict`. | Si no existe, está roto o no es una lista, lanza `ErrorInventario`. |
| `guardar_productos(productos, ruta)` | Reescribe el JSON completo con `ensure_ascii=False` (para que las tildes queden legibles) e `indent=2`. | Un `OSError` se convierte en `ErrorInventario`. |
| `cargar_movimientos(ruta) -> list[Movimiento]` | Lee el CSV con `csv.DictReader`: cada fila llega como dict. | Si **no existe, devuelve `[]`**, porque un inventario nuevo no tiene historial. |
| `agregar_movimiento(movimiento, ruta)` | Abre en modo `"a"` (agregar al final) y escribe una fila con `csv.DictWriter`. Si el archivo es nuevo, escribe antes el encabezado. | Un `OSError` se convierte en `ErrorInventario`. |
| `exportar_orden_compra(productos, ruta) -> int` | Escribe `datos/orden_compra.csv` con código, nombre, cantidad y costo por producto, más una fila `TOTAL`. Devuelve cuántos productos exportó. | Un `OSError` se convierte en `ErrorInventario`. |
| `guardar_cotizacion(cotizacion, ruta)` / `cargar_cotizacion(ruta) -> dict` | Guardan y leen la caché de la cotización del dólar. | Si falta la caché o está rota, lanzan `ErrorInventario`. |
| `_crear_carpeta_de(ruta)` | Crea la carpeta `datos/` si no existe (`os.makedirs(..., exist_ok=True)`). | |

**Por qué JSON para productos y CSV para movimientos.** Los productos son registros que cambian, así que el archivo se reescribe entero en cada cambio. JSON guarda bien los tipos: números como números. Los movimientos son un historial que solo crece, así que se agrega una línea y nunca se reescribe. CSV es ideal para eso, y pandas lo lee directo como tabla.

### 4.3 `inventario.py`: las reglas del negocio

La clase `Inventario` guarda dos listas: `self.productos` (objetos `Producto`) y `self.movimientos` (objetos `Movimiento`). No lee ni escribe archivos. Recibe los datos ya cargados, y `main.py` decide cuándo guardar.

| Método | Qué hace |
|---|---|
| `listar()` | Devuelve una copia ordenada por código con `sorted(..., key=_codigo_de)`. `_codigo_de` es una función que devuelve el código, y `sorted` la usa para saber por qué ordenar. |
| `obtener(codigo)` | Recorre la lista con un `for` y devuelve el producto o `None`. No distingue mayúsculas. |
| `obtener_o_error(codigo)` | Hace lo mismo que `obtener`, pero si no existe lanza `ErrorInventario`. Lo usan todas las operaciones que necesitan un producto existente. |
| `buscar(texto)` | Devuelve los productos cuyo código o nombre contienen el texto (`texto in nombre.lower()`). Con texto vacío devuelve todos. |
| `categorias()` | Arma la lista de categorías sin repetir, agregando solo si `not in`, y la ordena. |
| `filtrar_por_categoria(categoria)` | Devuelve los productos de esa categoría. |
| `alertas()` | Devuelve los productos con `esta_en_alerta()`, ordenados por `_urgencia`, que es qué fracción del mínimo queda. Con stock 0 la fracción es 0, así que queda primero. Si el mínimo es 0 se usa 1, para no dividir por cero. |
| `costo_total_reposicion()` | Suma `costo_reposicion()` de cada producto en alerta. |
| `agregar(producto)` | Si el código ya existe, lanza `ErrorInventario`. Si no, lo agrega. |
| `modificar(codigo, campo, valor)` | Solo permite los campos de `CAMPOS_MODIFICABLES`. El stock no se toca a mano: se cambia con un movimiento. Arma un **producto nuevo** con el cambio usando `producto_desde_dict`, así lo valida el constructor. Si el valor es inválido, el original queda intacto. Si es válido, lo reemplaza en la misma posición de la lista. |
| `eliminar(codigo)` | Saca el producto con `list.remove` y lo devuelve. |
| `registrar_movimiento(codigo, tipo, cantidad, fecha=None)` | Es **la única forma de cambiar el stock**. Paso a paso en la sección 3. |
| `movimientos_de(codigo=None, ultimos=20)` | Filtra por código si se pasa uno y devuelve los últimos con la porción `lista[-ultimos:]`. |

**Validar antes de modificar.** Todos los métodos que cambian algo primero controlan que todo esté bien y recién después modifican. Si algo falla, el inventario queda exactamente como estaba.

### 4.4 `analisis.py`: pandas y matplotlib

Todas las funciones reciben el `Inventario` y arman los DataFrame adentro. Así `main.py` no necesita pandas, y la notebook usa exactamente los mismos cálculos.

| Función | Qué hace |
|---|---|
| `productos_a_dataframe` / `movimientos_a_dataframe` | Convierten la lista de objetos en tabla: `pd.DataFrame([p.a_dict() for p in ...])`. En movimientos, `pd.to_datetime` convierte la fecha de texto a fecha, para poder restar días. |
| `tabla_como_texto(tabla) -> str` | Arma el `to_string` con dos decimales, separador de miles y `"sin ventas"` donde hay NaN. Es para imprimir en consola. |
| `valor_total_inventario` | **Indicador 1.** Calcula `(precio * stock).sum()`. pandas multiplica columna por columna, fila a fila, sin escribir un `for`. |
| `analizar_valor_inventario(inventario, cotizacion=None)` | **Indicador 1 por categoría.** Agrupa por categoría con `groupby("categoria").agg(...)` y cuenta productos, suma unidades y suma valor. Si recibe una cotización, agrega `valor_usd`. |
| `salidas_recientes(inventario, dias=30)` | Devuelve las salidas de los últimos 30 días. **Cuenta desde el último movimiento registrado, no desde hoy**, para que el análisis no quede vacío si la app no se usa por un tiempo. |
| `_vendido_por_producto` | Suma lo vendido por código con `groupby("codigo")["cantidad"].sum()`. Después hace `merge(..., how="left")` con los productos, para que aparezcan también los que no vendieron nada, con 0. |
| `analizar_cobertura` | **Indicador 2.** Calcula `consumo_diario = vendido / 30` y `dias_cobertura = stock / consumo_diario`. Sin ventas, la cobertura queda en NaN, porque no se puede estimar. Ordena de menor a mayor: los primeros se terminan antes. |
| `analizar_mas_vendidos(top=5)` | **Indicador 3.** Ordena por unidades vendidas y se queda con los primeros (`head(top)`). |
| `analizar_sin_movimiento` | **Extra.** Devuelve los productos con stock que no vendieron nada en 30 días, que son plata inmovilizada. |
| `ventas_por_dia` | Suma las salidas por día. Con `reindex` completa los días sin ventas con 0, así el gráfico no salta días. |
| `graficar_stock_vs_minimo(..., mostrar=False)` | Dibuja barras horizontales con el stock: rojas si el producto está en alerta, verdes si no. Una marca negra señala el mínimo. Están ordenadas de más urgente arriba a menos urgente abajo. |
| `graficar_salidas_por_dia(...)` | Dibuja una línea con las unidades vendidas por día y una línea punteada con el promedio. |
| `_guardar_grafico(figura, ruta, mostrar)` | Aplica `tight_layout` y `savefig` a PNG. Si se pidió, muestra el gráfico con `plt.show()`. Después hace `plt.close` para liberar memoria. |

**Qué agrega la cobertura sobre la alerta simple.** La alerta mira una foto: stock contra mínimo. La cobertura mira la velocidad a la que se vende. Un producto puede estar arriba del mínimo y terminarse en tres días porque se vende mucho. O puede estar en alerta pero casi no venderse. Con las dos cosas juntas se decide mejor qué pedir primero.

### 4.5 `main.py`: el menú

Tiene cuatro grupos de funciones, separados con comentarios:

- **Entrada:** `leer` envuelve `input()`. Si la entrada se termina (`EOFError`), cierra el programa limpio, y eso permite correr el smoke con un archivo. `pedir_texto`, `pedir_entero`, `pedir_decimal` y `elegir_de_lista` **repreguntan** con un `while True` hasta recibir algo válido. `confirmar` pregunta s/n.
- **Salida:** `mostrar_productos`, `mostrar_movimientos`, `mostrar_alertas` y `mostrar_resumen_alertas` imprimen tablas alineadas con f-strings. Por ejemplo, `{p.nombre:<26}` alinea a la izquierda en 26 caracteres.
- **Opciones:** hay una función `opcion_*` por cada opción del menú, todas con la misma firma `(inventario) -> None`. Las que modifican datos guardan con `persistencia` al final. `registrar_y_guardar` es el código común de entradas y salidas.
- **Menú:** `OPCIONES` es una lista de tuplas `(tecla, texto, función)`. En Python una función es un valor más: se puede guardar en una lista y llamarla después. `ejecutar_opcion` busca la tecla en la lista y llama a su función. `main()` carga los datos, muestra el aviso de alertas y corre el `while True` con **un único `try/except ErrorInventario`** para todos los errores de negocio.

| Tecla | Función | Qué llama |
|---|---|---|
| 1 | `opcion_listar_productos` | `inventario.listar()` |
| 2 | `opcion_buscar` | `inventario.buscar(texto)` |
| 3 | `opcion_filtrar_categoria` | `inventario.categorias()` y `filtrar_por_categoria` |
| 4 | `opcion_agregar_producto` | `Producto(...)`, `inventario.agregar`, `guardar_productos` |
| 5 | `opcion_modificar_producto` | `inventario.modificar`, `guardar_productos` |
| 6 | `opcion_eliminar_producto` | `confirmar`, `inventario.eliminar`, `guardar_productos` |
| 7 · 8 | `opcion_registrar_entrada` · `opcion_registrar_salida` | `registrar_y_guardar`, que llama a `registrar_movimiento`, `guardar_productos` y `agregar_movimiento` |
| 9 | `opcion_ver_movimientos` | `inventario.movimientos_de` |
| 10 | `opcion_ver_alertas` | `inventario.alertas()`, `costo_total_reposicion()` |
| 11 | `opcion_exportar_orden` | `persistencia.exportar_orden_compra` |
| 12 | `opcion_ver_indicadores` | `analisis.analizar_*` |
| 13 | `opcion_generar_grafico` | `analisis.graficar_stock_vs_minimo` o `graficar_salidas_por_dia` |
| 14 | `opcion_ver_valor_usd` | `fuente_externa.obtener_cotizacion`, `analisis.analizar_valor_inventario(..., venta)` |
| 0 | `opcion_salir` | `sys.exit(0)` |

`sys.stdout.reconfigure(encoding="utf-8")` al principio de `main()` hace que las tildes se vean bien en cualquier terminal de Windows, incluida Git Bash.

### 4.6 `analisis.ipynb`: la notebook

Carga los mismos datos con `persistencia` y el `Inventario`, y usa las funciones de `analisis`. Tiene cinco partes:

1. productos: `head`, `describe` y cantidad por categoría;
2. movimientos: entradas contra salidas y ventas por día, con un gráfico de línea hecho en la notebook;
3. los cuatro indicadores, más un gráfico de barras de valor por categoría hecho en la notebook;
4. las alertas y el gráfico de stock contra mínimo de la app;
5. la cotización del dólar.

Termina con conclusiones escritas para el dueño del almacén. Está guardada **con las salidas**, así se ve completa sin ejecutarla.

### 4.7 `fuente_externa.py`: la API del dólar

**Qué es la API.** [DolarApi](https://dolarapi.com) es un servicio gratuito, que no pide clave. Una petición `GET` a `https://dolarapi.com/v1/dolares/oficial` devuelve un JSON como este:

```json
{"moneda": "USD", "casa": "oficial", "compra": 1495, "venta": 1545, "fechaActualizacion": "2026-09-25T18:00:00.000Z"}
```

Se usa `venta`: lo que cuesta comprar un dólar.

- `interpretar_cotizacion(datos) -> dict` es una función pura, que no usa la red. Controla que existan `venta` y `fechaActualizacion` y que `venta` sea un número positivo. Reduce la respuesta a `{"venta", "fecha", "origen": "api"}`. Si algo está mal, lanza `ErrorInventario`. Está separada para poder testearla sin internet.
- `obtener_cotizacion(ruta_cache) -> dict` hace el pedido y guarda el resultado en la caché:
  1. `requests.get(URL, timeout=5)`: el **timeout** evita que el menú quede colgado si la red no responde;
  2. `raise_for_status()`: si la API respondió con un error HTTP (404, 500), lanza una excepción;
  3. `respuesta.json()` convierte el texto en diccionario, e `interpretar_cotizacion` lo valida;
  4. guarda el resultado en `datos/cotizacion.json`.

  Si cualquiera de estos pasos falla (sin internet, API caída, respuesta que no es JSON, datos inválidos), el `except` usa `_cotizacion_guardada`. Esa función devuelve la última cotización con `origen: "cache"`, y `main.py` avisa que es la guardada. Si tampoco hay caché, lanza `ErrorInventario`.

`analisis.py` no llama a la API. Recibe el número por parámetro, así sus tests no dependen de internet.

## 5. Manejo de errores

| Qué puede fallar | Dónde se detecta | Qué pasa | Qué ve el usuario |
|---|---|---|---|
| Falta `productos.json` o está roto | `persistencia.cargar_productos` (`FileNotFoundError`, `JSONDecodeError`) | Se relanza como `ErrorInventario` | "Error al cargar los datos: ..." y el programa termina, porque sin productos no hay nada que hacer |
| Falta `movimientos.csv` | `persistencia.cargar_movimientos` | Devuelve `[]` | Nada: la app arranca sin historial |
| Letras donde va un número | `main.pedir_entero` / `pedir_decimal` (`ValueError`) | Se repregunta | "Tiene que ser un número entero, por ejemplo 12." |
| Número fuera de rango (precio 0, cantidad 0) | `main.pedir_*` | Se repregunta | "Tiene que ser mayor a 0." |
| Código repetido al agregar | `main.opcion_agregar_producto` e `Inventario.agregar` | `ErrorInventario` | "Error: Ya existe un producto con código A001." |
| Código inexistente | `Inventario.obtener_o_error` | `ErrorInventario` | "Error: No existe un producto con código Z9." |
| Salida mayor al stock | `Inventario.registrar_movimiento` | `ErrorInventario`, sin tocar nada | "Error: Stock insuficiente de ...: hay 25, se pidieron 999." |
| Intentar cambiar el stock desde "modificar" | `Inventario.modificar` | `ErrorInventario` | "El stock no se modifica a mano: registrá una entrada o una salida." |
| Opción de menú inexistente | `main.ejecutar_opcion` devuelve `False` | Se vuelve al menú | "Opción inválida. Elegí un número del menú." |
| No se puede escribir un archivo | `persistencia.*` (`OSError`) | `ErrorInventario` | "Error: No se pudo guardar ..." |
| Sin internet, API caída o respuesta inválida | `fuente_externa.obtener_cotizacion` | Usa la caché | "SIN CONEXIÓN: se usa la cotización guardada del ..." |
| Sin internet y sin caché | `fuente_externa._cotizacion_guardada` | `ErrorInventario` | "Error: No se pudo obtener la cotización y no hay una guardada." |
| Se termina la entrada (archivo del smoke) | `main.leer` (`EOFError`) | `sys.exit(0)` | "Fin de la entrada. Hasta luego." |

Nunca se usa `except:` a secas ni `except Exception`, porque ocultarían errores de programación reales. Cada `except` atrapa solo lo que se espera que pueda fallar ahí.

## 6. Conceptos de Python usados y dónde

| Concepto | Dónde se ve | Nota |
|---|---|---|
| Variables, tipos (`str`, `int`, `float`, `bool`) y conversión | `main.pedir_entero` (`int(...)`), `modelos.producto_desde_dict` | Todo lo que llega de `input()` o del CSV es texto: hay que convertirlo. |
| `if/elif/else` | `Inventario.registrar_movimiento` (entrada o salida), `main.opcion_modificar_producto` | |
| `for` y `while` | `for` en todas las búsquedas de `inventario.py`, `while True` en el menú y en los `pedir_*` | `continue` en `pedir_entero` vuelve al principio del `while`. |
| Listas | `Inventario.productos`, `OPCIONES`, `lista[-20:]` en `movimientos_de` | |
| Tuplas | `CAMPOS_MODIFICABLES`, `TIPOS_MOVIMIENTO`, cada opción del menú | Se usan para datos que no cambian. |
| Diccionarios | `Producto.a_dict()`, filas del CSV, respuesta de la API | |
| Funciones con anotaciones de tipo | Todas | Por ejemplo, `def obtener(self, codigo: str) -> Producto \| None`. |
| Clases, `__init__`, `self`, métodos | `modelos.py`, `inventario.py` | `self` es el objeto sobre el que se llama el método. |
| Excepción propia, `raise`, `try/except` | `ErrorInventario`, en todos los módulos | Ver la sección 5. |
| Módulos e `import` | Ver la sección 2 | `import persistencia` y `from modelos import Producto`. |
| JSON | `persistencia.py` | `json.load` y `json.dump`. |
| CSV | `persistencia.py` | `csv.DictReader` y `csv.DictWriter`. |
| `datetime` | `Movimiento.__init__`, `registrar_movimiento` | `fromisoformat` valida la fecha y `today()` da la fecha de hoy. |
| API con `requests` (GET, JSON, timeout) | `fuente_externa.py` | GET pide datos a una URL, `.json()` los convierte en diccionario y `timeout` pone un límite de espera. |
| pandas (`DataFrame`, `groupby`, `agg`, `merge`, `sort_values`, `where`) | `analisis.py` | Operan sobre columnas enteras sin escribir `for`. |
| matplotlib (`barh`, `scatter`, `plot`, `savefig`) | `analisis.graficar_*`, notebook | |
| pytest (`assert`, `pytest.raises`, `tmp_path`, `monkeypatch`) | `tests/` | Ver la sección 7. |

## 7. Cómo se prueba

**Tests automáticos** con `pytest -q`, que tienen que dar todos verdes:

| Archivo | Tests | Qué cubre |
|---|---|---|
| `tests/test_modelos.py` | 20 | Productos y movimientos válidos e inválidos (precio 0, stock negativo o decimal, código vacío, fecha mal escrita, tipo `venta`), conversión desde dict, reglas de alerta y reposición. |
| `tests/test_inventario.py` | 30 | Búsqueda, filtro, alta con código repetido, modificación válida e inválida (el producto queda igual), baja, entradas, salidas (stock insuficiente sin cambios, salida que deja 0), historial y orden de las alertas. |
| `tests/test_persistencia.py` | 6 | Archivo inexistente, JSON roto, guardar y volver a cargar da lo mismo, CSV nuevo con encabezado, orden de compra. Usa `tmp_path`, una carpeta temporal que da pytest, para no tocar `datos/`. |
| `tests/test_analisis.py` | 14 | Los cuatro indicadores con números calculables a mano (por ejemplo, 30 unidades en 30 días con stock 10 dan 10 días de cobertura), la ventana de 30 días, el valor en dólares y que los gráficos se generen. |
| `tests/test_fuente_externa.py` | 7 | La respuesta de la API válida e inválida. Con `monkeypatch` se reemplaza `requests.get` por una función falsa, para simular la API o la falta de internet **sin usar la red**. |

Cada función importante tiene al menos un caso normal, uno límite y uno inválido.

**Smoke.** `python main.py < tests/smoke_input.txt` recorre todas las opciones de consulta del menú con respuestas escritas en un archivo, y tiene que terminar sin errores. No modifica `datos/`.

**Casos manuales para mostrar en el oral:**

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Válido | Opción 8, `A002`, `15` | El stock del azúcar pasa de 25 a 10 y aparece "ALERTA: Azúcar 1kg quedó en el mínimo" |
| Inválido | Opción 8, `A002`, `999` | "Error: Stock insuficiente de Azúcar 1kg: hay 10, se pidieron 999." El stock no cambia |
| Inválido de tipo | Opción 4, código nuevo, precio `abc` | "Tiene que ser un número..." y repregunta |
| Límite | Opción 10 | El detergente, con stock 5 y mínimo 5, aparece en alerta porque la regla es `<=`, y pide 5 |
| Sin internet | Opción 14 con el wifi apagado | Muestra el valor en dólares con "SIN CONEXIÓN: se usa la cotización guardada" |

Después de la demo, para volver a los datos originales:

```bash
git checkout datos/
```

## 8. Preguntas probables del oral

**¿Por qué POO si no se vio en clase?**
Porque el problema tiene tres conceptos claros (producto, movimiento, inventario) y cada clase junta sus datos con sus reglas. Por ejemplo, `producto.esta_en_alerta()`. Se usó solo lo básico: `__init__`, atributos y métodos.

**¿Por qué JSON para productos y CSV para movimientos?**
Los productos cambian y se reescriben enteros, y JSON conserva los tipos. Los movimientos solo se agregan al final, y CSV es una tabla que pandas lee directo.

**¿Por qué pedir hasta el doble del mínimo?**
Así queda un colchón igual al mínimo antes de la próxima alerta y no hay que pedir todo el tiempo. Es una constante (`FACTOR_STOCK_OBJETIVO`): cambiarla es cambiar una línea.

**¿Qué pasa si borro `datos/productos.json`?**
`cargar_productos` lanza `ErrorInventario("No se encontró el archivo de productos")`, `main()` lo muestra y termina sin romper. Si se borra `movimientos.csv`, arranca sin historial.

**¿Qué pasa si no hay internet durante la demo?**
La opción 14 usa la última cotización guardada en `datos/cotizacion.json` y lo avisa. El resto de la app no usa internet.

**¿Por qué el dólar oficial y el valor de venta?**
Es la referencia más estable. Venta es lo que cuesta comprar un dólar, que es lo que responde "cuántos dólares vale mi stock". Cambiar a blue es cambiar la URL.

**¿Qué hace pandas que no haría con listas?**
Agrupar, sumar y cruzar tablas en una línea (`groupby`, `merge`). Con listas harían falta diccionarios acumuladores y varios `for`. Además, los resultados salen como tabla lista para mostrar o graficar.

**¿Por qué los últimos 30 días se cuentan desde el último movimiento y no desde hoy?**
Para que los indicadores no queden vacíos si la app no se usa por un tiempo, o si los datos de ejemplo son de otra fecha.

**¿Cómo sé que funciona?**
Hay 77 tests con casos normales, límite e inválidos, un smoke que recorre el menú, y los casos manuales de la sección 7.

**¿Qué cambiaría con más tiempo?**
- Guardar productos y movimientos de forma atómica: hoy, si falla la segunda escritura, quedan desincronizados.
- Búsqueda que ignore tildes.
- Mínimos que se ajusten solos según la cobertura.
- Historial de precios.
