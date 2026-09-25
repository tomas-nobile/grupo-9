"""Indicadores con pandas y gráficos con matplotlib.

Las funciones reciben el Inventario, arman los DataFrame adentro y devuelven resultados.
Así main.py y la notebook usan exactamente el mismo cálculo.
"""
import pandas as pd

from inventario import Inventario
from modelos import TIPO_SALIDA

DIAS_ANALISIS = 30

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


# ---------- Salidas del período (base de los indicadores 2 y 3) ----------

def salidas_recientes(inventario: Inventario, dias: int = DIAS_ANALISIS) -> pd.DataFrame:
    """Salidas de los últimos `dias` días, contando hacia atrás desde el último movimiento registrado.

    Se toma el último movimiento como referencia (y no la fecha de hoy) para que el análisis
    siempre use datos: si la app no se usa por una semana, los indicadores no quedan vacíos.
    """
    movimientos = movimientos_a_dataframe(inventario)
    salidas = movimientos[movimientos["tipo"] == TIPO_SALIDA]
    if salidas.empty:
        return salidas
    fecha_referencia = movimientos["fecha"].max()
    desde = fecha_referencia - pd.Timedelta(days=dias)
    return salidas[salidas["fecha"] > desde]


def _vendido_por_producto(inventario: Inventario, dias: int) -> pd.DataFrame:
    """Productos con la suma de unidades que salieron en el período (0 si no salió nada)."""
    salidas = salidas_recientes(inventario, dias)
    vendido = salidas.groupby("codigo")["cantidad"].sum().reset_index(name="vendido")
    productos = productos_a_dataframe(inventario)
    tabla = productos.merge(vendido, on="codigo", how="left")
    tabla["vendido"] = tabla["vendido"].fillna(0).astype(int)
    return tabla


# ---------- Indicador 2: consumo diario y días de cobertura ----------

def analizar_cobertura(inventario: Inventario, dias: int = DIAS_ANALISIS) -> pd.DataFrame:
    """Cuántos días dura el stock de cada producto al ritmo de consumo del período.

    Sin salidas en el período, la cobertura queda vacía (NaN): no se puede estimar.
    """
    tabla = _vendido_por_producto(inventario, dias)
    tabla["consumo_diario"] = tabla["vendido"] / dias
    cobertura = tabla["stock"] / tabla["consumo_diario"]
    tabla["dias_cobertura"] = cobertura.where(tabla["consumo_diario"] > 0)
    tabla = tabla.sort_values("dias_cobertura", na_position="last")
    return tabla[["codigo", "nombre", "stock", "consumo_diario", "dias_cobertura"]]
