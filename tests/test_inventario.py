from inventario import Inventario
from modelos import Producto


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
