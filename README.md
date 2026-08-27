# Software de Métodos Numéricos

Aplicación universitaria para aproximar raíces de funciones reales mediante Bisección, Regla falsa, Punto fijo, Newton-Raphson y Secante. Presenta cada iteración, el error aproximado, una gráfica interactiva y exportación a Excel.

## Características

- Parser seguro basado en SymPy, sin `eval()`.
- Funciones naturales como `2x`, `x^3`, `sen(x)`, `ln(x)` y `e^(-x)`.
- Validaciones de dominio, signos, divisiones, derivadas y convergencia.
- Carga de imágenes con vista previa y OCR opcional, siempre editable y confirmable.
- Tablas redondeables a 4, 6, 8 o 10 decimales.

## Tecnologías y estructura

Python 3.12, Streamlit, SymPy, Pandas, Plotly, Pillow y OpenPyXL. La lógica reutilizable está en `metodos/`; el parser, gráfica, exportación y OCR en `utilidades/`; las pruebas en `tests/`.

## Instalación y ejecución en Windows

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Formato y ejemplos

Escriba una función usando `x` como variable. Se admiten potencias con `^`, multiplicación implícita, `sin`, `cos`, `tan`, `exp`, `log`, `sqrt` y `abs`, además de `sen` y `ln` como formas naturales.

Ejemplos: `exp(-x)-x`, `x^3+2*x^2+10*x-20`, `x*sin(x)-1`, `cos(x)-x`, `sqrt(x)-2` y `log(x)+x`.

## Pruebas

```powershell
python -m pytest -q
```

## Limitaciones actuales del OCR

La aplicación no inventa una función cuando la lectura es dudosa. Si `pytesseract` o el motor Tesseract no están instalados, muestra un aviso y permite introducir la expresión manualmente. El texto reconocido siempre debe confirmarse o corregirse antes de resolver.
