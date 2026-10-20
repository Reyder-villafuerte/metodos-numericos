"""Reorganización de los métodos numéricos por unidades.

La Unidad 1 reúne los seis métodos de raíces de ecuaciones. La Unidad 2 aún no
tiene implementaciones; solo se conserva su marcador.
"""

from .unidad_1 import *  # noqa: F401,F403
from .unidad_1.metodos import *  # noqa: F401,F403
from .unidad_1.explicaciones import generar_explicacion, GENERADORES
from .unidad_2 import TITULO_UNIDAD_2, MENSAJE_UNIDAD_2

from componentes.catalogo_unidades import (
    UNIDADES,
    METODOS_POR_UNIDAD,
    UNIDAD_POR_METODO,
    obtener_metodos_por_unidad,
    obtener_unidad_de_metodo,
    registrar_metodo,
)

__all__ = [
    "UNIDADES",
    "METODOS_POR_UNIDAD",
    "UNIDAD_POR_METODO",
    "obtener_metodos_por_unidad",
    "obtener_unidad_de_metodo",
    "registrar_metodo",
    "generar_explicacion",
    "GENERADORES",
    "TITULO_UNIDAD_2",
    "MENSAJE_UNIDAD_2",
]
