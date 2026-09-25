"""Punto de entrada: menú de consola del control de inventario.

Este módulo solo habla con el usuario: pide datos, llama a la lógica y muestra resultados.
Las reglas de negocio están en inventario.py y modelos.py.
"""
import sys

import persistencia
from inventario import Inventario
from modelos import ErrorInventario, Producto


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


def opcion_salir(inventario: Inventario) -> None:
    """Termina el programa."""
    print("Hasta luego.")
    sys.exit(0)


# Cada opción del menú: (tecla, texto, función que la resuelve).
OPCIONES = [
    ("1", "Listar productos", opcion_listar_productos),
    ("2", "Buscar producto", opcion_buscar),
    ("3", "Filtrar por categoría", opcion_filtrar_categoria),
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
