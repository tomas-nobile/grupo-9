import pytest
import requests

import fuente_externa
import persistencia
from modelos import ErrorInventario

RESPUESTA_EJEMPLO = {"moneda": "USD", "casa": "oficial", "nombre": "Oficial", "compra": 1495,
                     "venta": 1545, "fechaActualizacion": "2026-09-25T18:00:00.000Z"}


class RespuestaFalsa:
    """Imita la respuesta de requests.get para no llamar a la API real en los tests."""

    def __init__(self, datos: dict) -> None:
        self.datos = datos

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self.datos


def _get_que_responde(url: str, timeout: int) -> RespuestaFalsa:
    return RespuestaFalsa(RESPUESTA_EJEMPLO)


def _get_sin_internet(url: str, timeout: int) -> RespuestaFalsa:
    raise requests.ConnectionError("sin internet")


# --- interpretar_cotizacion (sin red) ---

def test_interpretar_respuesta_valida():
    assert fuente_externa.interpretar_cotizacion(RESPUESTA_EJEMPLO) == {
        "venta": 1545.0, "fecha": "2026-09-25", "origen": "api"}


def test_interpretar_sin_venta_lanza():
    with pytest.raises(ErrorInventario):
        fuente_externa.interpretar_cotizacion({"fechaActualizacion": "2026-09-25"})


def test_interpretar_venta_cero_lanza():
    with pytest.raises(ErrorInventario):
        fuente_externa.interpretar_cotizacion({"venta": 0, "fechaActualizacion": "2026-09-25"})


def test_interpretar_venta_texto_lanza():
    with pytest.raises(ErrorInventario):
        fuente_externa.interpretar_cotizacion({"venta": "mil", "fechaActualizacion": "2026-09-25"})


# --- obtener_cotizacion (con la red simulada) ---

def test_obtener_con_api_guarda_la_cache(tmp_path, monkeypatch):
    ruta = str(tmp_path / "cotizacion.json")
    monkeypatch.setattr(fuente_externa.requests, "get", _get_que_responde)
    cotizacion = fuente_externa.obtener_cotizacion(ruta)
    assert cotizacion["origen"] == "api"
    assert persistencia.cargar_cotizacion(ruta)["venta"] == 1545.0


def test_obtener_sin_internet_usa_la_cache(tmp_path, monkeypatch):
    ruta = str(tmp_path / "cotizacion.json")
    persistencia.guardar_cotizacion({"venta": 1500.0, "fecha": "2026-09-20", "origen": "api"}, ruta)
    monkeypatch.setattr(fuente_externa.requests, "get", _get_sin_internet)
    cotizacion = fuente_externa.obtener_cotizacion(ruta)
    assert cotizacion == {"venta": 1500.0, "fecha": "2026-09-20", "origen": "cache"}


def test_obtener_sin_internet_ni_cache_lanza(tmp_path, monkeypatch):
    monkeypatch.setattr(fuente_externa.requests, "get", _get_sin_internet)
    with pytest.raises(ErrorInventario):
        fuente_externa.obtener_cotizacion(str(tmp_path / "no_existe.json"))
