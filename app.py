# ============================================================
# BioLab - Danimar | Aplicación web local (Flask)
# Sprint 1:
#   HU-01  Registrar un paciente
#   HU-02  Generar el presupuesto de los exámenes (orden + pago)
# ============================================================
import os
import secrets
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db

app = Flask(__name__)
# Ninguna clave va escrita en el código (Definition of Done).
# - BIOLAB_SECRET: clave para firmar las sesiones. Si no existe, se genera
#   una aleatoria cada vez que arranca la aplicación.
# - BIOLAB_CLAVE: contraseña de la licenciada. Si no existe, se genera una
#   contraseña temporal y se muestra en la consola al iniciar.
app.secret_key = os.environ.get("BIOLAB_SECRET") or secrets.token_hex(32)

USUARIO = os.environ.get("BIOLAB_USUARIO", "licenciada")
_clave = os.environ.get("BIOLAB_CLAVE")
CLAVE_TEMPORAL = None
if not _clave:
    _clave = CLAVE_TEMPORAL = secrets.token_urlsafe(8)
# La contraseña solo se guarda cifrada (hash) en memoria.
CLAVE_HASH = generate_password_hash(_clave)
del _clave


@app.template_filter("dinero")
def dinero(valor):
    """1350 -> '1.350,00'"""
    try:
        v = float(valor or 0)
    except (TypeError, ValueError):
        v = 0
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def login_requerido(f):
    @wraps(f)
    def envoltura(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return envoltura


# ---------------- Inicio de sesión ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("usuario"):
        return redirect(url_for("pacientes"))
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")
        if usuario == USUARIO and check_password_hash(CLAVE_HASH, clave):
            session["usuario"] = usuario
            return redirect(url_for("pacientes"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))


# ---------------- HU-01: Pacientes ----------------
@app.route("/pacientes")
@login_requerido
def pacientes():
    q = request.args.get("q", "").strip()
    if q:
        lista = db.consultar(
            """SELECT * FROM paciente
               WHERE cedula LIKE ? OR nombre_completo LIKE ?
               ORDER BY nombre_completo""", (f"%{q}%", f"%{q}%"))
    else:
        lista = db.consultar("SELECT * FROM paciente ORDER BY id_paciente DESC")
    return render_template("pacientes.html", pacientes=lista, q=q)


@app.route("/pacientes/nuevo", methods=["POST"])
@login_requerido
def paciente_nuevo():
    cedula = request.form.get("cedula", "").strip()
    nombre = " ".join(request.form.get("nombre_completo", "").split())
    edad = request.form.get("edad", "").strip()

    # Validaciones (criterios de aceptación de HU-01)
    if not cedula or not nombre:
        flash("La cédula y el nombre son obligatorios.", "error")
        return redirect(url_for("pacientes"))
    if not cedula.isdigit():
        flash("La cédula solo debe contener números.", "error")
        return redirect(url_for("pacientes"))
    if edad and (not edad.isdigit() or not 0 <= int(edad) <= 120):
        flash("La edad debe ser un número entre 0 y 120.", "error")
        return redirect(url_for("pacientes"))
    if db.consultar("SELECT 1 FROM paciente WHERE cedula = ?", (cedula,), uno=True):
        flash(f"Ya existe un paciente con la cédula {cedula}.", "error")
        return redirect(url_for("pacientes"))

    db.ejecutar("INSERT INTO paciente (cedula, nombre_completo, edad) VALUES (?, ?, ?)",
                (cedula, nombre, int(edad) if edad else None))
    flash(f"Paciente {nombre} registrado correctamente.", "ok")
    return redirect(url_for("pacientes"))


# ---------------- HU-02: Orden / presupuesto ----------------
@app.route("/ordenes")
@login_requerido
def ordenes():
    lista = db.consultar(
        """SELECT t.*, p.cedula, p.nombre_completo
           FROM v_orden_totales t JOIN paciente p ON p.id_paciente = t.id_paciente
           ORDER BY t.id_orden DESC""")
    return render_template("ordenes.html", ordenes=lista)


@app.route("/ordenes/nueva", methods=["GET", "POST"])
@login_requerido
def orden_nueva():
    if request.method == "POST":
        id_paciente = request.form.get("id_paciente", "")
        examenes = [e for e in request.form.getlist("examenes") if e.isdigit()]
        if not db.consultar("SELECT 1 FROM paciente WHERE id_paciente = ?", (id_paciente,), uno=True):
            flash("Selecciona un paciente.", "error")
            return redirect(url_for("orden_nueva"))
        if not examenes:
            flash("Selecciona al menos un examen.", "error")
            return redirect(url_for("orden_nueva", paciente=id_paciente))

        id_orden = db.ejecutar("INSERT INTO orden (id_paciente) VALUES (?)", (id_paciente,))
        for id_examen in dict.fromkeys(examenes):            # sin repetidos
            db.ejecutar(
                """INSERT INTO orden_examen (id_orden, id_examen, costo)
                   SELECT ?, id_examen, costo FROM examen WHERE id_examen = ?""",
                (id_orden, id_examen))
        flash("Presupuesto generado.", "ok")
        return redirect(url_for("orden_detalle", id_orden=id_orden))

    lista_pac = db.consultar("SELECT id_paciente, cedula, nombre_completo FROM paciente ORDER BY nombre_completo")
    grupos = db.consultar("SELECT * FROM grupo_examen ORDER BY nombre")
    examenes = db.consultar("SELECT * FROM examen ORDER BY nombre")
    for g in grupos:
        g["examenes"] = [e for e in examenes if e["id_grupo"] == g["id_grupo"]]
    return render_template("orden_nueva.html", pacientes=lista_pac, grupos=grupos,
                           elegido=request.args.get("paciente", ""))


@app.route("/ordenes/<int:id_orden>")
@login_requerido
def orden_detalle(id_orden):
    orden = db.consultar(
        """SELECT t.*, p.cedula, p.nombre_completo, p.edad
           FROM v_orden_totales t JOIN paciente p ON p.id_paciente = t.id_paciente
           WHERE t.id_orden = ?""", (id_orden,), uno=True)
    if not orden:
        flash("La orden no existe.", "error")
        return redirect(url_for("ordenes"))
    detalle = db.consultar(
        """SELECT e.nombre, g.nombre AS grupo, oe.costo
           FROM orden_examen oe
           JOIN examen e ON e.id_examen = oe.id_examen
           JOIN grupo_examen g ON g.id_grupo = e.id_grupo
           WHERE oe.id_orden = ? ORDER BY g.nombre, e.nombre""", (id_orden,))
    return render_template("orden.html", orden=orden, detalle=detalle)


@app.route("/ordenes/<int:id_orden>/pago", methods=["POST"])
@login_requerido
def orden_pago(id_orden):
    orden = db.consultar("SELECT * FROM v_orden_totales WHERE id_orden = ?", (id_orden,), uno=True)
    if not orden:
        return redirect(url_for("ordenes"))
    tipo = request.form.get("tipo")
    total = float(orden["total"])

    if tipo == "completo":
        abonado = total
    elif tipo == "abono":
        try:
            txt = request.form.get("monto", "").strip()
            if "," in txt:                      # formato 1.350,50
                txt = txt.replace(".", "").replace(",", ".")
            monto = float(txt or 0)
        except ValueError:
            monto = 0
        if monto <= 0:
            flash("Escribe un monto mayor que cero.", "error")
            return redirect(url_for("orden_detalle", id_orden=id_orden))
        if monto > float(orden["saldo"]) + 0.001:
            flash("El abono no puede ser mayor que el saldo pendiente.", "error")
            return redirect(url_for("orden_detalle", id_orden=id_orden))
        abonado = float(orden["monto_abonado"]) + monto
    else:
        return redirect(url_for("orden_detalle", id_orden=id_orden))

    estado = "pago" if abonado >= total - 0.001 else ("parcial" if abonado > 0 else "pendiente")
    db.ejecutar("UPDATE orden SET monto_abonado = ?, estado_pago = ? WHERE id_orden = ?",
                (min(abonado, total), estado, id_orden))
    flash("Pago registrado.", "ok")
    return redirect(url_for("orden_detalle", id_orden=id_orden))


if __name__ == "__main__":
    print("BioLab - Danimar en http://127.0.0.1:8000  (Ctrl+C para salir)")
    if CLAVE_TEMPORAL:
        print(f"Usuario: {USUARIO} | Contraseña temporal: {CLAVE_TEMPORAL}")
        print("Para fijar una contraseña propia, define la variable BIOLAB_CLAVE.")
    app.run(host="127.0.0.1", port=8000, debug=False)
