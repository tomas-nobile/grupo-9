"""Punto de entrada: menú de consola del control de inventario.

Este módulo solo habla con el usuario: pide datos, llama a la lógica y muestra resultados.
Las reglas de negocio están en inventario.py y modelos.py.
"""
import sys

import persistencia
from inventario import CAMPOS_MODIFICABLES, Inventario
from modelos import TIPO_ENTRADA, TIPO_SALIDA, ErrorInventario, Movimiento, Producto


# ---------- Entrada: funciones que piden datos por teclado ----------

def leer(mensaje: str) -> str:
    """Lee una línea del teclado. Si la entrada se terminó, cierra el programa."""
    try:
        return input(mensaje).strip()
    except EOFError:
        print("\nFin de la entrada. Hasta luego.")
        sys.exit(0)


def pedir_texto(mensaje: str) -> str:
    """Pide un texto no vacío; repregunta hasta que lo recibe."""
    while True:
        texto = leer(mensaje)
        if texto != "":
            return texto
        print("  No puede quedar vacío.")


def pedir_entero(mensaje: str, minimo: int = 0) -> int:
    """Pide un número entero mayor o igual a `minimo`; repregunta hasta que es válido."""
    while True:
        try:
            numero = int(leer(mensaje))
        except ValueError:
            print("  Tiene que ser un número entero, por ejemplo 12.")
            continue
        if numero >= minimo:
            return numero
        print(f"  Tiene que ser mayor o igual a {minimo}.")


def pedir_decimal(mensaje: str) -> float:
    """Pide un número mayor a 0 (acepta coma o punto decimal); repregunta hasta que es válido."""
    while True:
        try:
            numero = float(leer(mensaje).replace(",", "."))
        except ValueError:
            print("  Tiene que ser un número, por ejemplo 1250.50.")
            continue
        if numero > 0:
            return numero
        print("  Tiene que ser mayor a 0.")


def elegir_de_lista(titulo: str, opciones: list[str]) -> str:
    """Muestra opciones numeradas y devuelve la elegida."""
    print(titulo)
    for numero, opcion in enumerate(opciones, start=1):
        print(f"  {numero}. {opcion}")
    while True:
        eleccion = pedir_entero("Número: ", minimo=1)
        if eleccion <= len(opciones):
            return opciones[eleccion - 1]
        print(f"  Elegí un número entre 1 y {len(opciones)}.")


def confirmar(mensaje: str) -> bool:
    """Pregunta s/n y devuelve True si la respuesta es 's'."""
    return leer(f"{mensaje} (s/n): ").lower() == "s"


# ---------- Salida: funciones que muestran datos ----------

def mostrar_productos(productos: list[Producto]) -> None:
    """Imprime una tabla de productos."""
    if len(productos) == 0:
        print("No se encontraron productos.")
        return
    print(f"{'CÓDIGO':<7}{'NOMBRE':<26}{'CATEGORÍA':<11}{'PRECIO':>10}{'STOCK':>7}{'MÍNIMO':>8}")
    for p in productos:
        print(f"{p.codigo:<7}{p.nombre:<26}{p.categoria:<11}{p.precio:>10.2f}{p.stock:>7}{p.stock_minimo:>8}")


def mostrar_movimientos(movimientos: list[Movimiento]) -> None:
    """Imprime una tabla de movimientos."""
    if len(movimientos) == 0:
        print("No hay movimientos.")
        return
    print(f"{'FECHA':<12}{'CÓDIGO':<8}{'TIPO':<9}{'CANTIDAD':>9}")
    for m in movimientos:
        print(f"{m.fecha:<12}{m.codigo:<8}{m.tipo:<9}{m.cantidad:>9}")


# ---------- Opciones del menú: una función por opción ----------

def opcion_listar_productos(inventario: Inventario) -> None:
    """Muestra todos los productos."""
    mostrar_productos(inventario.listar())


def opcion_buscar(inventario: Inventario) -> None:
    """Busca productos por código o parte del nombre."""
    texto = leer("Código o parte del nombre (Enter = todos): ")
    mostrar_productos(inventario.buscar(texto))


def opcion_filtrar_categoria(inventario: Inventario) -> None:
    """Muestra los productos de una categoría elegida de la lista."""
    categoria = elegir_de_lista("Categorías:", inventario.categorias())
    mostrar_productos(inventario.filtrar_por_categoria(categoria))


def opcion_agregar_producto(inventario: Inventario) -> None:
    """Da de alta un producto nuevo y lo guarda."""
    codigo = pedir_texto("Código: ")
    if inventario.obtener(codigo) is not None:
        raise ErrorInventario(f"Ya existe un producto con código {codigo.upper()}.")
    producto = Producto(
        codigo=codigo,
        nombre=pedir_texto("Nombre: "),
        categoria=pedir_texto("Categoría: "),
        precio=pedir_decimal("Precio: "),
        stock=pedir_entero("Stock inicial: "),
        stock_minimo=pedir_entero("Stock mínimo: "),
    )
    inventario.agregar(producto)
    persistencia.guardar_productos(inventario.productos)
    print(f"Producto {producto.codigo} agregado.")


