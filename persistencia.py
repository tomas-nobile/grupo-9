"""Lectura y escritura de archivos: productos en JSON y movimientos en CSV.

Es el único módulo que abre archivos. Los errores de archivo se convierten en
ErrorInventario con un mensaje en español, así main.py los maneja igual que el resto.
"""
import json
import os

from modelos import ErrorInventario, Producto, producto_desde_dict

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATOS = os.path.join(CARPETA_BASE, "datos")
RUTA_PRODUCTOS = os.path.join(CARPETA_DATOS, "productos.json")


def _crear_carpeta_de(ruta: str) -> None:
    """Crea la carpeta que va a contener el archivo, si no existe."""
    carpeta = os.path.dirname(ruta)
    if carpeta != "":
        os.makedirs(carpeta, exist_ok=True)


def cargar_productos(ruta: str = RUTA_PRODUCTOS) -> list[Producto]:
    """Lee el JSON de productos y devuelve la lista de objetos Producto."""
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        raise ErrorInventario(f"No se encontró el archivo de productos: {ruta}")
    except json.JSONDecodeError:
        raise ErrorInventario(f"El archivo {ruta} no es un JSON válido.")
    if not isinstance(datos, list):
        raise ErrorInventario(f"El archivo {ruta} tiene que contener una lista de productos.")
    productos = []
    for item in datos:
        productos.append(producto_desde_dict(item))
    return productos


def guardar_productos(productos: list[Producto], ruta: str = RUTA_PRODUCTOS) -> None:
    """Escribe la lista de productos en el JSON, reemplazando el contenido anterior."""
    datos = []
    for producto in productos:
        datos.append(producto.a_dict())
    try:
        _crear_carpeta_de(ruta)
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
    except OSError:
        raise ErrorInventario(f"No se pudo guardar el archivo {ruta}.")
