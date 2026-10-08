# ============================================================
# BioLab - Danimar | Conexión a la base de datos (SQLite)
# ------------------------------------------------------------
# SQLite viene incluido en Python: no hay que instalar ningún
# servidor. La base es un solo archivo (biolab.db) que se crea
# sola la primera vez a partir de los scripts de /database.
# ============================================================
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("BIOLAB_DB", os.path.join(BASE_DIR, "biolab.db"))
SQL_DIR = os.path.join(BASE_DIR, "database")


def _crear_base():
    """Crea las tablas y carga el catálogo y los datos de prueba (solo la 1.ª vez)."""
    nueva = not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0
    con = sqlite3.connect(DB_PATH)
    try:
        with open(os.path.join(SQL_DIR, "schema.sql"), encoding="utf-8") as f:
            con.executescript(f.read())
        if nueva:
            for archivo in ("seed_catalogo.sql", "seed_pruebas.sql"):
                with open(os.path.join(SQL_DIR, archivo), encoding="utf-8") as f:
                    con.executescript(f.read())
        con.commit()
    finally:
        con.close()


_crear_base()


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row          # filas como diccionarios
    con.execute("PRAGMA foreign_keys = ON")
    return con


def consultar(sql, params=(), uno=False):
    """SELECT -> lista de diccionarios (o uno solo si uno=True)."""
    with conectar() as con:
        filas = [dict(f) for f in con.execute(sql, params).fetchall()]
    return (filas[0] if filas else None) if uno else filas


def ejecutar(sql, params=()):
    """INSERT/UPDATE/DELETE. Devuelve el id de la fila insertada."""
    con = conectar()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()
