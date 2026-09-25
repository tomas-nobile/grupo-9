"""Punto de entrada: menú de consola del control de inventario.

Este módulo solo habla con el usuario: pide datos, llama a la lógica y muestra resultados.
Las reglas de negocio están en inventario.py y modelos.py.
"""
import sys

import persistencia
from inventario import Inventario
from modelos import ErrorInventario, Producto

OPCIONES = [
    ("1", "Listar productos"),
    ("0", "Salir"),
]


def mostrar_menu() -> None:
    """Imprime las opciones del menú."""
    print()
    print("=== CONTROL DE INVENTARIO ===")
    for clave, texto in OPCIONES:
        print(f"{clave:>3}. {texto}")


def pedir_opcion() -> str:
    """Pide una opción del menú. Si se termina la entrada, devuelve '0' para salir."""
    try:
        return input("Opción: ").strip()
    except EOFError:
        return "0"


def mostrar_productos(productos: list[Producto]) -> None:
    """Imprime una tabla de productos."""
    if len(productos) == 0:
        print("No se encontraron productos.")
        return
    print(f"{'CÓDIGO':<7}{'NOMBRE':<26}{'CATEGORÍA':<11}{'PRECIO':>10}{'STOCK':>7}{'MÍNIMO':>8}")
    for p in productos:
        print(f"{p.codigo:<7}{p.nombre:<26}{p.categoria:<11}{p.precio:>10.2f}{p.stock:>7}{p.stock_minimo:>8}")


def opcion_listar_productos(inventario: Inventario) -> None:
    """Opción 1: muestra todos los productos."""
    mostrar_productos(inventario.listar())


def main() -> None:
    """Carga los datos, arma el inventario y corre el menú hasta que el usuario sale."""
    sys.stdout.reconfigure(encoding="utf-8")  # tildes correctas en cualquier terminal de Windows
    try:
        productos = persistencia.cargar_productos()
    except ErrorInventario as error:
        print(f"Error al cargar los datos: {error}")
        return
    inventario = Inventario(productos)

    while True:
        mostrar_menu()
        opcion = pedir_opcion()
        if opcion == "1":
            opcion_listar_productos(inventario)
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida. Elegí un número del menú.")


if __name__ == "__main__":
    main()
