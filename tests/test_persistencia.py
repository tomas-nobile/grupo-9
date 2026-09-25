import pytest

import persistencia
from modelos import ErrorInventario, Producto


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
