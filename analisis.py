"""Indicadores con pandas y gráficos con matplotlib.

Las funciones reciben el Inventario, arman los DataFrame adentro y devuelven resultados.
Así main.py y la notebook usan exactamente el mismo cálculo.
"""
import pandas as pd

from inventario import Inventario

COLUMNAS_PRODUCTOS = ["codigo", "nombre", "categoria", "precio", "stock", "stock_minimo"]
COLUMNAS_MOVIMIENTOS = ["fecha", "codigo", "tipo", "cantidad"]


# ---------- De objetos a DataFrame ----------

def productos_a_dataframe(inventario: Inventario) -> pd.DataFrame:
    """Una fila por producto, con las mismas columnas que el JSON."""
    filas = [producto.a_dict() for producto in inventario.productos]
    return pd.DataFrame(filas, columns=COLUMNAS_PRODUCTOS)


def movimientos_a_dataframe(inventario: Inventario) -> pd.DataFrame:
    """Una fila por movimiento, con la fecha convertida a tipo fecha de pandas."""
    filas = [movimiento.a_dict() for movimiento in inventario.movimientos]
    tabla = pd.DataFrame(filas, columns=COLUMNAS_MOVIMIENTOS)
    tabla["fecha"] = pd.to_datetime(tabla["fecha"])
    return tabla


def tabla_como_texto(tabla: pd.DataFrame) -> str:
    """Convierte un DataFrame en texto alineado para imprimir en consola."""
    if tabla.empty:
        return "(sin datos)"
    return tabla.to_string(index=False, float_format="{:,.2f}".format, na_rep="sin ventas")


# ---------- Indicador 1: valor del inventario ----------

def valor_total_inventario(inventario: Inventario) -> float:
    """Plata inmovilizada en stock: suma de precio por stock de todos los productos."""
    productos = productos_a_dataframe(inventario)
    return float((productos["precio"] * productos["stock"]).sum())


def analizar_valor_inventario(inventario: Inventario) -> pd.DataFrame:
    """Valor del stock por categoría, de mayor a menor."""
    productos = productos_a_dataframe(inventario)
    productos["valor"] = productos["precio"] * productos["stock"]
    resumen = productos.groupby("categoria").agg(
        productos=("codigo", "count"),
        unidades=("stock", "sum"),
        valor=("valor", "sum"),
    )
    return resumen.reset_index().sort_values("valor", ascending=False)
