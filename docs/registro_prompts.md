# Registro de uso de IA

**Herramienta:** Claude Code, un asistente de programación que trabaja en la terminal sobre los archivos del proyecto.

**Modo de trabajo:**
- Primero acordé con la IA qué construir y cómo. Eso quedó escrito en `CLAUDE.md` y en una especificación por feature (`specs/`), con criterios de aceptación y cómo verificar cada una.
- Después la IA implementó story por story, con tests y un commit por story. Cada decisión técnica quedó anotada en `docs/decisions.md`.
- Yo revisé las propuestas, cambié lo que no me cerraba y verifiqué el resultado corriendo la app y los tests.

A continuación, los cuatro prompts más significativos.

---

## 1 · Definir el proyecto antes de programar

**Prompt:**
> "Tengo que hacer un proyecto de control de inventario y alertas de reabastecimiento siguiendo esta consigna. Armá la configuración del proyecto y el CLAUDE.md. Haceme preguntas y confirmemos cómo quedaría antes de terminar. Armá el git también."

**Respuesta de la IA:** leyó la consigna y me hizo dos rondas de preguntas: tipo de interfaz, fuente de datos externa, rubro del negocio, idioma del código, forma de trabajo, registro de prompts, repositorio y tests. Con mis respuestas propuso:
- un menú de consola;
- dos módulos, `main.py` y `funciones.py`, como sugiere la consigna;
- **no usar clases**, porque POO no está en el cronograma de la materia;
- un hook que guardara automáticamente cada prompt;
- siete features con sus criterios de aceptación;
- un repositorio en GitHub.

**Decisión: modificada.**
- **Acepté** el menú de consola, el rubro almacén/kiosco, el código en español, las especificaciones por feature y los tests con pytest.
- **Rechacé** el hook automático de prompts y cualquier automatización tipo GitHub Actions. Para un trabajo de este tamaño agregan complejidad que no necesito y que tendría que explicar.
- **Cambié** la propuesta de no usar clases. Pedí que se hiciera **con POO aunque no esté en el programa**, limpio y bien modularizado, y con una **guía en `docs/` para entender el código**. En el oral tengo que explicar cómo funciona. Con clases, cada concepto del problema (producto, movimiento, inventario) tiene su lugar, y con la guía puedo recorrerlo paso a paso.

La IA rehízo la estructura: cinco módulos en capas y el esqueleto de `docs/guia.md`.

**Verificación:** revisé la estructura de archivos y las especificaciones antes de que se creara nada. Después controlé en el commit inicial que estuvieran los archivos acordados.

---

## 2 · Agregar una fuente de datos externa

**Prompt:**
> "Agregá una fuente externa o API, agregalo como feature."

**Respuesta de la IA:** primero probó que la API respondiera:

```
GET https://dolarapi.com/v1/dolares/oficial  ->  {"compra": 1495, "venta": 1545, "fechaActualizacion": "2026-09-25T18:00:00.000Z", ...}
```

Después escribió la especificación F08:
- un módulo nuevo, `fuente_externa.py`, que es el único que usa internet;
- trae la cotización del dólar oficial con `requests` y un tiempo máximo de espera de 5 segundos;
- con el valor de venta muestra el inventario y el costo de reposición en dólares;
- si no hay internet, usa la última cotización guardada en `datos/cotizacion.json` y avisa que es la guardada.

Descartó una API de productos ficticios, porque no son productos de un almacén, y un CSV de proveedor, porque no es una API.

**Decisión: aceptada.** Al principio había elegido no usar fuente externa. La consigna la pide "cuando resulte pertinente", y valuar el stock en dólares tiene sentido para un comercio en Argentina. Me convenció el respaldo local: si en el aula no hay wifi, la demo funciona igual. Además deja un caso claro de manejo de errores para mostrar.

**Verificación:**
- Siete tests simulan la API sin usar internet. Cubren una respuesta válida, un valor de venta en 0, un valor de venta con texto, sin internet con cotización guardada y sin internet sin cotización guardada.
- A mano, la opción 14 trajo la cotización real, con origen `api`.
- Con una URL inválida, la app usó la cotización guardada, con origen `cache`.

---

## 3 · Implementar todas las features

**Prompt:**
> "Implementá las features."

**Respuesta de la IA:** implementó las 23 stories en orden, con tests para cada una y un commit por story. En el camino tomó dos decisiones que no estaban en las especificaciones, y las anotó en `docs/decisions.md`:
- **Menú:** la especificación pedía un `if/elif` con 15 ramas y un `try/except` en cada opción. La IA propuso una lista `OPCIONES` con (tecla, texto, función) y **un solo `try/except`** en el loop principal que atrapa todos los errores del negocio.
- **Indicadores:** los de "últimos 30 días" se cuentan desde el **último movimiento registrado**, no desde la fecha de hoy. Si no, los datos de ejemplo quedarían fuera de la ventana el día del oral y todos los indicadores saldrían vacíos.

**Decisión: aceptada, con las dos decisiones incluidas.**
- El menú con la lista queda más corto, y agregar una opción es agregar una función y una línea.
- Guardar funciones dentro de una lista no lo vimos en clase, así que me aseguré de que esté explicado en la guía, sección 4.5.
- La fecha de referencia de los indicadores me pareció necesaria para que la demo muestre datos.

**Verificación:**
- 77 tests automáticos con casos normales, límite e inválidos.
- Un recorrido automático del menú (`python main.py < tests/smoke_input.txt`).
- La notebook se ejecuta completa.
- El ZIP de entrega, instalado en un entorno limpio, pasa los tests y el recorrido.
- A mano probé una venta válida: el azúcar pasó de 25 a 10 y apareció el aviso de alerta. Una venta de 999 unidades mostró "Stock insuficiente" y no cambió nada.

---

## 4 · Un error de la IA detectado al probar

**Contexto:** durante la implementación de la pantalla de indicadores (opción 12), la IA editó `main.py` con un script.

**Qué pasó:** quiso escribir `print(f"\n1) VALOR...")`, pero el `\n` quedó como un salto de línea real dentro del texto. `main.py` quedó con un **error de sintaxis** y la app no arrancaba. **Los tests seguían pasando**, porque prueban la lógica y ninguno importa el menú. El error apareció recién al correr la app.

La IA lo corrigió reemplazando cada `\n` por un `print()` vacío antes de cada título, que además se lee mejor.

Antes, al correr la app por primera vez, apareció otro problema que los tests tampoco detectan. En Git Bash las tildes salían rotas (`Opci�n`), porque Windows usa otra codificación cuando la salida está redirigida. Se resolvió forzando UTF-8 al inicio de `main()`.

**Decisión: aceptada la corrección.** La lección es que los tests no alcanzan: también hay que correr la app. Por eso el recorrido automático del menú (`tests/smoke_input.txt`) se corre después de cada cambio junto con los tests.

**Verificación:** corrí la app, entré a la opción 12 y se vieron las tablas de indicadores. El recorrido automático del menú termina sin errores.
