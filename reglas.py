# ============================================================
# BioLab - Danimar | Reglas del negocio
# ------------------------------------------------------------
# Aquí viven las decisiones del laboratorio (qué datos son válidos,
# cuándo un abono se acepta, qué estado de pago tiene una orden).
# No usa Flask ni la base de datos: recibe datos y devuelve una
# respuesta. Así cada regla se prueba sola y, si la licenciada
# cambia una regla, solo se toca este archivo (principio S de SOLID).
# ============================================================

TOLERANCIA = 0.001   # margen para comparar dinero guardado como decimal


# ---------------- HU-01: Pacientes ----------------
def validar_paciente(cedula, nombre, edad):
    """Criterios de aceptación de HU-01.
    Devuelve el mensaje del primer error, o None si los datos sirven.
    (Que la cédula no esté repetida se revisa en la ruta, porque
    necesita consultar la base de datos.)"""
    if not cedula or not nombre:
        return "La cédula y el nombre son obligatorios."
    if not cedula.isdigit():
        return "La cédula solo debe contener números."
    if edad and (not edad.isdigit() or not 0 <= int(edad) <= 120):
        return "La edad debe ser un número entre 0 y 120."
    return None


# ---------------- HU-03: Pagos (regla RN-04) ----------------
def leer_monto(texto):
    """Convierte lo que escribe la licenciada en un número.
    '1.350,50' -> 1350.5 | '1350.5' -> 1350.5 | texto inválido -> 0."""
    txt = (texto or "").strip()
    if "," in txt:                                   # formato 1.350,50
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt or 0)
    except ValueError:
        return 0.0


def validar_abono(monto, saldo):
    """Un abono debe ser mayor que cero y no superar el saldo pendiente.
    Devuelve el mensaje de error, o None si el abono se acepta."""
    if monto <= 0:
        return "Escribe un monto mayor que cero."
    if monto > saldo + TOLERANCIA:
        return "El abono no puede ser mayor que el saldo pendiente."
    return None


def estado_pago(abonado, total):
    """pendiente (nada abonado), parcial (algo abonado) o pago (todo)."""
    if abonado >= total - TOLERANCIA:
        return "pago"
    return "parcial" if abonado > 0 else "pendiente"
