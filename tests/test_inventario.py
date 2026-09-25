import datetime

import pytest

from inventario import Inventario
from modelos import ErrorInventario, Producto


def _inventario() -> Inventario:
    return Inventario([
        Producto("B002", "Agua mineral", "bebidas", 1200.0, 0, 15),
        Producto("A001", "Yerba mate", "almacen", 2500.0, 6, 10),
        Producto("A002", "Azúcar", "almacen", 1400.0, 25, 10),
    ])


def test_listar_ordena_por_codigo():
    codigos = [p.codigo for p in _inventario().listar()]
    assert codigos == ["A001", "A002", "B002"]


def test_obtener_existente_sin_importar_mayusculas():
    assert _inventario().obtener(" a001 ").nombre == "Yerba mate"


def test_obtener_inexistente_devuelve_none():
    assert _inventario().obtener("Z999") is None


def test_buscar_parcial_e_insensible_a_mayusculas():
    encontrados = _inventario().buscar("YER")
    assert [p.codigo for p in encontrados] == ["A001"]


def test_buscar_por_codigo():
    assert len(_inventario().buscar("a0")) == 2


def test_buscar_sin_coincidencias_devuelve_vacio():
    assert _inventario().buscar("fernet") == []


def test_buscar_texto_vacio_devuelve_todos():
    assert len(_inventario().buscar("")) == 3


def test_categorias_sin_repetidos_y_ordenadas():
    assert _inventario().categorias() == ["almacen", "bebidas"]


def test_filtrar_por_categoria():
    assert [p.codigo for p in _inventario().filtrar_por_categoria("Almacen")] == ["A001", "A002"]


def test_filtrar_categoria_inexistente_devuelve_vacio():
    assert _inventario().filtrar_por_categoria("ferreteria") == []


def test_agregar_valido_aumenta_la_lista():
    inventario = _inventario()
    inventario.agregar(Producto("C001", "Café", "almacen", 5000.0, 3, 2))
    assert len(inventario.listar()) == 4


def test_agregar_codigo_repetido_lanza_y_no_agrega():
    inventario = _inventario()
    with pytest.raises(ErrorInventario):
        inventario.agregar(Producto("a001", "Otra yerba", "almacen", 1.0, 1, 1))
    assert len(inventario.listar()) == 3


def test_obtener_o_error_inexistente_lanza():
    with pytest.raises(ErrorInventario):
        _inventario().obtener_o_error("Z999")


def test_modificar_precio_valido():
    inventario = _inventario()
    actualizado = inventario.modificar("A001", "precio", 2700.0)
    assert actualizado.precio == 2700.0
    assert inventario.obtener("A001").precio == 2700.0


def test_modificar_precio_invalido_lanza_y_no_cambia():
    inventario = _inventario()
    with pytest.raises(ErrorInventario):
        inventario.modificar("A001", "precio", -10)
    assert inventario.obtener("A001").precio == 2500.0


def test_modificar_codigo_inexistente_lanza():
    with pytest.raises(ErrorInventario):
        _inventario().modificar("Z999", "precio", 100.0)


def test_modificar_stock_lanza():
    with pytest.raises(ErrorInventario):
        _inventario().modificar("A001", "stock", 100)


def test_eliminar_existente():
    inventario = _inventario()
    eliminado = inventario.eliminar("b002")
    assert eliminado.codigo == "B002"
    assert len(inventario.listar()) == 2
    assert inventario.obtener("B002") is None


def test_eliminar_inexistente_lanza():
    with pytest.raises(ErrorInventario):
        _inventario().eliminar("Z999")


# --- Movimientos ---

def test_entrada_suma_stock_y_registra_movimiento():
    inventario = _inventario()
    movimiento = inventario.registrar_movimiento("A001", "entrada", 10, fecha="2026-09-25")
    assert inventario.obtener("A001").stock == 16
    assert inventario.movimientos == [movimiento]
    assert movimiento.fecha == "2026-09-25"


def test_entrada_cantidad_cero_lanza_y_no_cambia():
    inventario = _inventario()
    with pytest.raises(ErrorInventario):
        inventario.registrar_movimiento("A001", "entrada", 0)
    assert inventario.obtener("A001").stock == 6
    assert inventario.movimientos == []


def test_movimiento_codigo_inexistente_lanza():
    with pytest.raises(ErrorInventario):
        _inventario().registrar_movimiento("Z999", "entrada", 5)


def test_movimiento_sin_fecha_usa_hoy():
    movimiento = _inventario().registrar_movimiento("A001", "entrada", 1)
    assert movimiento.fecha == datetime.date.today().isoformat()
