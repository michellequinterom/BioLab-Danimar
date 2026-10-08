# Configuración común de las pruebas.
# Cada prueba usa una base de datos NUEVA y temporal, así nunca se
# toca biolab.db ni se mezclan datos entre una prueba y otra.
import os
import sys
import tempfile

import pytest

# Raíz del proyecto en el path y base temporal ANTES de importar la app
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.environ["BIOLAB_DB"] = os.path.join(tempfile.mkdtemp(), "inicial.db")
# Credenciales SOLO para las pruebas (la app no trae contraseñas en el código)
CLAVE_PRUEBA = "clave-de-prueba"
os.environ["BIOLAB_USUARIO"] = "licenciada"
os.environ["BIOLAB_CLAVE"] = CLAVE_PRUEBA

import db            # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def base(tmp_path, monkeypatch):
    """Base de datos limpia (esquema + catálogo + pacientes de prueba)."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "prueba.db"))
    db._crear_base()
    return db


@pytest.fixture
def cliente(base):
    """Navegador simulado SIN sesión iniciada."""
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def sesion(cliente):
    """Navegador simulado CON la sesión de la licenciada iniciada."""
    cliente.post("/", data={"usuario": "licenciada", "clave": CLAVE_PRUEBA})
    return cliente


@pytest.fixture
def examenes_con_precio(base):
    """Crea dos exámenes con precio conocido (el catálogo no trae precios)."""
    id_grupo = base.consultar("SELECT id_grupo FROM grupo_examen LIMIT 1", uno=True)["id_grupo"]
    a = base.ejecutar("INSERT INTO examen (id_grupo, nombre, costo) VALUES (?, 'Examen A', 1000)", (id_grupo,))
    b = base.ejecutar("INSERT INTO examen (id_grupo, nombre, costo) VALUES (?, 'Examen B', 2500)", (id_grupo,))
    return [a, b]
