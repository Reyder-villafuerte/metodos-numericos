# Software de Métodos Numéricos

Aplicación universitaria interactiva para aproximar raíces de funciones reales usando cinco métodos numéricos clásicos: Bisección, Regla falsa, Punto fijo, Newton-Raphson y Secante. Incluye visualización interactiva, tablas detalladas y exportación a Excel.

## Características Principales

✓ **Parser seguro basado en SymPy** sin uso de `eval()`
✓ **Funciones matemáticas completas**: sin/cos/tan, asin/acos/atan, exp, log, sqrt, abs
✓ **Normalización automática**: sen→sin, ln→log, arctan→atan, e^x→exp(x), 2x→2*x
✓ **Validaciones robustas**: dominio, divisiones por cero, derivadas nulas, convergencia
✓ **Criterios de parada flexibles**: error permitido o número fijo de iteraciones
✓ **Gráficas interactivas** estilo GNU Octave con manejo de discontinuidades
✓ **Tablas educativas** con encabezados comprensibles y explicaciones integradas
✓ **Carga de imágenes** con vista previa (OCR opcional si está disponible)
✓ **Exportación a Excel** con tres hojas: Resumen, Iteraciones, Descripción
✓ **Punto fijo mejorado** con sugerencias de despejes y validación de convergencia

## Métodos Implementados

### 1. Bisección
- Intervalo [a, b] con cambio de signo obligatorio
- Aproximación mediante punto medio
- Tabla: Iteración | Extremo izquierdo | Extremo derecho | Aproximación | f(a) | f(m) | f(b) | Error (%)

### 2. Regla Falsa
- Intervalo [a, b] con cambio de signo obligatorio  
- Aproximación mediante intersección de recta
- Tabla similar a Bisección

### 3. Punto Fijo
- Requiere despeje x = g(x) equivalente a f(x) = 0
- Validación de criterio |g'(x0)| < 1 para convergencia local
- Sugerencias automáticas de despejes para expresiones comunes
- Tabla: Iteración | Valor actual | g(xi) | Error (%)

### 4. Newton-Raphson
- Requiere valor inicial x0
- Calcula automáticamente derivada f'(x)
- Muy rápido cuando es convergente
- Tabla: Iteración | Valor actual | f(xi) | f'(xi) | Nueva aproximación | Error (%)

### 5. Secante
- Requiere dos valores iniciales x0 y x1
- No necesita derivada explícita
- Tabla: Iteración | Valor anterior | Valor actual | f(anterior) | f(actual) | Nueva aproximación | Error (%)

## Formato de Entrada

### Funciones Admitidas
```
Operadores: +, -, *, /, ^ (potencia)
Funciones:  sin, cos, tan, asin, acos, atan
            exp, log (logaritmo natural), sqrt, abs
Nombres naturales: sen, ln, arcsin, arccos, arctan, arcsen
Exponenciales: e^x, e^(-x), e^(-2*x) → exp(x), exp(-x), exp(-2*x)
Multiplicación implícita: 2x → 2*x
```

### Ejemplos de Funciones Válidas
```
exp(-x)-x
x^3+2*x^2+10*x-20
x*sin(x)-1
1-x^2-arctan(x)
arcsin(x)-exp(-2*x)
sin(x)+x-1
log(x)+2*x-4
cos(x)-x
sqrt(x)-2
abs(x)-1
```

## Instalación y Ejecución en Windows

```powershell
# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Pruebas Unitarias

```powershell
python -m pytest -q
```

Todas las pruebas validan la precisión de los métodos con ejercicios documentados.

## Estructura del Proyecto

```
.
├── app.py                          # Aplicación Streamlit principal
├── requirements.txt                # Dependencias
├── README.md                       # Este archivo
├── metodos/
│   ├── __init__.py                # Clases y funciones compartidas
│   ├── biseccion.py               # Método de bisección
│   ├── regla_falsa.py             # Método de regla falsa
│   ├── punto_fijo.py              # Método de punto fijo
│   ├── newton_raphson.py          # Método de Newton-Raphson
│   └── secante.py                 # Método de secante
├── utilidades/
│   ├── parser_funciones.py        # Parser matemático seguro (SymPy)
│   ├── graficas.py                # Generación de gráficas Plotly
│   ├── exportacion.py             # Exportación a Excel
│   ├── lector_imagen.py           # OCR con pytesseract (opcional)
│   └── punto_fijo_ayuda.py        # Sugerencias y validación para punto fijo
└── tests/
    └── test_metodos.py            # Pruebas unitarias
```

## Características Técnicas

### Precisión
- Cálculos internos con precisión completa
- Redondeo solo en presentación
- Manejo de valores extremos, NaN e infinito

### Validaciones
- Función no vacía ni inválida
- Parámetros consistentes (a < b, error > 0, iteraciones > 0)
- Cambio de signo en intervalos (bisección, regla falsa)
- Derivada no nula (Newton-Raphson, secante)
- Dominio válido (arcsin, log, sqrt)

### Gráficas
- Hasta 1000 puntos por gráfica
- Filtrado automático de discontinuidades
- Escala Y automática basada en percentiles
- Ejes cartesianos visibles
- Marcadores para raíz y valores iniciales
- Interactividad completa: zoom, desplazamiento, descarga PNG

## Ejercicios de Validación

Todos estos ejercicios se resuelven correctamente:

### Newton-Raphson
```
f(x) = 1-x^2-arctan(x), x0=0.2, Ea < 1%
→ Raíz ≈ 0.650566
```

### Secante
```
f(x) = arcsin(x)-exp(-2*x), x0=0.1, x1=0.5, Ea < 1%
→ Raíz ≈ 0.419118
```

### Punto Fijo
```
f(x) = sin(x)+x-1, g(x)=1-sin(x), x0=0.52, Ea < 1%
→ Raíz ≈ 0.510...
```

### Bisección
```
f(x) = exp(-x)-x, a=0, b=1
→ Raíz ≈ 0.567143
```

### Regla Falsa
```
f(x) = x*sin(x)-1, a=2, b=3
→ Raíz ≈ 2.7726
```

## Limitaciones y Notas

- **OCR**: Si pytesseract no está instalado, el lector de imágenes muestra un aviso pero la app sigue funcionando
- **Dominio**: El usuario es responsable de proporcionar valores iniciales en el dominio de la función
- **Convergencia**: No se garantiza convergencia; depende de la función y parámetros iniciales
- **Newton-Raphson**: Requiere que la derivada sea calculable y no nula
- **Punto Fijo**: Requiere despeje manual; no automatiza completamente la búsqueda de g(x)

## Cambios Recientes

### v1.1 (Actual)
- ✓ Parser: Agregadas funciones arctan, arcsin, acos
- ✓ Normalización mejorada: e^(-2*x) → exp(-2*x)
- ✓ Exportación Excel: Completamente refactorizada, ahora funciona con todas las estructuras
- ✓ Gráficas: Manejo mejorado de discontinuidades y escala Y automática
- ✓ Interfaz: Selector de criterio de parada (error o iteraciones)
- ✓ Tablas: Encabezados claros con explicaciones desplegables
- ✓ Punto Fijo: Sugerencias de despejes y validación mejorada
- ✓ Todas las pruebas pasando

## Autor y Licencia

Proyecto educativo. Libre para uso académico y modificación.

## Soporte

Para issues o sugerencias, revise la estructura del código y las validaciones incluidas en cada módulo.

