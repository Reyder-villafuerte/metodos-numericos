def extraer_funcion(imagen):
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None, "El reconocimiento automático está pendiente: instale Tesseract y pytesseract para activarlo."
    try:
        if not hasattr(imagen, "mode"):
            imagen = Image.open(imagen)
        texto = pytesseract.image_to_string(imagen, lang="spa+eng").strip()
    except Exception:
        return None, "No fue posible leer la imagen. Escriba la función manualmente."
    return (texto, "Texto detectado; confirme o corrija la función antes de resolver.") if texto else (None, "No se detectó una función confiable en la imagen.")
