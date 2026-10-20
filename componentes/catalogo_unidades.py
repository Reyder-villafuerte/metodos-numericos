from typing import Any, Dict, List


UNIDADES = {
    'unidad_1': {
        'id': 'unidad_1',
        'nombre': 'Unidad 1',
        'titulo': 'Unidad 1 — Raíces de ecuaciones',
        'descripcion': 'Métodos de raíces de ecuaciones (6 métodos existentes)',
    },
    'unidad_2': {
        'id': 'unidad_2',
        'nombre': 'Unidad 2',
        'titulo': 'Unidad 2 — Sistemas de ecuaciones lineales',
        'descripcion': 'Métodos iterativos, sistemas no lineales, interpolación y regresión.',
    },
}


METODOS_POR_UNIDAD: Dict[str, List[str]] = {
    'unidad_1': [
        'Bisección',
        'Regla falsa',
        'Punto fijo',
        'Newton-Raphson',
        'Secante',
        'Müller',
    ],
    'unidad_2': [
        'Matriz inversa',
        'Regla de Cramer',
        'Doolittle',
        'Crout',
        'Jacobi',
        'Gauss-Seidel',
        'Jacobi no lineal',
        'Gauss-Seidel no lineal',
        'Newton-Raphson para sistemas',
        'Interpolación de Newton',
        'Regresión polinomial',
        'Regresión lineal múltiple',
    ],
}


UNIDAD_POR_METODO: Dict[str, str] = {}
for unidad, metodos in METODOS_POR_UNIDAD.items():
    for metodo in metodos:
        UNIDAD_POR_METODO[metodo] = unidad


def obtener_metodos_por_unidad(unidad_id: str) -> List[str]:
    return list(METODOS_POR_UNIDAD.get(unidad_id, []))


def obtener_unidad_de_metodo(metodo: str) -> str | None:
    return UNIDAD_POR_METODO.get(metodo)


def registrar_metodo(unidad_id: str, metodo_id: str, metodo_nombre: str = None) -> None:
    if unidad_id not in METODOS_POR_UNIDAD:
        METODOS_POR_UNIDAD[unidad_id] = []
    if metodo_id not in METODOS_POR_UNIDAD[unidad_id]:
        METODOS_POR_UNIDAD[unidad_id].append(metodo_id)
    UNIDAD_POR_METODO[metodo_id] = unidad_id
