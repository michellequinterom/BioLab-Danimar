# HU-02: Generar el presupuesto de los exámenes (orden + pago)


def crear_orden(sesion, base, examenes, paciente=1):
    sesion.post("/ordenes/nueva", data={"id_paciente": str(paciente),
                                        "examenes": [str(e) for e in examenes]})
    return base.consultar("SELECT * FROM v_orden_totales ORDER BY id_orden DESC LIMIT 1", uno=True)


def pagar(sesion, id_orden, **datos):
    sesion.post(f"/ordenes/{id_orden}/pago", data=datos)


def test_total_es_la_suma_de_los_examenes(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    assert orden["total"] == 3500
    assert orden["saldo"] == 3500
    assert orden["estado_pago"] == "pendiente"


def test_examen_repetido_cuenta_una_vez(sesion, base, examenes_con_precio):
    a = examenes_con_precio[0]
    orden = crear_orden(sesion, base, [a, a])
    assert orden["total"] == 1000


def test_orden_sin_examenes_no_se_crea(sesion, base):
    sesion.post("/ordenes/nueva", data={"id_paciente": "1"})
    assert base.consultar("SELECT COUNT(*) AS n FROM orden", uno=True)["n"] == 0


def test_orden_sin_paciente_no_se_crea(sesion, base, examenes_con_precio):
    sesion.post("/ordenes/nueva", data={"id_paciente": "", "examenes": [str(examenes_con_precio[0])]})
    assert base.consultar("SELECT COUNT(*) AS n FROM orden", uno=True)["n"] == 0


def test_precio_queda_fijo_en_la_orden(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    base.ejecutar("UPDATE examen SET costo = 9999")          # cambio de precio posterior
    despues = base.consultar("SELECT total FROM v_orden_totales WHERE id_orden = ?",
                             (orden["id_orden"],), uno=True)
    assert despues["total"] == 3500


def test_abono_parcial(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    pagar(sesion, orden["id_orden"], tipo="abono", monto="1.000,50")
    o = base.consultar("SELECT * FROM v_orden_totales WHERE id_orden = ?", (orden["id_orden"],), uno=True)
    assert o["estado_pago"] == "parcial"
    assert o["monto_abonado"] == 1000.5
    assert o["saldo"] == 2499.5


def test_abono_mayor_al_saldo_se_rechaza(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    pagar(sesion, orden["id_orden"], tipo="abono", monto="5000")
    o = base.consultar("SELECT * FROM v_orden_totales WHERE id_orden = ?", (orden["id_orden"],), uno=True)
    assert o["monto_abonado"] == 0
    assert o["estado_pago"] == "pendiente"


def test_abonos_que_completan_el_total(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    pagar(sesion, orden["id_orden"], tipo="abono", monto="1500")
    pagar(sesion, orden["id_orden"], tipo="abono", monto="2000")
    o = base.consultar("SELECT * FROM v_orden_totales WHERE id_orden = ?", (orden["id_orden"],), uno=True)
    assert o["estado_pago"] == "pago"
    assert o["saldo"] == 0


def test_pago_completo(sesion, base, examenes_con_precio):
    orden = crear_orden(sesion, base, examenes_con_precio)
    pagar(sesion, orden["id_orden"], tipo="completo")
    o = base.consultar("SELECT * FROM v_orden_totales WHERE id_orden = ?", (orden["id_orden"],), uno=True)
    assert o["estado_pago"] == "pago"
    assert o["saldo"] == 0
