"""La clase Inventario: los productos y movimientos del almacén y las operaciones sobre ellos.

Toda regla de negocio vive acá (búsquedas, altas, movimientos de stock, alertas).
No lee ni escribe archivos: eso lo hace persistencia.py.
"""
import datetime

from modelos import TIPO_SALIDA, ErrorInventario, Movimiento, Producto, producto_desde_dict

CAMPOS_MODIFICABLES = ("nombre", "categoria", "precio", "stock_minimo")


def _codigo_de(producto: Producto) -> str:
    """Clave de orden: el código del producto."""
    return producto.codigo


def _urgencia(producto: Producto) -> float:
    """Clave de orden de las alertas: qué fracción del mínimo queda (0 = sin stock, lo más urgente)."""
    minimo = producto.stock_minimo
    if minimo == 0:
        minimo = 1  # evita dividir por cero
    return producto.stock / minimo


class Inventario:
    """Colección de productos y movimientos con las operaciones del almacén."""

    def __init__(self, productos: list[Producto], movimientos: list[Movimiento] | None = None) -> None:
        self.productos = productos
        if movimientos is None:
            movimientos = []
        self.movimientos = movimientos

    # ---------- Consultas: no modifican nada ----------

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

    def buscar(self, texto: str) -> list[Producto]:
        """Productos cuyo código o nombre contiene el texto, sin distinguir mayúsculas."""
        texto = texto.strip().lower()
        encontrados = []
        for producto in self.listar():
            if texto in producto.codigo.lower() or texto in producto.nombre.lower():
                encontrados.append(producto)
        return encontrados

    def categorias(self) -> list[str]:
        """Lista de categorías sin repetir, ordenada alfabéticamente."""
        categorias = []
        for producto in self.productos:
            if producto.categoria not in categorias:
                categorias.append(producto.categoria)
        return sorted(categorias)

    def filtrar_por_categoria(self, categoria: str) -> list[Producto]:
        """Productos de una categoría."""
        categoria = categoria.strip().lower()
        filtrados = []
        for producto in self.listar():
            if producto.categoria == categoria:
                filtrados.append(producto)
        return filtrados

    # ---------- Alertas de reabastecimiento ----------

    def alertas(self) -> list[Producto]:
        """Productos en el mínimo o por debajo, del más urgente al menos urgente."""
        en_alerta = []
        for producto in self.productos:
            if producto.esta_en_alerta():
                en_alerta.append(producto)
        return sorted(en_alerta, key=_urgencia)

    def costo_total_reposicion(self) -> float:
        """Suma de lo que cuesta reponer todos los productos en alerta."""
        total = 0.0
        for producto in self.alertas():
            total = total + producto.costo_reposicion()
        return total

    # ---------- Cambios: validan todo antes de modificar ----------

    def obtener_o_error(self, codigo: str) -> Producto:
        """Devuelve el producto con ese código, o lanza ErrorInventario si no existe."""
        producto = self.obtener(codigo)
        if producto is None:
            raise ErrorInventario(f"No existe un producto con código {codigo.strip().upper()}.")
        return producto

    def agregar(self, producto: Producto) -> None:
        """Agrega un producto nuevo. Lanza ErrorInventario si el código ya existe."""
        if self.obtener(producto.codigo) is not None:
            raise ErrorInventario(f"Ya existe un producto con código {producto.codigo}.")
        self.productos.append(producto)

    def modificar(self, codigo: str, campo: str, valor: str | float | int) -> Producto:
        """Cambia un campo de un producto y devuelve el producto actualizado.

        Arma un Producto nuevo con el cambio para que lo valide el constructor:
        si el valor es inválido, se lanza ErrorInventario y el producto original queda igual.
        """
        if campo == "stock":
            raise ErrorInventario("El stock no se modifica a mano: registrá una entrada o una salida.")
        if campo not in CAMPOS_MODIFICABLES:
            raise ErrorInventario(f"El campo '{campo}' no se puede modificar.")
        actual = self.obtener_o_error(codigo)
        datos = actual.a_dict()
        datos[campo] = valor
        nuevo = producto_desde_dict(datos)
        posicion = self.productos.index(actual)
        self.productos[posicion] = nuevo
        return nuevo

    def eliminar(self, codigo: str) -> Producto:
        """Quita un producto del inventario y lo devuelve. Lanza ErrorInventario si no existe."""
        producto = self.obtener_o_error(codigo)
        self.productos.remove(producto)
        return producto

    # ---------- Movimientos: la única forma de cambiar el stock ----------

    def registrar_movimiento(self, codigo: str, tipo: str, cantidad: int,
                             fecha: str | None = None) -> Movimiento:
        """Registra una entrada o salida, actualiza el stock y devuelve el movimiento creado."""
        producto = self.obtener_o_error(codigo)
        if fecha is None:
            fecha = datetime.date.today().isoformat()
        movimiento = Movimiento(fecha, producto.codigo, tipo, cantidad)  # valida tipo, cantidad y fecha
        if movimiento.tipo == TIPO_SALIDA:
            if movimiento.cantidad > producto.stock:
                raise ErrorInventario(f"Stock insuficiente de {producto.nombre}: hay {producto.stock}, "
                                      f"se pidieron {movimiento.cantidad}.")
            producto.stock = producto.stock - movimiento.cantidad
        else:
            producto.stock = producto.stock + movimiento.cantidad
        self.movimientos.append(movimiento)
        return movimiento

    def movimientos_de(self, codigo: str | None = None, ultimos: int = 20) -> list[Movimiento]:
        """Últimos movimientos, de todos los productos o de uno. El más reciente queda al final."""
        seleccionados = []
        for movimiento in self.movimientos:
            if codigo is None or movimiento.codigo == codigo.strip().upper():
                seleccionados.append(movimiento)
        return seleccionados[-ultimos:]
