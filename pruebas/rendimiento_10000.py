# ============================================================
# BioLab - Danimar | Prueba de rendimiento del RNF-01
# ------------------------------------------------------------
# RNF-01: la ficha de un paciente debe cargar en máximo 2 s
# con 10.000 pacientes registrados.
#
# La prueba crea una base TEMPORAL (nunca toca biolab.db) con
# 10.000 pacientes ficticios y sus órdenes, y mide cuánto tarda
# el servidor en responder cada pantalla.
#
# Uso:  python pruebas/rendimiento_10000.py
# ============================================================
import os
import random
import statistics
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.environ["BIOLAB_DB"] = os.path.join(tempfile.mkdtemp(), "rendimiento.db")
os.environ["BIOLAB_USUARIO"] = "licenciada"
os.environ["BIOLAB_CLAVE"] = "clave-de-prueba"

import db            # noqa: E402
from app import app  # noqa: E402

N_PACIENTES = 10_000
LIMITE_S = 2.0
REPETICIONES = 5
random.seed(2026)

NOMBRES = ["Ana", "Luis", "María", "José", "Carmen", "Pedro", "Rosa", "Juan", "Elena", "Carlos"]
APELLIDOS = ["Pérez", "Gómez", "Rodríguez", "Díaz", "Mora", "Rojas", "Vargas", "Suárez", "Ortiz", "Ruiz"]


def poblar():
    con = db.conectar()
    con.execute("UPDATE examen SET costo = 500 + (id_examen % 10) * 150")  # precios ficticios
    examenes = [r[0] for r in con.execute("SELECT id_examen FROM examen")]
    pacientes = [(str(20_000_000 + i),
                  f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)} {i}",
                  random.randint(1, 90)) for i in range(N_PACIENTES)]
    con.executemany("INSERT INTO paciente (cedula, nombre_completo, edad) VALUES (?, ?, ?)", pacientes)
    ids = [r[0] for r in con.execute("SELECT id_paciente FROM paciente")]
    n_ordenes = 0
    for idp in ids:
        for _ in range(random.randint(1, 3)):
            cur = con.execute("INSERT INTO orden (id_paciente) VALUES (?)", (idp,))
            n_ordenes += 1
            for ide in random.sample(examenes, random.randint(1, 3)):
                con.execute("""INSERT INTO orden_examen (id_orden, id_examen, costo)
                               SELECT ?, id_examen, costo FROM examen WHERE id_examen = ?""",
                            (cur.lastrowid, ide))
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM paciente").fetchone()[0]
    con.close()
    return total, n_ordenes


def medir(cliente, url):
    tiempos = []
    for _ in range(REPETICIONES):
        t0 = time.perf_counter()
        r = cliente.get(url)
        tiempos.append(time.perf_counter() - t0)
        assert r.status_code == 200, f"{url} respondió {r.status_code}"
    return statistics.median(tiempos), max(tiempos)


def main():
    t0 = time.perf_counter()
    total, n_ordenes = poblar()
    print(f"Base de prueba: {total} pacientes y {n_ordenes} órdenes "
          f"(creada en {time.perf_counter() - t0:.1f} s)\n")

    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/", data={"usuario": "licenciada", "clave": "clave-de-prueba"})

    cedula = "20007351"
    id_orden = db.consultar("""SELECT o.id_orden FROM orden o JOIN paciente p
                               ON p.id_paciente = o.id_paciente
                               WHERE p.cedula = ? LIMIT 1""", (cedula,), uno=True)["id_orden"]
    pruebas = [
        ("Buscar un paciente por cédula", f"/pacientes?q={cedula}"),
        ("Buscar pacientes por apellido", "/pacientes?q=Rojas"),
        ("Abrir la orden de ese paciente", f"/ordenes/{id_orden}"),
        ("Lista completa de pacientes (10.000)", "/pacientes"),
        ("Pantalla de nueva orden (10.000 en la lista)", "/ordenes/nueva"),
        ("Lista completa de órdenes", "/ordenes"),
    ]
    fallas = 0
    print(f"{'Pantalla':48} {'Mediana':>9} {'Máximo':>9}  RNF-01")
    for nombre, url in pruebas:
        med, mx = medir(c, url)
        ok = mx <= LIMITE_S
        fallas += not ok
        print(f"{nombre:48} {med:8.3f}s {mx:8.3f}s  {'CUMPLE' if ok else 'NO CUMPLE'}")
    print(f"\nLímite: {LIMITE_S} s. {REPETICIONES} repeticiones por pantalla.")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
