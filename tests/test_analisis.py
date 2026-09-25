import matplotlib

matplotlib.use("Agg")  # sin ventanas: los gráficos solo se guardan a archivo

import pandas as pd

import analisis
from inventario import Inventario
from modelos import Movimiento, Producto


def _inventario() -> Inventario:
    productos = [
        Producto("A001", "Yerba", "almacen", 100.0, 10, 5),
        Producto("A002", "Azúcar", "almacen", 50.0, 4, 5),
        Producto("B001", "Agua", "bebidas", 20.0, 0, 10),
    ]
    movimientos = [
        Movimiento("2026-08-10", "B001", "salida", 99),   # más de 30 días antes del último: no cuenta
        Movimiento("2026-08-27", "A001", "salida", 10),
        Movimiento("2026-09-10", "A001", "salida", 20),
        Movimiento("2026-09-15", "A002", "entrada", 30),
        Movimiento("2026-09-20", "B001", "salida", 6),
        Movimiento("2026-09-25", "A002", "salida", 3),
    ]
    return Inventario(productos, movimientos)


# --- Indicador 1: valor del inventario ---

def test_valor_total_inventario():
    # 100*10 + 50*4 + 20*0
    assert analisis.valor_total_inventario(_inventario()) == 1200.0


def test_valor_por_categoria_ordenado():
    resumen = analisis.analizar_valor_inventario(_inventario())
    assert list(resumen["categoria"]) == ["almacen", "bebidas"]
    assert list(resumen["valor"]) == [1200.0, 0.0]
    assert list(resumen["productos"]) == [2, 1]


# --- Indicador 2: cobertura ---

def test_salidas_recientes_cuenta_desde_el_ultimo_movimiento():
    salidas = analisis.salidas_recientes(_inventario(), dias=30)
    # 2026-08-10 queda afuera; 2026-08-27 entra (29 días antes del 2026-09-25)
    assert sorted(salidas["cantidad"]) == [3, 6, 10, 20]


def test_cobertura_calcula_consumo_y_dias():
    tabla = analisis.analizar_cobertura(_inventario(), dias=30).set_index("codigo")
    assert tabla.loc["A001", "consumo_diario"] == 1.0          # 30 unidades / 30 días
    assert tabla.loc["A001", "dias_cobertura"] == 10.0         # 10 de stock / 1 por día
    assert tabla.loc["B001", "dias_cobertura"] == 0.0          # sin stock


def test_cobertura_sin_salidas_queda_vacia_y_al_final():
    inventario = _inventario()
    inventario.productos.append(Producto("Z001", "Nuevo", "varios", 10.0, 5, 1))
    tabla = analisis.analizar_cobertura(inventario, dias=30)
    ultima = tabla.iloc[-1]
    assert ultima["codigo"] == "Z001"
    assert ultima["consumo_diario"] == 0
    assert pd.isna(ultima["dias_cobertura"])


def test_cobertura_sin_movimientos_no_rompe():
    inventario = Inventario([Producto("A001", "Yerba", "almacen", 100.0, 10, 5)])
    tabla = analisis.analizar_cobertura(inventario)
    assert len(tabla) == 1
