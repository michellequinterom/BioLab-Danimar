from conftest import CLAVE_PRUEBA
# Inicio de sesión


def test_sin_sesion_redirige_al_login(cliente):
    r = cliente.get("/pacientes")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/")


def test_clave_incorrecta(cliente):
    r = cliente.post("/", data={"usuario": "licenciada", "clave": "otra"})
    assert "incorrectos" in r.get_data(as_text=True)


def test_clave_correcta_entra(cliente):
    r = cliente.post("/", data={"usuario": "licenciada", "clave": CLAVE_PRUEBA})
    assert r.status_code == 302
    assert "/pacientes" in r.headers["Location"]


def test_cerrar_sesion(sesion):
    sesion.get("/salir")
    assert sesion.get("/pacientes").status_code == 302
