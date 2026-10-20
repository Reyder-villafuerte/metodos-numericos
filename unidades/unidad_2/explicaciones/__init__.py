"""Explicaciones educativas para los métodos de sistemas lineales."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..metodos import ResultadoSistemaLineal


@dataclass
class SeccionExplicacion:
    titulo: str
    texto: str
    formulas: list[str] = field(default_factory=list)
    matrices: dict[str, np.ndarray] = field(default_factory=dict)


def latex_numero(valor: float, decimales: int = 6) -> str:
    if abs(valor) < 10 ** (-(decimales + 1)):
        valor = 0.0
    return f"{valor:.{decimales}g}"


def latex_matriz(matriz: Any, decimales: int = 6) -> str:
    datos = np.asarray(matriz, dtype=float)
    if datos.ndim == 1:
        datos = datos.reshape(-1, 1)
    filas = [" & ".join(latex_numero(float(v), decimales) for v in fila) for fila in datos]
    return r"\begin{bmatrix}" + r" \\ ".join(filas) + r"\end{bmatrix}"


def _secciones_comunes(resultado: ResultadoSistemaLineal, decimales: int) -> list[SeccionExplicacion]:
    return [
        SeccionExplicacion(
            "1. Planteamiento matricial",
            "El sistema se escribe como $Ax=b$, donde A contiene los coeficientes, x las incógnitas y b los términos independientes.",
            [f"A={latex_matriz(resultado.A, decimales)}", f"b={latex_matriz(resultado.b, decimales)}"],
        ),
        SeccionExplicacion(
            "2. Determinante e invertibilidad",
            "El determinante se calcula mediante eliminación con pivoteo parcial, un procedimiento de orden cúbico. No se usa expansión factorial por cofactores.",
            [rf"\det(A)={latex_numero(resultado.determinante, decimales)}"],
        ),
    ]


def _explicacion_inversa(resultado: ResultadoSistemaLineal, decimales: int) -> list[SeccionExplicacion]:
    secciones = _secciones_comunes(resultado, decimales)
    relacion = "PA=LU" if resultado.hubo_pivoteo else "A=LU"
    secciones.append(
        SeccionExplicacion(
            "3. Factorización reutilizable",
            "Para no sustituir el procedimiento por una llamada a una inversa de biblioteca, se obtiene una factorización LU con pivoteo parcial. La misma factorización se reutiliza para todas las columnas.",
            [relacion],
            {"P": resultado.P, "L": resultado.L, "U": resultado.U},
        )
    )
    for columna in resultado.columnas_inversa:
        j = columna["columna"]
        formulas = [
            rf"e_{{{j}}}={latex_matriz(columna['e'], decimales)}",
            rf"P e_{{{j}}}={latex_matriz(columna['Pb'], decimales)}",
        ]
        formulas.extend(
            rf"y_{{{p['indice']}}}=\frac{{{latex_numero(p['termino'], decimales)}-{latex_numero(p['suma'], decimales)}}}{{{latex_numero(p['pivote'], decimales)}}}={latex_numero(p['valor'], decimales)}"
            for p in columna["pasos_y"]
        )
        formulas.extend(
            rf"z_{{{p['indice']}}}=\frac{{{latex_numero(p['termino'], decimales)}-{latex_numero(p['suma'], decimales)}}}{{{latex_numero(p['pivote'], decimales)}}}={latex_numero(p['valor'], decimales)}"
            for p in columna["pasos_z"]
        )
        secciones.append(
            SeccionExplicacion(
                f"4.{j}. Columna {j} de la inversa",
                f"Se resuelve $Az_{j}=e_{j}$ mediante $Ly=Pe_{j}$ y $Uz_{j}=y$.",
                formulas,
            )
        )
    secciones.extend(
        [
            SeccionExplicacion(
                "5. Construcción numérica de la inversa",
                "Las soluciones de los sistemas con vectores canónicos se reúnen como columnas de $A^{-1}$.",
                [
                    rf"z_{{{columna['columna']}}}={latex_matriz(columna['z'], decimales)}"
                    for columna in resultado.columnas_inversa
                ],
                {"A⁻¹": resultado.inversa},
            ),
            SeccionExplicacion(
                "6. Multiplicación por b",
                "Con la inversa ya construida se aplica la fórmula del método.",
                [
                    "x=A^{-1}b",
                    f"x={latex_matriz(resultado.inversa, decimales)}{latex_matriz(resultado.b, decimales)}={latex_matriz(resultado.x, decimales)}",
                ],
            ),
        ]
    )
    return secciones


def _explicacion_cramer(resultado: ResultadoSistemaLineal, decimales: int) -> list[SeccionExplicacion]:
    secciones = _secciones_comunes(resultado, decimales)
    secciones.append(
        SeccionExplicacion(
            "3. Sustitución de columnas",
            "Para cada incógnita se sustituye la columna correspondiente de A por b y se calcula el nuevo determinante.",
            [r"x_i=\frac{\det(A_i)}{\det(A)}"],
        )
    )
    for i, (Ai, det_ai, xi) in enumerate(
        zip(resultado.matrices_cramer, resultado.determinantes_cramer, resultado.x), start=1
    ):
        secciones.append(
            SeccionExplicacion(
                f"4.{i}. Cálculo de x{i}",
                f"En $A_{i}$ se reemplaza la columna {i} por el vector b.",
                [
                    f"A_{{{i}}}={latex_matriz(Ai, decimales)}",
                    rf"\det(A_{{{i}}})={latex_numero(det_ai, decimales)}",
                    rf"x_{{{i}}}=\frac{{{latex_numero(det_ai, decimales)}}}{{{latex_numero(resultado.determinante, decimales)}}}={latex_numero(float(xi), decimales)}",
                ],
            )
        )
    return secciones


def _explicacion_lu(resultado: ResultadoSistemaLineal, decimales: int) -> list[SeccionExplicacion]:
    secciones = _secciones_comunes(resultado, decimales)
    diagonal = "L" if resultado.metodo == "Doolittle" else "U"
    relacion = "PA=LU" if resultado.hubo_pivoteo else "A=LU"
    secciones.append(
        SeccionExplicacion(
            "3. Construcción de L y U",
            f"En {resultado.metodo}, la diagonal de {diagonal} es igual a 1. En cada etapa se selecciona el pivote de mayor magnitud disponible y cualquier intercambio queda registrado en P.",
            [relacion],
            {"P": resultado.P, "L": resultado.L, "U": resultado.U},
        )
    )
    for paso in resultado.pasos:
        formulas = []
        if paso.get("intercambio"):
            f1, f2 = paso["intercambio"]
            formulas.append(rf"F_{{{f1}}}\leftrightarrow F_{{{f2}}}")
        if resultado.metodo == "Doolittle":
            formulas.extend(
                rf"l_{{{i}{j}}}=\frac{{{latex_numero(numerador, decimales)}}}{{{latex_numero(pivote, decimales)}}}={latex_numero(valor, decimales)}"
                for i, j, numerador, pivote, valor in paso.get("calculos_L", [])
            )
            formulas.extend(
                rf"F_{{{op['fila']}}}\leftarrow F_{{{op['fila']}}}-{latex_numero(op['multiplicador'], decimales)}F_{{{op['fila_pivote']}}}"
                for op in paso.get("operaciones_fila", [])
            )
        else:
            formulas.extend(
                rf"l_{{{i}{j}}}={latex_numero(elemento, decimales)}-{latex_numero(suma, decimales)}={latex_numero(valor, decimales)}"
                for i, j, elemento, suma, valor in paso.get("calculos_L", [])
            )
            formulas.extend(
                rf"u_{{{i}{j}}}=\frac{{{latex_numero(elemento, decimales)}-{latex_numero(suma, decimales)}}}{{{latex_numero(pivote, decimales)}}}={latex_numero(valor, decimales)}"
                for i, j, elemento, suma, pivote, valor in paso.get("calculos_U", [])
            )
        secciones.append(
            SeccionExplicacion(
                f"3.{paso['etapa']}. Etapa {paso['etapa']}",
                f"Se usa como pivote el elemento de la fila {paso['fila_pivote']}, con valor {latex_numero(paso['pivote'], decimales)}.",
                formulas,
            )
        )
    secciones.extend(
        [
            SeccionExplicacion(
                "4. Sustitución progresiva",
                "Se resuelve $Ly=Pb$ desde la primera ecuación hasta la última.",
                [
                    rf"y_{{{p['indice']}}}=\frac{{{latex_numero(p['termino'], decimales)}-{latex_numero(p['suma'], decimales)}}}{{{latex_numero(p['pivote'], decimales)}}}={latex_numero(p['valor'], decimales)}"
                    for p in resultado.pasos_progresiva
                ],
            ),
            SeccionExplicacion(
                "5. Sustitución regresiva",
                "Se resuelve $Ux=y$ desde la última ecuación hasta la primera.",
                [
                    rf"x_{{{p['indice']}}}=\frac{{{latex_numero(p['termino'], decimales)}-{latex_numero(p['suma'], decimales)}}}{{{latex_numero(p['pivote'], decimales)}}}={latex_numero(p['valor'], decimales)}"
                    for p in resultado.pasos_regresiva
                ],
            ),
        ]
    )
    return secciones


def generar_explicacion(
    resultado: ResultadoSistemaLineal, decimales: int = 6
) -> list[SeccionExplicacion]:
    if resultado.metodo == "Matriz inversa":
        secciones = _explicacion_inversa(resultado, decimales)
    elif resultado.metodo == "Regla de Cramer":
        secciones = _explicacion_cramer(resultado, decimales)
    else:
        secciones = _explicacion_lu(resultado, decimales)
    secciones.extend(
        [
            SeccionExplicacion(
                "Resultado",
                "El vector solución reúne los valores de todas las incógnitas.",
                [f"x={latex_matriz(resultado.x, decimales)}"],
            ),
            SeccionExplicacion(
                "Verificación",
                "Se calcula nuevamente $Ax$ y se compara con b. El residuo debe ser cercano a cero.",
                [
                    f"Ax={latex_matriz(resultado.comprobacion, decimales)}",
                    f"Ax-b={latex_matriz(resultado.residuo, decimales)}",
                    rf"\lVert Ax-b\rVert_\infty={latex_numero(resultado.norma_residuo, decimales)}",
                ],
            ),
        ]
    )
    return secciones


__all__ = ["SeccionExplicacion", "generar_explicacion", "latex_matriz", "latex_numero"]
