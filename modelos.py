"""Modelos del dominio: Producto, Movimiento y la excepción ErrorInventario.

Cada clase valida sus datos en el constructor: si un objeto existe, sus datos son válidos.
Este módulo no importa nada del proyecto.
"""


class ErrorInventario(Exception):
    """Error de negocio con un mensaje pensado para mostrarle al usuario."""


def _validar_texto(valor: str, campo: str) -> str:
    """Devuelve el texto sin espacios en los bordes, o lanza ErrorInventario si está vacío."""
    if not isinstance(valor, str) or valor.strip() == "":
        raise ErrorInventario(f"El campo '{campo}' no puede estar vacío.")
    return valor.strip()


def _validar_entero_no_negativo(valor: int, campo: str) -> int:
    """Devuelve el valor si es un entero mayor o igual a 0, o lanza ErrorInventario."""
    if type(valor) is not int or valor < 0:
        raise ErrorInventario(f"El campo '{campo}' tiene que ser un número entero mayor o igual a 0.")
    return valor


class Producto:
    """Un producto del almacén con su precio, su stock actual y su stock mínimo."""

    def __init__(self, codigo: str, nombre: str, categoria: str, precio: float,
                 stock: int, stock_minimo: int) -> None:
        self.codigo = _validar_texto(codigo, "codigo").upper().replace(" ", "")
        self.nombre = _validar_texto(nombre, "nombre")
        self.categoria = _validar_texto(categoria, "categoria").lower()
        if type(precio) not in (int, float) or precio <= 0:
            raise ErrorInventario("El campo 'precio' tiene que ser un número mayor a 0.")
        self.precio = float(precio)
        self.stock = _validar_entero_no_negativo(stock, "stock")
        self.stock_minimo = _validar_entero_no_negativo(stock_minimo, "stock_minimo")

    def a_dict(self) -> dict:
        """Devuelve el producto como diccionario, con las mismas claves que el JSON."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
        }

    def __repr__(self) -> str:
        return f"Producto({self.codigo}, {self.nombre}, stock={self.stock})"


def producto_desde_dict(datos: dict) -> Producto:
    """Crea un Producto a partir de un diccionario leído del JSON."""
    try:
        return Producto(
            codigo=str(datos["codigo"]),
            nombre=str(datos["nombre"]),
            categoria=str(datos["categoria"]),
            precio=float(datos["precio"]),
            stock=int(datos["stock"]),
            stock_minimo=int(datos["stock_minimo"]),
        )
    except KeyError as error:
        raise ErrorInventario(f"Al producto le falta el campo {error}.")
    except (ValueError, TypeError):
        raise ErrorInventario(f"El producto {datos.get('codigo', '?')} tiene un número inválido.")
