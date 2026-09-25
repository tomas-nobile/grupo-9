import matplotlib

matplotlib.use("Agg")  # sin ventanas: los gráficos solo se guardan a archivo

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
