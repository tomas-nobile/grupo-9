"""Modelos del dominio: Producto, Movimiento y la excepción ErrorInventario.

Cada clase valida sus datos en el constructor: si un objeto existe, sus datos son válidos.
Este módulo no importa nada del proyecto.
"""
import datetime

TIPO_ENTRADA = "entrada"
TIPO_SALIDA = "salida"
TIPOS_MOVIMIENTO = (TIPO_ENTRADA, TIPO_SALIDA)

# Al reponer se apunta a tener el doble del stock mínimo.
FACTOR_STOCK_OBJETIVO = 2


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

    def esta_en_alerta(self) -> bool:
        """True si el stock llegó al mínimo o está por debajo."""
        return self.stock <= self.stock_minimo

    def cantidad_sugerida(self) -> int:
        """Unidades a pedir para llegar al stock objetivo (el doble del mínimo). Nunca negativo."""
        faltante = self.stock_minimo * FACTOR_STOCK_OBJETIVO - self.stock
        return max(faltante, 0)

    def costo_reposicion(self) -> float:
        """Cuánto cuesta comprar la cantidad sugerida, a precio actual."""
        return self.cantidad_sugerida() * self.precio

    def valor_stock(self) -> float:
        """Plata inmovilizada en este producto: stock por precio."""
        return self.stock * self.precio

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


class Movimiento:
    """Una entrada o salida de stock de un producto en una fecha."""

    def __init__(self, fecha: str, codigo: str, tipo: str, cantidad: int) -> None:
        try:
            self.fecha = datetime.date.fromisoformat(str(fecha).strip()).isoformat()
        except ValueError:
            raise ErrorInventario(f"La fecha '{fecha}' no es válida. Usá el formato AAAA-MM-DD.")
        self.codigo = _validar_texto(codigo, "codigo").upper().replace(" ", "")
        tipo = _validar_texto(tipo, "tipo").lower()
        if tipo not in TIPOS_MOVIMIENTO:
            raise ErrorInventario(f"El tipo '{tipo}' no es válido: tiene que ser entrada o salida.")
        self.tipo = tipo
        if type(cantidad) is not int or cantidad <= 0:
            raise ErrorInventario("La cantidad tiene que ser un número entero mayor a 0.")
        self.cantidad = cantidad

    def a_dict(self) -> dict:
        """Devuelve el movimiento como diccionario, con las mismas columnas que el CSV."""
        return {"fecha": self.fecha, "codigo": self.codigo, "tipo": self.tipo, "cantidad": self.cantidad}

    def __repr__(self) -> str:
        return f"Movimiento({self.fecha}, {self.codigo}, {self.tipo}, {self.cantidad})"


def movimiento_desde_dict(datos: dict) -> Movimiento:
    """Crea un Movimiento a partir de una fila leída del CSV."""
    try:
        return Movimiento(
            fecha=datos["fecha"],
            codigo=datos["codigo"],
            tipo=datos["tipo"],
            cantidad=int(datos["cantidad"]),
        )
    except KeyError as error:
        raise ErrorInventario(f"Al movimiento le falta la columna {error}.")
    except (ValueError, TypeError):
        raise ErrorInventario(f"El movimiento del {datos.get('fecha', '?')} tiene una cantidad inválida.")
