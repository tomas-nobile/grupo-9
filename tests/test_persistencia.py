import pytest

import persistencia
from modelos import ErrorInventario, Movimiento, Producto


def _productos() -> list[Producto]:
    return [
        Producto("A001", "Yerba", "almacen", 2500.0, 6, 10),
        Producto("B002", "Agua mineral", "bebidas", 1200.0, 0, 15),
    ]


def test_cargar_productos_ruta_inexistente_lanza(tmp_path):
    with pytest.raises(ErrorInventario):
        persistencia.cargar_productos(str(tmp_path / "no_existe.json"))


def test_cargar_productos_json_roto_lanza(tmp_path):
    ruta = tmp_path / "roto.json"
    ruta.write_text("[{esto no es json", encoding="utf-8")
    with pytest.raises(ErrorInventario):
        persistencia.cargar_productos(str(ruta))


def test_guardar_y_cargar_productos_devuelve_lo_mismo(tmp_path):
    ruta = str(tmp_path / "sub" / "productos.json")
    persistencia.guardar_productos(_productos(), ruta)
    cargados = persistencia.cargar_productos(ruta)
    assert [p.a_dict() for p in cargados] == [p.a_dict() for p in _productos()]


def test_cargar_movimientos_ruta_inexistente_devuelve_vacio(tmp_path):
    assert persistencia.cargar_movimientos(str(tmp_path / "no_existe.csv")) == []


def test_agregar_dos_movimientos_y_cargar(tmp_path):
    ruta = str(tmp_path / "movimientos.csv")
    persistencia.agregar_movimiento(Movimiento("2026-09-20", "A001", "salida", 3), ruta)
    persistencia.agregar_movimiento(Movimiento("2026-09-21", "A001", "entrada", 10), ruta)
    cargados = persistencia.cargar_movimientos(ruta)
    assert len(cargados) == 2
    assert cargados[1].cantidad == 10
    assert type(cargados[0].cantidad) is int
