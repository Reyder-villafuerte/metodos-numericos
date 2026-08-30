#!/usr/bin/env python
"""Script de validación para nuevas funciones y cambios."""

import math
import sys
from utilidades.parser_funciones import analizar_funcion, funcion_numerica, X
from utilidades.exportacion import crear_excel
from utilidades.graficas import crear_grafica
from metodos.newton_raphson import newton_raphson
from metodos.secante import secante
import sympy as sp

def validar_parser():
    """Validar que el parser reconoce arctan y arcsin."""
    print("[*] Probando parser con arctan y arcsin...")
    
    try:
        # Prueba arctan
        expr1 = analizar_funcion("arctan(x)")
        f1 = funcion_numerica(expr1)
        val1 = f1(0.5)
        assert abs(val1 - math.atan(0.5)) < 1e-10, f"arctan fallo: {val1} != {math.atan(0.5)}"
        print("  [OK] arctan funciona")
        
        # Prueba arcsin
        expr2 = analizar_funcion("arcsin(x)")
        f2 = funcion_numerica(expr2)
        val2 = f2(0.5)
        assert abs(val2 - math.asin(0.5)) < 1e-10, f"arcsin fallo: {val2} != {math.asin(0.5)}"
        print("  [OK] arcsin funciona")
        
        # Prueba combined
        expr3 = analizar_funcion("1-x^2-arctan(x)")
        f3 = funcion_numerica(expr3)
        val3 = f3(0.5)
        print(f"  [OK] Expresión compleja funciona: 1-x^2-arctan(x) en x=0.5 => {val3}")
        
        # Prueba e^(-2*x)
        expr4 = analizar_funcion("exp(-2*x)")
        f4 = funcion_numerica(expr4)
        val4 = f4(1)
        assert abs(val4 - math.exp(-2)) < 1e-10, f"exp(-2*x) fallo"
        print("  [OK] exp(-2*x) funciona")
        
        return True
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        return False

def validar_exportacion():
    """Validar que la exportación a Excel funciona."""
    print("[*] Probando exportación a Excel...")
    
    try:
        iteraciones = [
            {"i": 1, "xi": 0.5, "f(xi)": 0.1065, "f'(xi)": -1.378, "xi+1": 0.577, "Ea (%)": 99.99},
            {"i": 2, "xi": 0.577, "f(xi)": -0.00267, "f'(xi)": -1.321, "xi+1": 0.5671, "Ea (%)": 1.687},
        ]
        
        archivo = crear_excel(
            "Software de Métodos Numéricos",
            "exp(-x)-x",
            "Newton-Raphson",
            "{'x0': 0.5}",
            0.01,
            0.567143,
            1.687,
            iteraciones
        )
        
        assert isinstance(archivo, bytes), "No se devolvió bytes"
        assert len(archivo) > 100, "Archivo demasiado pequeño"
        print(f"  [OK] Excel generado exitosamente ({len(archivo)} bytes)")
        
        # Guardar para inspección manual
        with open("test_resultado.xlsx", "wb") as f:
            f.write(archivo)
        print("  [OK] Archivo guardado como test_resultado.xlsx")
        
        return True
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        import traceback
        traceback.print_exc()
        return False

def validar_grafica():
    """Validar que la gráfica se crea sin errores."""
    print("[*] Probando gráfica...")
    
    try:
        expr = analizar_funcion("exp(-x)-x")
        fig = crear_grafica(expr, 0.567143, [-2, 3], [0, 1])
        assert fig is not None, "Gráfica es None"
        print("  [OK] Gráfica creada exitosamente")
        return True
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        return False

def validar_ejercicios():
    """Validar ejercicios específicos del enunciado."""
    print("[*] Probando ejercicios del enunciado...")
    
    try:
        # Newton-Raphson: 1-x^2-arctan(x), x0=0.2, Ea<1%
        f_expr = analizar_funcion("1-x^2-arctan(x)")
        f = funcion_numerica(f_expr)
        f_prime = sp.diff(f_expr, X)
        f_prime_num = funcion_numerica(f_prime)
        resultado = newton_raphson(f, f_prime_num, 0.2, 1.0, 100)
        print(f"  [OK] Newton-Raphson (1-x^2-arctan(x)): raiz={resultado.raiz:.6f}, convergió={resultado.convergio}")
        
        # Secante: arcsin(x)-exp(-2*x), x0=0.1, x1=0.5, Ea<1%
        f_expr2 = analizar_funcion("arcsin(x)-exp(-2*x)")
        f2 = funcion_numerica(f_expr2)
        resultado2 = secante(f2, 0.1, 0.5, 1.0, 100)
        print(f"  [OK] Secante (arcsin(x)-exp(-2*x)): raiz={resultado2.raiz:.6f}, convergió={resultado2.convergio}")
        
        return True
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultados = []
    
    resultados.append(("Parser (arctan, arcsin)", validar_parser()))
    resultados.append(("Exportacion Excel", validar_exportacion()))
    resultados.append(("Grafica", validar_grafica()))
    resultados.append(("Ejercicios enunciado", validar_ejercicios()))
    
    print("\n" + "="*50)
    print("RESUMEN DE VALIDACION")
    print("="*50)
    
    for nombre, resultado in resultados:
        estado = "[PASS]" if resultado else "[FAIL]"
        print(f"{estado}: {nombre}")
    
    todos_ok = all(r for _, r in resultados)
    sys.exit(0 if todos_ok else 1)