def opcion_modificar_producto(inventario: Inventario) -> None:
    """Cambia nombre, categoría, precio o stock mínimo de un producto."""
    producto = inventario.obtener_o_error(pedir_texto("Código: "))
    mostrar_productos([producto])
    campo = elegir_de_lista("¿Qué campo querés cambiar?", list(CAMPOS_MODIFICABLES))
    if campo == "precio":
        valor = pedir_decimal("Precio nuevo: ")
    elif campo == "stock_minimo":
        valor = pedir_entero("Stock mínimo nuevo: ")
    else:
        valor = pedir_texto(f"{campo.capitalize()} nuevo: ")
    actualizado = inventario.modificar(producto.codigo, campo, valor)
    persistencia.guardar_productos(inventario.productos)
    print("Producto actualizado:")
    mostrar_productos([actualizado])


def opcion_eliminar_producto(inventario: Inventario) -> None:
    """Elimina un producto, previa confirmación."""
    producto = inventario.obtener_o_error(pedir_texto("Código: "))
    mostrar_productos([producto])
    if not confirmar(f"¿Eliminar {producto.nombre}?"):
        print("No se eliminó nada.")
        return
    inventario.eliminar(producto.codigo)
    persistencia.guardar_productos(inventario.productos)
    print(f"Producto {producto.codigo} eliminado.")


def registrar_y_guardar(inventario: Inventario, tipo: str) -> Producto:
    """Pide código y cantidad, registra el movimiento, lo guarda y devuelve el producto."""
    producto = inventario.obtener_o_error(pedir_texto("Código: "))
    print(f"{producto.nombre}: stock actual {producto.stock}")
    cantidad = pedir_entero(f"Cantidad de {tipo}: ", minimo=1)
    inventario.registrar_movimiento(producto.codigo, tipo, cantidad)
    persistencia.guardar_productos(inventario.productos)
    persistencia.agregar_movimiento(inventario.movimientos[-1])
    print(f"Listo. Stock de {producto.nombre}: {producto.stock}")
    return producto


def opcion_registrar_entrada(inventario: Inventario) -> None:
    """Registra que llegó mercadería."""
    registrar_y_guardar(inventario, TIPO_ENTRADA)


def opcion_registrar_salida(inventario: Inventario) -> None:
    """Registra una venta o consumo y avisa si el producto quedó en el mínimo."""
    producto = registrar_y_guardar(inventario, TIPO_SALIDA)
    if producto.stock <= producto.stock_minimo:
        print(f"ALERTA: {producto.nombre} quedó en el mínimo o por debajo "
              f"(stock {producto.stock}, mínimo {producto.stock_minimo}).")


def opcion_ver_movimientos(inventario: Inventario) -> None:
    """Muestra los últimos movimientos, de todos o de un producto."""
    codigo = leer("Código (Enter = todos): ")
    if codigo == "":
        mostrar_movimientos(inventario.movimientos_de())
    else:
        producto = inventario.obtener_o_error(codigo)
        print(f"Movimientos de {producto.nombre}:")
        mostrar_movimientos(inventario.movimientos_de(producto.codigo))


def opcion_salir(inventario: Inventario) -> None:
    """Termina el programa."""
    print("Hasta luego.")
    sys.exit(0)


# Cada opción del menú: (tecla, texto, función que la resuelve).
OPCIONES = [
    ("1", "Listar productos", opcion_listar_productos),
    ("2", "Buscar producto", opcion_buscar),
    ("3", "Filtrar por categoría", opcion_filtrar_categoria),
    ("4", "Agregar producto", opcion_agregar_producto),
    ("5", "Modificar producto", opcion_modificar_producto),
    ("6", "Eliminar producto", opcion_eliminar_producto),
    ("7", "Registrar entrada de stock", opcion_registrar_entrada),
    ("8", "Registrar salida de stock", opcion_registrar_salida),
    ("9", "Ver movimientos", opcion_ver_movimientos),
    ("0", "Salir", opcion_salir),
]


def mostrar_menu() -> None:
    """Imprime las opciones del menú."""
    print()
    print("=== CONTROL DE INVENTARIO ===")
    for clave, texto, funcion in OPCIONES:
        print(f"{clave:>3}. {texto}")


def ejecutar_opcion(clave: str, inventario: Inventario) -> bool:
    """Ejecuta la función de la opción elegida. Devuelve False si la tecla no existe."""
    for opcion_clave, texto, funcion in OPCIONES:
        if opcion_clave == clave:
            funcion(inventario)
            return True
    return False


def main() -> None:
    """Carga los datos, arma el inventario y corre el menú hasta que el usuario sale."""
    sys.stdout.reconfigure(encoding="utf-8")  # tildes correctas en cualquier terminal de Windows
    try:
        productos = persistencia.cargar_productos()
        movimientos = persistencia.cargar_movimientos()
    except ErrorInventario as error:
        print(f"Error al cargar los datos: {error}")
        return
    inventario = Inventario(productos, movimientos)

    while True:
        mostrar_menu()
        clave = leer("Opción: ")
        try:
            if not ejecutar_opcion(clave, inventario):
                print("Opción inválida. Elegí un número del menú.")
        except ErrorInventario as error:
            # Un solo lugar atrapa todos los errores de negocio: se muestra el mensaje y se vuelve al menú.
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
