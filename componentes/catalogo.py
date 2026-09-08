METODOS = {
    "Bisección": {
        "icono": "÷", "tipo": "Intervalo cerrado", "nivel": "Robusto",
        "descripcion": "Reduce repetidamente un intervalo con cambio de signo hasta aislar una raíz.",
        "formula": r"x_m = \frac{a+b}{2}",
        "ventaja": "Convergencia garantizada si la función es continua y cambia de signo.",
        "limitacion": "Converge más lentamente que los métodos abiertos.",
        "ejemplo": "exp(-x)-x", "parametros": {"intervalo_a": 0.0, "intervalo_b": 1.0},
    },
    "Regla falsa": {
        "icono": "↗", "tipo": "Intervalo cerrado", "nivel": "Robusto",
        "descripcion": "Interpola linealmente los extremos de un intervalo con cambio de signo.",
        "formula": r"x_r=b-\frac{f(b)(b-a)}{f(b)-f(a)}",
        "ventaja": "Suele mejorar la velocidad de bisección manteniendo un intervalo seguro.",
        "limitacion": "Un extremo puede permanecer fijo durante muchas iteraciones.",
        "ejemplo": "x*sin(x)-1", "parametros": {"intervalo_a": 2.0, "intervalo_b": 3.0},
    },
    "Punto fijo": {
        "icono": "↻", "tipo": "Método abierto", "nivel": "Didáctico",
        "descripcion": "Reescribe f(x)=0 como x=g(x) y genera una sucesión de aproximaciones.",
        "formula": r"x_{n+1}=g(x_n)",
        "ventaja": "Procedimiento sencillo y muy útil para estudiar convergencia.",
        "limitacion": "Depende fuertemente del despeje y de que |g'(x)| sea menor que uno.",
        "ejemplo": "x^3+2*x^2+10*x-20",
        "parametros": {"punto_fijo_x0": 1.5, "despeje_input": "20/(x^2+2*x+10)"},
    },
    "Newton-Raphson": {
        "icono": "N", "tipo": "Método abierto", "nivel": "Rápido",
        "descripcion": "Usa la recta tangente para producir aproximaciones sucesivas de la raíz.",
        "formula": r"x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}",
        "ventaja": "Convergencia muy rápida cerca de una raíz simple.",
        "limitacion": "Puede fallar si la derivada es nula o el valor inicial es inadecuado.",
        "ejemplo": "cos(x)-x", "parametros": {"newton_x0": 0.5},
    },
    "Secante": {
        "icono": "S", "tipo": "Método abierto", "nivel": "Rápido",
        "descripcion": "Aproxima la derivada mediante dos puntos y evita calcularla simbólicamente.",
        "formula": r"x_{n+1}=x_n-\frac{f(x_n)(x_n-x_{n-1})}{f(x_n)-f(x_{n-1})}",
        "ventaja": "Buena velocidad sin requerir derivada.",
        "limitacion": "No garantiza convergencia y necesita dos valores iniciales adecuados.",
        "ejemplo": "exp(-x)-x", "parametros": {"secante_x0": 0.0, "secante_x1": 1.0},
    },
    "Müller": {
        "icono": "M", "tipo": "Interpolación cuadrática", "nivel": "Avanzado",
        "descripcion": "Construye una parábola con tres puntos y permite obtener raíces reales o complejas.",
        "formula": r"x_3=x_2-\frac{2c}{b\pm\sqrt{b^2-4ac}}",
        "ventaja": "Puede localizar raíces complejas sin derivadas.",
        "limitacion": "Requiere tres puntos distintos y puede ser sensible a denominadores pequeños.",
        "ejemplo": "x^3-13*x-12",
        "parametros": {"muller_x0": 4.5, "muller_x1": 5.5, "muller_x2": 5.0},
    },
}


def cargar_ejemplo_en_estado(estado, metodo):
    ejemplo = METODOS[metodo]
    estado["funcion_input"] = ejemplo["ejemplo"]
    for clave, valor in ejemplo["parametros"].items():
        estado[clave] = valor
