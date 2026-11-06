# Pruebas de las reglas del negocio (reglas.py).
# No necesitan Flask ni base de datos: se llama la función y se revisa
# la respuesta. Por eso son rápidas y muestran la regla con claridad.
import reglas


def test_paciente_valido():
    assert reglas.validar_paciente("1090123456", "Ana Pérez", "34") is None


def test_paciente_sin_edad_es_valido():
    assert reglas.validar_paciente("1090123456", "Ana Pérez", "") is None


def test_paciente_con_errores():
    assert "obligatorios" in reglas.validar_paciente("", "Ana", "")
    assert "números" in reglas.validar_paciente("10A9", "Ana", "")
    assert "edad" in reglas.validar_paciente("109", "Ana", "130")


def test_leer_monto_en_formato_colombiano_y_con_punto():
    assert reglas.leer_monto("1.350,50") == 1350.5
    assert reglas.leer_monto("1350.5") == 1350.5
    assert reglas.leer_monto("abc") == 0
    assert reglas.leer_monto(None) == 0


def test_validar_abono():
    assert reglas.validar_abono(500, 3500) is None
    assert reglas.validar_abono(3500, 3500) is None          # pagar justo el saldo
    assert "mayor que cero" in reglas.validar_abono(0, 3500)
    assert "saldo" in reglas.validar_abono(4000, 3500)


def test_estado_pago():
    assert reglas.estado_pago(0, 3500) == "pendiente"
    assert reglas.estado_pago(1000, 3500) == "parcial"
    assert reglas.estado_pago(3500, 3500) == "pago"
