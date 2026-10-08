-- ============================================================
-- BioLab - Danimar | Esquema de la base de datos (Sprint 1)
-- Motor: SQLite
-- Historias cubiertas:
--   HU-01 Registrar un paciente
--   HU-02 Generar el presupuesto de los exámenes (orden + pago)
-- ============================================================

-- Categorías del catálogo (Hematología, Química, Uroanálisis...)
CREATE TABLE IF NOT EXISTS grupo_examen (
    id_grupo  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL UNIQUE
);

-- Catálogo de exámenes con su precio
CREATE TABLE IF NOT EXISTS examen (
    id_examen INTEGER PRIMARY KEY AUTOINCREMENT,
    id_grupo  INTEGER NOT NULL REFERENCES grupo_examen(id_grupo),
    nombre    TEXT NOT NULL,
    muestra   TEXT,
    costo     NUMERIC NOT NULL DEFAULT 0 CHECK (costo >= 0)
);

-- Pacientes del laboratorio (la cédula no se puede repetir)
CREATE TABLE IF NOT EXISTS paciente (
    id_paciente     INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula          TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    edad            INTEGER CHECK (edad IS NULL OR (edad BETWEEN 0 AND 120)),
    fecha_registro  TEXT NOT NULL DEFAULT (date('now','localtime'))
);

-- Orden (presupuesto) de un paciente y su estado de pago
CREATE TABLE IF NOT EXISTS orden (
    id_orden       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente    INTEGER NOT NULL REFERENCES paciente(id_paciente),
    fecha          TEXT NOT NULL DEFAULT (date('now','localtime')),
    estado_pago    TEXT NOT NULL DEFAULT 'pendiente'
                   CHECK (estado_pago IN ('pendiente','parcial','pago')),
    monto_abonado  NUMERIC NOT NULL DEFAULT 0 CHECK (monto_abonado >= 0)
);

-- Exámenes incluidos en cada orden. El precio se copia al crear la
-- orden, para que un cambio de precio futuro no altere órdenes viejas.
CREATE TABLE IF NOT EXISTS orden_examen (
    id_orden_examen INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden        INTEGER NOT NULL REFERENCES orden(id_orden) ON DELETE CASCADE,
    id_examen       INTEGER NOT NULL REFERENCES examen(id_examen),
    costo           NUMERIC NOT NULL DEFAULT 0,
    UNIQUE (id_orden, id_examen)
);

-- Vista: total, abonado y saldo de cada orden
CREATE VIEW IF NOT EXISTS v_orden_totales AS
SELECT o.id_orden,
       o.id_paciente,
       o.fecha,
       o.estado_pago,
       o.monto_abonado,
       COALESCE(SUM(oe.costo), 0)                       AS total,
       COALESCE(SUM(oe.costo), 0) - o.monto_abonado     AS saldo
FROM orden o
LEFT JOIN orden_examen oe ON oe.id_orden = o.id_orden
GROUP BY o.id_orden;
