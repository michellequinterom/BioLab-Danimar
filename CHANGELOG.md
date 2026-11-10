# Registro de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Las versiones siguen [SemVer](https://semver.org/lang/es/).

## [0.1.0] - 2026-11
Primer release etiquetado del MVP.

### Incluye
- Inicio de sesión de la licenciada, con la contraseña fuera del código (archivo `.env`).
- HU-01: registro y búsqueda de pacientes, con validaciones (cédula numérica y no repetida, edad de 0 a 120).
- HU-02: presupuesto de exámenes por grupo, con el precio fijo en la orden.
- Pagos completos y abonos parciales, con saldo y estado de pago.
- Reglas del negocio separadas en `reglas.py`, con pruebas propias.
- Pruebas automáticas con pytest y prueba de rendimiento con 10.000 pacientes.

### Corregido
- Una orden con un examen inexistente ya no se guarda vacía, y la orden se guarda con sus exámenes en una sola transacción.

### Pendiente para próximas versiones
- HU-04: ingreso de resultados por parámetro.
- HU-07: reporte de resultados en PDF.
