# HU-01: Registrar un paciente


def registrar(sesion, **datos):
    sesion.post("/pacientes/nuevo", data=datos)
    return sesion.get("/pacientes").get_data(as_text=True)


def contar(base, cedula):
    return base.consultar("SELECT COUNT(*) AS n FROM paciente WHERE cedula = ?", (cedula,), uno=True)["n"]


def test_registra_paciente_valido(sesion, base):
    html = registrar(sesion, cedula="20000001", nombre_completo="Ana Prueba", edad="30")
    assert "registrado correctamente" in html
    assert contar(base, "20000001") == 1


def test_cedula_y_nombre_obligatorios(sesion, base):
    html = registrar(sesion, cedula="", nombre_completo="Sin Cédula")
    assert "obligatorios" in html
    html = registrar(sesion, cedula="20000002", nombre_completo="   ")
    assert "obligatorios" in html
    assert contar(base, "20000002") == 0


def test_cedula_solo_numeros(sesion, base):
    html = registrar(sesion, cedula="12AB", nombre_completo="Letras")
    assert "solo debe contener" in html
    assert contar(base, "12AB") == 0


def test_cedula_duplicada(sesion, base):
    # 10000001 ya existe en los pacientes de prueba
    html = registrar(sesion, cedula="10000001", nombre_completo="Repetido")
    assert "Ya existe" in html
    assert contar(base, "10000001") == 1


def test_edad_fuera_de_rango(sesion, base):
    html = registrar(sesion, cedula="20000003", nombre_completo="Edad Mala", edad="150")
    assert "entre 0 y 120" in html
    assert contar(base, "20000003") == 0


def test_nombre_sin_espacios_de_mas(sesion, base):
    registrar(sesion, cedula="20000004", nombre_completo="  Luis   Pérez  ")
    p = base.consultar("SELECT nombre_completo FROM paciente WHERE cedula = '20000004'", uno=True)
    assert p["nombre_completo"] == "Luis Pérez"


def test_buscar_paciente(sesion):
    html = sesion.get("/pacientes?q=Prueba Dos").get_data(as_text=True)
    assert "Paciente de Prueba Dos" in html
    assert "Paciente de Prueba Uno" not in html
