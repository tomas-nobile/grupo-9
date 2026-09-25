"""La clase Inventario: los productos y movimientos del almacén y las operaciones sobre ellos.

Toda regla de negocio vive acá (búsquedas, altas, movimientos de stock, alertas).
No lee ni escribe archivos: eso lo hace persistencia.py.
"""
from modelos import Movimiento, Producto


def _codigo_de(producto: Producto) -> str:
    """Clave de orden: el código del producto."""
    return producto.codigo


class Inventario:
    """Colección de productos y movimientos con las operaciones del almacén."""

    def __init__(self, productos: list[Producto], movimientos: list[Movimiento] | None = None) -> None:
        self.productos = productos
        if movimientos is None:
            movimientos = []
        self.movimientos = movimientos

    def listar(self) -> list[Producto]:
        """Devuelve una copia de los productos ordenada por código."""
        return sorted(self.productos, key=_codigo_de)

    def obtener(self, codigo: str) -> Producto | None:
        """Devuelve el producto con ese código, o None si no existe."""
        codigo = codigo.strip().upper()
        for producto in self.productos:
            if producto.codigo == codigo:
                return producto
        return None
