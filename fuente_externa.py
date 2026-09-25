"""Fuente de datos externa: cotización del dólar oficial desde DolarApi (https://dolarapi.com).

Es el único módulo que usa la red. Si la API no responde, devuelve la última cotización
guardada en datos/cotizacion.json (la caché), así la app sigue funcionando sin internet.
"""
import datetime

import requests

import persistencia
from modelos import ErrorInventario

URL_COTIZACION = "https://dolarapi.com/v1/dolares/oficial"
TIMEOUT_SEGUNDOS = 5
ORIGEN_API = "api"
ORIGEN_CACHE = "cache"


def interpretar_cotizacion(datos: dict) -> dict:
    """Valida la respuesta de la API y la reduce a lo que usa la app: venta, fecha y origen.

    Ejemplo de respuesta: {"compra": 1495, "venta": 1545, "fechaActualizacion": "2026-09-25T18:00:00.000Z", ...}
    """
    if not isinstance(datos, dict) or "venta" not in datos or "fechaActualizacion" not in datos:
        raise ErrorInventario("La API devolvió una cotización inválida: faltan datos.")
    venta = datos["venta"]
    if type(venta) not in (int, float) or venta <= 0:
        raise ErrorInventario("La API devolvió una cotización inválida: el valor de venta no es un número positivo.")
    try:
        fecha = datetime.date.fromisoformat(str(datos["fechaActualizacion"])[:10]).isoformat()
    except ValueError:
        raise ErrorInventario("La API devolvió una cotización inválida: la fecha no se entiende.")
    return {"venta": float(venta), "fecha": fecha, "origen": ORIGEN_API}


def obtener_cotizacion(ruta_cache: str = persistencia.RUTA_COTIZACION) -> dict:
    """Pide la cotización a la API y la guarda como caché. Si falla, devuelve la caché."""
    try:
        respuesta = requests.get(URL_COTIZACION, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()                      # un error HTTP (404, 500...) lanza excepción
        cotizacion = interpretar_cotizacion(respuesta.json())
    except (requests.RequestException, ValueError, ErrorInventario):
        # Sin internet, API caída, respuesta que no es JSON o datos inválidos: se usa la caché.
        return _cotizacion_guardada(ruta_cache)
    persistencia.guardar_cotizacion(cotizacion, ruta_cache)
    return cotizacion


def _cotizacion_guardada(ruta_cache: str) -> dict:
    """Devuelve la última cotización guardada, marcada como origen 'cache'."""
    try:
        cotizacion = persistencia.cargar_cotizacion(ruta_cache)
    except ErrorInventario:
        raise ErrorInventario("No se pudo obtener la cotización y no hay una guardada.")
    cotizacion["origen"] = ORIGEN_CACHE
    return cotizacion
