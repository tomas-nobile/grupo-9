import pytest

from modelos import ErrorInventario, Movimiento, Producto, movimiento_desde_dict, producto_desde_dict


def _producto(**cambios) -> Producto:
    """Arma un producto válido; los argumentos reemplazan campos puntuales."""
    datos = {"codigo": "a001", "nombre": "Yerba", "categoria": "Almacen",
             "precio": 2500.0, "stock": 12, "stock_minimo": 10}
    datos.update(cambios)
    return Producto(**datos)


def test_producto_valido_normaliza_codigo_y_categoria():
    p = _producto(codigo=" a 001 ")
    assert p.codigo == "A001"
    assert p.categoria == "almacen"
    assert p.precio == 2500.0


def test_producto_precio_cero_lanza():
    with pytest.raises(ErrorInventario):
        _producto(precio=0)


def test_producto_stock_negativo_lanza():
    with pytest.raises(ErrorInventario):
        _producto(stock=-1)


def test_producto_stock_no_entero_lanza():
    with pytest.raises(ErrorInventario):
        _producto(stock=2.5)


def test_producto_codigo_vacio_lanza():
    with pytest.raises(ErrorInventario):
        _producto(codigo="  ")


def test_producto_stock_cero_es_valido():
    assert _producto(stock=0).stock == 0


def test_a_dict_tiene_las_seis_claves():
    claves = set(_producto().a_dict().keys())
    assert claves == {"codigo", "nombre", "categoria", "precio", "stock", "stock_minimo"}


def test_producto_desde_dict_convierte_tipos():
    p = producto_desde_dict({"codigo": "B1", "nombre": "Agua", "categoria": "bebidas",
                             "precio": "1200", "stock": "3", "stock_minimo": 5})
    assert p.precio == 1200.0
    assert p.stock == 3


def test_producto_desde_dict_sin_campo_lanza():
    with pytest.raises(ErrorInventario):
        producto_desde_dict({"codigo": "B1", "nombre": "Agua"})


def test_producto_desde_dict_numero_invalido_lanza():
    with pytest.raises(ErrorInventario):
        producto_desde_dict({"codigo": "B1", "nombre": "Agua", "categoria": "bebidas",
                             "precio": "caro", "stock": 3, "stock_minimo": 5})


# --- Movimiento ---


def test_movimiento_valido_normaliza():
    m = Movimiento("2026-09-20", "a001", "Salida", 3)
    assert (m.fecha, m.codigo, m.tipo, m.cantidad) == ("2026-09-20", "A001", "salida", 3)


def test_movimiento_fecha_mal_formada_lanza():
    with pytest.raises(ErrorInventario):
        Movimiento("20/09/2026", "A001", "salida", 3)


def test_movimiento_tipo_invalido_lanza():
    with pytest.raises(ErrorInventario):
        Movimiento("2026-09-20", "A001", "venta", 3)


def test_movimiento_cantidad_cero_lanza():
    with pytest.raises(ErrorInventario):
        Movimiento("2026-09-20", "A001", "salida", 0)


def test_movimiento_desde_dict_convierte_cantidad():
    m = movimiento_desde_dict({"fecha": "2026-09-20", "codigo": "A001", "tipo": "entrada", "cantidad": "7"})
    assert m.cantidad == 7
