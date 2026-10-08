# BioLab - Danimar

Sistema web local para el registro y control de pacientes, órdenes de exámenes y pagos del **Laboratorio Clínico Danimar**. Funciona en la computadora del laboratorio, sin necesidad de internet.

## Estado: Sprint 1

| Historia de usuario | Estado |
|---|---|
| **HU-01** Registrar un paciente | Hecho |
| **HU-02** Generar el presupuesto de los exámenes | Hecho |

### Qué incluye este incremento
- Inicio de sesión de la licenciada.
- Registro y consulta de pacientes, con validaciones:
  - cédula y nombre obligatorios;
  - la cédula solo admite números y no se puede repetir;
  - la edad debe estar entre 0 y 120.
- Catálogo de exámenes por categoría, con precios.
- Creación de órdenes: se eligen los exámenes y el total se calcula en vivo.
- Registro de pago completo o abonos parciales, con el saldo pendiente.

### Próximos incrementos (backlog)
- Carga de resultados por parámetro y valores de referencia.
- Reporte de resultados e impresión en PDF.
- Envío del reporte al paciente.
- Inventario de reactivos e insumos.
- Auditoría, respaldos y configuración.

## Tecnologías
- **Python 3** con **Flask** (servidor web local).
- **SQLite** (base de datos en un solo archivo, incluida en Python).
- **HTML, CSS y JavaScript** con plantillas Jinja2.

## Estructura
```
BioLab-Danimar/
├── app.py              # Rutas de la aplicación
├── db.py               # Conexión y creación de la base de datos
├── database/
│   ├── schema.sql      # Tablas y vista de totales
│   ├── seed_catalogo.sql   # Catálogo de exámenes (sin precios)
│   └── seed_pruebas.sql    # Pacientes ficticios para pruebas
├── templates/          # Pantallas (HTML)
├── static/css/         # Estilos
├── tests/              # Pruebas automáticas (pytest)
├── requirements.txt
└── requirements-dev.txt    # Dependencias para correr las pruebas
```

## Modelo de datos
`paciente` 1 — N `orden` 1 — N `orden_examen` N — 1 `examen` N — 1 `grupo_examen`

El precio de cada examen se copia en `orden_examen` al crear la orden, para que un cambio de precio futuro no altere presupuestos anteriores. La vista `v_orden_totales` calcula el total, lo abonado y el saldo de cada orden.

## Cómo ejecutarlo
```bash
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Luego abre **http://127.0.0.1:8000**.

La base de datos `biolab.db` se crea sola la primera vez, con el catálogo y tres pacientes de prueba.
El catálogo de prueba no incluye precios (todos en 0); los precios reales se cargan en un incremento posterior.

**Acceso:** el usuario es `licenciada`. Ninguna contraseña está escrita en el código:
- Si no se define la variable `BIOLAB_CLAVE`, al iniciar se genera una **contraseña temporal** y se muestra en la consola.
- Para fijar una contraseña propia:
  ```bash
  export BIOLAB_CLAVE="tu-contraseña"      # En Windows: set BIOLAB_CLAVE=tu-contraseña
  python app.py
  ```
- Variables opcionales: `BIOLAB_USUARIO` (nombre de usuario) y `BIOLAB_SECRET` (clave de las sesiones; si no existe, se genera una aleatoria).

## Pruebas
Las pruebas automáticas cubren los criterios de aceptación de HU-01 y HU-02. Cada prueba usa una base de datos temporal y nueva.

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

| Archivo | Qué verifica |
|---|---|
| `tests/test_login.py` | Acceso con usuario y contraseña, bloqueo sin sesión y cierre de sesión |
| `tests/test_pacientes.py` | Registro válido, campos obligatorios, cédula numérica y no repetida, rango de edad y búsqueda |
| `tests/test_ordenes.py` | Cálculo del total, exámenes repetidos, orden sin paciente o sin exámenes, precio fijo en la orden, abonos, abono mayor al saldo y pago completo |

## Equipo
Proyecto de Ingeniería de Software I — Ingeniería de Sistemas, Universidad de Pamplona.
