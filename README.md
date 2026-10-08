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
│   ├── seed_catalogo.sql   # Catálogo de exámenes con precios
│   └── seed_pruebas.sql    # Pacientes ficticios para pruebas
├── templates/          # Pantallas (HTML)
├── static/css/         # Estilos
└── requirements.txt
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

**Acceso de prueba:** usuario `licenciada`, contraseña `biolab2026`.
Se pueden cambiar con las variables de entorno `BIOLAB_USUARIO` y `BIOLAB_CLAVE`.

## Equipo
Proyecto de Ingeniería de Software I — Ingeniería de Sistemas, Universidad de Pamplona.
