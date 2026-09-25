"""Indicadores con pandas y gráficos con matplotlib.

Las funciones reciben el Inventario, arman los DataFrame adentro y devuelven resultados.
Así main.py y la notebook usan exactamente el mismo cálculo.
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

from inventario import Inventario
from modelos import TIPO_SALIDA

DIAS_ANALISIS = 30
CARPETA_GRAFICOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficos")
RUTA_GRAFICO_STOCK = os.path.join(CARPETA_GRAFICOS, "stock_vs_minimo.png")
RUTA_GRAFICO_SALIDAS = os.path.join(CARPETA_GRAFICOS, "salidas_por_dia.png")
COLOR_ALERTA = "#d62728"
COLOR_OK = "#2ca02c"

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


def analizar_valor_inventario(inventario: Inventario, cotizacion: float | None = None) -> pd.DataFrame:
    """Valor del stock por categoría, de mayor a menor. Con cotización, agrega el valor en dólares."""
    productos = productos_a_dataframe(inventario)
    productos["valor"] = productos["precio"] * productos["stock"]
    resumen = productos.groupby("categoria").agg(
        productos=("codigo", "count"),
        unidades=("stock", "sum"),
        valor=("valor", "sum"),
    )
    resumen = resumen.reset_index().sort_values("valor", ascending=False)
    if cotizacion is not None:
        resumen["valor_usd"] = resumen["valor"] / cotizacion
    return resumen


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


# ---------- Indicador 3: productos más vendidos ----------

def analizar_mas_vendidos(inventario: Inventario, top: int = 5, dias: int = DIAS_ANALISIS) -> pd.DataFrame:
    """Ranking de los productos con más unidades vendidas en el período."""
    tabla = _vendido_por_producto(inventario, dias)
    tabla = tabla[tabla["vendido"] > 0]
    tabla = tabla.sort_values("vendido", ascending=False).head(top)
    return tabla[["codigo", "nombre", "categoria", "vendido"]]


# ---------- Extra: productos sin ventas (stock inmovilizado) ----------

def analizar_sin_movimiento(inventario: Inventario, dias: int = DIAS_ANALISIS) -> pd.DataFrame:
    """Productos con stock que no tuvieron ninguna salida en el período."""
    tabla = _vendido_por_producto(inventario, dias)
    tabla = tabla[(tabla["vendido"] == 0) & (tabla["stock"] > 0)]
    tabla["valor"] = tabla["precio"] * tabla["stock"]
    return tabla[["codigo", "nombre", "stock", "valor"]]


# ---------- Gráficos ----------

def _guardar_grafico(figura: plt.Figure, ruta: str, mostrar: bool) -> str:
    """Guarda la figura como PNG, la muestra en pantalla si se pide, y devuelve la ruta."""
    carpeta = os.path.dirname(ruta)
    if carpeta != "":
        os.makedirs(carpeta, exist_ok=True)
    figura.tight_layout()
    figura.savefig(ruta, dpi=120)
    if mostrar:
        plt.show()
    plt.close(figura)
    return ruta


def graficar_stock_vs_minimo(inventario: Inventario, ruta: str = RUTA_GRAFICO_STOCK,
                             mostrar: bool = False) -> str:
    """Barras con el stock de cada producto (rojo si está en alerta) y una marca en su mínimo."""
    tabla = productos_a_dataframe(inventario)
    minimo = tabla["stock_minimo"].where(tabla["stock_minimo"] > 0, 1)  # evita dividir por cero
    tabla["proporcion"] = tabla["stock"] / minimo
    tabla = tabla.sort_values("proporcion", ascending=False).reset_index(drop=True)
    tabla["posicion"] = range(len(tabla))
    en_alerta = tabla[tabla["stock"] <= tabla["stock_minimo"]]
    ok = tabla[tabla["stock"] > tabla["stock_minimo"]]

    figura, eje = plt.subplots(figsize=(9, 6))
    eje.barh(ok["posicion"], ok["stock"], color=COLOR_OK, label="Stock OK")
    eje.barh(en_alerta["posicion"], en_alerta["stock"], color=COLOR_ALERTA, label="En alerta: reponer")
    eje.scatter(tabla["stock_minimo"], tabla["posicion"], marker="|", s=250, linewidths=3,
                color="black", label="Stock mínimo", zorder=3)
    eje.set_yticks(tabla["posicion"])
    eje.set_yticklabels(tabla["nombre"])
    eje.set_title("Stock actual vs. stock mínimo")
    eje.set_xlabel("Unidades")
    eje.set_ylabel("Producto")
    eje.legend(loc="upper right")
    return _guardar_grafico(figura, ruta, mostrar)


def ventas_por_dia(inventario: Inventario, dias: int = DIAS_ANALISIS) -> pd.DataFrame:
    """Unidades que salieron cada día del período. Los días sin ventas aparecen con 0."""
    salidas = salidas_recientes(inventario, dias)
    if salidas.empty:
        return pd.DataFrame({"fecha": [], "unidades": []})
    por_dia = salidas.groupby("fecha")["cantidad"].sum()
    todos_los_dias = pd.date_range(end=por_dia.index.max(), periods=dias, freq="D")
    por_dia = por_dia.reindex(todos_los_dias, fill_value=0)
    return pd.DataFrame({"fecha": por_dia.index, "unidades": por_dia.values})


def graficar_salidas_por_dia(inventario: Inventario, dias: int = DIAS_ANALISIS,
                             ruta: str = RUTA_GRAFICO_SALIDAS, mostrar: bool = False) -> str:
    """Línea con las unidades vendidas por día y su promedio."""
    tabla = ventas_por_dia(inventario, dias)
    figura, eje = plt.subplots(figsize=(9, 4.5))
    eje.plot(tabla["fecha"], tabla["unidades"], marker="o", color="#1f77b4", label="Unidades vendidas")
    if not tabla.empty:
        promedio = tabla["unidades"].mean()
        eje.axhline(promedio, linestyle="--", color="gray", label=f"Promedio: {promedio:.1f} por día")
    eje.set_title(f"Unidades vendidas por día (últimos {dias} días)")
    eje.set_xlabel("Fecha")
    eje.set_ylabel("Unidades")
    eje.legend(loc="upper right")
    figura.autofmt_xdate()
    return _guardar_grafico(figura, ruta, mostrar)
