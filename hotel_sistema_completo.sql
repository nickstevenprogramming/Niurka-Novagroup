-- ================================================================
--  SISTEMA DE RESERVAS · HOTEL
--  MySQL 8.0+  |  Un solo establecimiento
--  Módulos: Habitaciones · Reservas · Huéspedes · Empleados
--           Facturación · Pagos · Inventario · Restaurante
--           Amas de llaves · Mantenimiento · Reseñas
--           Notificaciones · Auditoría · Dashboard
-- ================================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP DATABASE IF EXISTS hotel_reservas;
CREATE DATABASE hotel_reservas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotel_reservas;

-- ================================================================
-- ██ 1. CONFIGURACIÓN DEL HOTEL
-- ================================================================

CREATE TABLE hotel (
    id               TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    ruc              VARCHAR(20),
    direccion        VARCHAR(200),
    ciudad           VARCHAR(80),
    pais             VARCHAR(60) DEFAULT 'República Dominicana',
    telefono         VARCHAR(20),
    email            VARCHAR(100),
    sitio_web        VARCHAR(120),
    estrellas        TINYINT UNSIGNED DEFAULT 3,
    check_in_hora    TIME NOT NULL DEFAULT '14:00:00',
    check_out_hora   TIME NOT NULL DEFAULT '12:00:00',
    moneda           CHAR(3) DEFAULT 'DOP',
    impuesto_pct     DECIMAL(5,2) DEFAULT 18.00,
    politica_cancel  TEXT,
    activo           TINYINT(1) DEFAULT 1,
    creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO hotel (nombre, ruc, direccion, ciudad, telefono, email, sitio_web, estrellas,
                   check_in_hora, check_out_hora, impuesto_pct, politica_cancel) VALUES
('Hotel Anacaona & Spa', '1-23-45678-9', 'Av. Anacaona 18, Mirador Sur',
 'Santo Domingo', '809-555-0100', 'recepcion@anacaona.do', 'www.anacaona.do',
 4, '15:00:00', '12:00:00', 18.00,
 'Cancelación gratuita hasta 48 horas antes. Después se cobra 1 noche.');


-- ================================================================
-- ██ 2. CATÁLOGOS Y TIPOS
-- ================================================================

CREATE TABLE tipos_habitacion (
    id              TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(60)  NOT NULL,   -- Estándar, Superior, Junior Suite…
    descripcion     TEXT,
    capacidad_min   TINYINT UNSIGNED NOT NULL DEFAULT 1,
    capacidad_max   TINYINT UNSIGNED NOT NULL DEFAULT 2,
    camas           VARCHAR(60),             -- '1 king', '2 twins', etc.
    area_m2         DECIMAL(6,2),
    piso_minimo     TINYINT UNSIGNED DEFAULT 1,
    piso_maximo     TINYINT UNSIGNED DEFAULT 1,
    precio_base     DECIMAL(10,2) NOT NULL,  -- tarifa rack por noche
    activo          TINYINT(1) DEFAULT 1
);

INSERT INTO tipos_habitacion (nombre, descripcion, capacidad_min, capacidad_max, camas, area_m2, piso_minimo, piso_maximo, precio_base) VALUES
('Estándar Simple',  'Habitación estándar con vista al jardín',      1,1,'1 Queen',     22, 1,3,  2800.00),
('Estándar Doble',   'Habitación estándar con dos camas',            1,2,'2 Twins',     24, 1,3,  3200.00),
('Superior',         'Habitación superior con vista a la piscina',   1,2,'1 King',      28, 2,4,  4500.00),
('Junior Suite',     'Suite amplia con sala de estar',               1,3,'1 King+Sofá', 45, 3,5,  7500.00),
('Suite Master',     'Suite de lujo con jacuzzi y terraza',          1,4,'1 King+Twins',70, 5,5, 14000.00),
('Suite Presidencial','Suite ejecutiva con salón privado',           1,6,'2 King',     110, 5,5, 28000.00);


CREATE TABLE amenidades (
    id     SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    icono  VARCHAR(10)
);

INSERT INTO amenidades (nombre, icono) VALUES
('WiFi','📶'),('TV Cable','📺'),('Aire Acondicionado','❄️'),('Minibar','🍸'),
('Caja Fuerte','🔐'),('Bañera','🛁'),('Jacuzzi','♨️'),('Terraza','🌅'),
('Vista al Mar','🌊'),('Cocina','🍳'),('Sala de Estar','🛋'),('Balcón','🏙');

CREATE TABLE habitacion_amenidades (
    tipo_habitacion_id TINYINT UNSIGNED NOT NULL,
    amenidad_id        SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (tipo_habitacion_id, amenidad_id),
    FOREIGN KEY (tipo_habitacion_id) REFERENCES tipos_habitacion(id),
    FOREIGN KEY (amenidad_id)        REFERENCES amenidades(id)
);

INSERT INTO habitacion_amenidades VALUES
(1,1),(1,2),(1,3),
(2,1),(2,2),(2,3),
(3,1),(3,2),(3,3),(3,4),(3,5),
(4,1),(4,2),(4,3),(4,4),(4,5),(4,11),
(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(5,11),
(6,1),(6,2),(6,3),(6,4),(6,5),(6,6),(6,7),(6,8),(6,9),(6,10),(6,11),(6,12);


-- ================================================================
-- ██ 3. HABITACIONES (INVENTARIO FÍSICO)
-- ================================================================

CREATE TABLE habitaciones (
    id                 SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo_id            TINYINT UNSIGNED NOT NULL,
    numero             VARCHAR(10) NOT NULL UNIQUE,   -- '101', '305', 'PH-1'
    piso               TINYINT UNSIGNED NOT NULL,
    estado             ENUM('disponible','ocupada','mantenimiento','bloqueada','limpieza') NOT NULL DEFAULT 'disponible',
    estado_limpieza    ENUM('limpia','sucia','en_proceso','inspeccion') NOT NULL DEFAULT 'limpia',
    fumadores          TINYINT(1) DEFAULT 0,
    accesible          TINYINT(1) DEFAULT 0,           -- accesibilidad discapacitados
    notas_internas     TEXT,
    ultima_limpieza    DATETIME,
    activa             TINYINT(1) DEFAULT 1,
    FOREIGN KEY (tipo_id) REFERENCES tipos_habitacion(id),
    INDEX idx_estado (estado),
    INDEX idx_piso   (piso)
);

INSERT INTO habitaciones (tipo_id, numero, piso, accesible) VALUES
-- Piso 1
(1,'101',1,1),(1,'102',1,0),(2,'103',1,0),(2,'104',1,0),(1,'105',1,1),
-- Piso 2
(1,'201',2,0),(1,'202',2,0),(2,'203',2,0),(3,'204',2,0),(3,'205',2,0),
-- Piso 3
(2,'301',3,0),(2,'302',3,0),(3,'303',3,0),(3,'304',3,0),(4,'305',3,0),
-- Piso 4
(3,'401',4,0),(3,'402',4,0),(4,'403',4,0),(4,'404',4,0),(3,'405',4,0),
-- Piso 5 (suites)
(4,'501',5,0),(4,'502',5,0),(5,'503',5,0),(5,'504',5,0),(6,'PH-1',5,0);


-- ================================================================
-- ██ 4. TARIFAS Y TEMPORADAS
-- ================================================================

CREATE TABLE temporadas (
    id           TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(60) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin    DATE NOT NULL,
    multiplicador DECIMAL(4,2) NOT NULL DEFAULT 1.00,  -- 1.30 = +30%
    activa       TINYINT(1) DEFAULT 1,
    INDEX idx_fechas (fecha_inicio, fecha_fin)
);

INSERT INTO temporadas (nombre, fecha_inicio, fecha_fin, multiplicador) VALUES
('Temporada Alta Navidad', '2024-12-15', '2025-01-05', 1.50),
('Semana Santa',           '2025-04-13', '2025-04-21', 1.40),
('Temporada Baja Ago',     '2024-08-01', '2024-08-31', 0.85),
('Carnaval',               '2025-02-24', '2025-03-04', 1.25);

CREATE TABLE tarifas_especiales (
    id                 INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo_habitacion_id TINYINT UNSIGNED NOT NULL,
    temporada_id       TINYINT UNSIGNED,
    nombre             VARCHAR(80) NOT NULL,    -- 'Tarifa AAA', 'Paquete Romance'
    precio_noche       DECIMAL(10,2) NOT NULL,
    min_noches         TINYINT UNSIGNED DEFAULT 1,
    incluye_desayuno   TINYINT(1) DEFAULT 0,
    activa             TINYINT(1) DEFAULT 1,
    FOREIGN KEY (tipo_habitacion_id) REFERENCES tipos_habitacion(id),
    FOREIGN KEY (temporada_id)       REFERENCES temporadas(id)
);

INSERT INTO tarifas_especiales (tipo_habitacion_id, nombre, precio_noche, min_noches, incluye_desayuno) VALUES
(3,'Tarifa Corporativa',  3800.00, 3, 1),
(4,'Paquete Romance',     9500.00, 2, 1),
(5,'Paquete Honeymoon',  18000.00, 3, 1),
(6,'Tarifa Gobierno',    22000.00, 1, 0);


-- ================================================================
-- ██ 5. HUÉSPEDES / CLIENTES
-- ================================================================

CREATE TABLE paises (
    codigo CHAR(2) PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL
);

INSERT INTO paises VALUES
('DO','República Dominicana'),('US','Estados Unidos'),('ES','España'),
('MX','México'),('CO','Colombia'),('VE','Venezuela'),('PR','Puerto Rico'),
('FR','Francia'),('DE','Alemania'),('GB','Reino Unido'),('CA','Canadá'),
('BR','Brasil'),('AR','Argentina'),('IT','Italia'),('PT','Portugal');

CREATE TABLE huespedes (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo_documento   ENUM('cedula','pasaporte','licencia','otro') NOT NULL DEFAULT 'pasaporte',
    num_documento    VARCHAR(30) NOT NULL,
    nombre           VARCHAR(80) NOT NULL,
    apellido         VARCHAR(80) NOT NULL,
    email            VARCHAR(120) UNIQUE,
    telefono         VARCHAR(25),
    telefono2        VARCHAR(25),
    fecha_nacimiento DATE,
    genero           ENUM('M','F','otro'),
    pais_id          CHAR(2),
    ciudad_origen    VARCHAR(80),
    direccion        VARCHAR(200),
    empresa          VARCHAR(100),
    ruc_empresa      VARCHAR(30),
    nivel_vip        TINYINT UNSIGNED DEFAULT 0,    -- 0=normal,1=silver,2=gold,3=platinum
    notas            TEXT,
    blacklist        TINYINT(1) DEFAULT 0,
    creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_doc (tipo_documento, num_documento),
    FOREIGN KEY (pais_id) REFERENCES paises(codigo),
    INDEX idx_email    (email),
    INDEX idx_apellido (apellido)
);

INSERT INTO huespedes (tipo_documento, num_documento, nombre, apellido, email, telefono, pais_id, nivel_vip) VALUES
('cedula',  '001-1234567-8', 'Carlos',    'Martínez',  'carlos@example.com',  '809-555-1001', 'DO', 1),
('cedula',  '001-2345678-9', 'Ana',       'Gómez',     'ana@example.com',     '809-555-1002', 'DO', 0),
('pasaporte','A12345678',    'John',      'Williams',   'john@example.com',    '1-555-2001',   'US', 2),
('pasaporte','B98765432',    'Sophie',    'Dupont',     'sophie@example.com',  '33-6-1234',    'FR', 0),
('cedula',  '002-3456789-0', 'Luisa',     'Fernández', 'luisa@example.com',   '829-555-1003', 'DO', 1),
('pasaporte','C11223344',    'Alejandro', 'García',     'alex@example.com',    '52-55-5678',   'MX', 0),
('cedula',  '001-9876543-2', 'María',     'Rodríguez', 'mariard@example.com', '849-555-1004', 'DO', 3);


-- ================================================================
-- ██ 6. CANALES DE DISTRIBUCIÓN
-- ================================================================

CREATE TABLE canales (
    id         TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,    -- Booking.com, Airbnb, Directo, OTA…
    comision   DECIMAL(5,2) DEFAULT 0.00,
    activo     TINYINT(1) DEFAULT 1
);

INSERT INTO canales (nombre, comision) VALUES
('Directo Web',    0.00),
('Teléfono',       0.00),
('Walk-in',        0.00),
('Booking.com',   15.00),
('Expedia',       18.00),
('Airbnb',        14.00),
('Agencia Local',  8.00),
('OTA Otro',      16.00);


-- ================================================================
-- ██ 7. RESERVAS (NÚCLEO)
-- ================================================================

CREATE TABLE estados_reserva (
    id     TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    color  VARCHAR(7)
);

INSERT INTO estados_reserva (nombre, color) VALUES
('pendiente',  '#f9a825'),
('confirmada', '#6c63ff'),
('en_curso',   '#43e97b'),
('completada', '#2196f3'),
('cancelada',  '#ff6584'),
('no_show',    '#9e9e9e');

CREATE TABLE reservas (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo           VARCHAR(14) NOT NULL UNIQUE,       -- RES-2025-000001
    huesped_id       INT UNSIGNED NOT NULL,
    habitacion_id    SMALLINT UNSIGNED NOT NULL,
    canal_id         TINYINT UNSIGNED NOT NULL DEFAULT 1,
    tarifa_id        INT UNSIGNED,                      -- NULL = precio_base del tipo
    estado_id        TINYINT UNSIGNED NOT NULL DEFAULT 1,
    fecha_entrada    DATE NOT NULL,
    fecha_salida     DATE NOT NULL,
    hora_llegada_est TIME,                              -- hora estimada de llegada
    num_adultos      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    num_ninos        TINYINT UNSIGNED NOT NULL DEFAULT 0,
    precio_noche     DECIMAL(10,2) NOT NULL,
    precio_total     DECIMAL(10,2) NOT NULL,
    impuesto_total   DECIMAL(10,2) NOT NULL DEFAULT 0,
    descuento_monto  DECIMAL(10,2) NOT NULL DEFAULT 0,
    deposito_req     DECIMAL(10,2) NOT NULL DEFAULT 0,
    deposito_pagado  DECIMAL(10,2) NOT NULL DEFAULT 0,
    incluye_desayuno TINYINT(1) DEFAULT 0,
    incluye_almuerzo TINYINT(1) DEFAULT 0,
    incluye_cena     TINYINT(1) DEFAULT 0,
    codigo_externo   VARCHAR(60),                       -- código en Booking/Expedia
    notas_huesped    TEXT,
    notas_internas   TEXT,
    staff_creador_id INT UNSIGNED,
    creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizado_en   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (fecha_salida > fecha_entrada),
    CHECK (num_adultos >= 1),
    FOREIGN KEY (huesped_id)       REFERENCES huespedes(id),
    FOREIGN KEY (habitacion_id)    REFERENCES habitaciones(id),
    FOREIGN KEY (canal_id)         REFERENCES canales(id),
    FOREIGN KEY (tarifa_id)        REFERENCES tarifas_especiales(id),
    FOREIGN KEY (estado_id)        REFERENCES estados_reserva(id),
    INDEX idx_entrada    (fecha_entrada),
    INDEX idx_salida     (fecha_salida),
    INDEX idx_huesped    (huesped_id),
    INDEX idx_habitacion (habitacion_id),
    INDEX idx_estado     (estado_id)
);

INSERT INTO reservas (codigo, huesped_id, habitacion_id, canal_id, estado_id,
    fecha_entrada, fecha_salida, num_adultos, precio_noche, precio_total, impuesto_total,
    deposito_req, deposito_pagado, incluye_desayuno) VALUES
('RES-2025-000001', 1, 3,  1, 2, '2025-02-01','2025-02-04', 2, 4500.00, 13500.00, 2430.00, 4500.00, 4500.00, 1),
('RES-2025-000002', 2, 7,  4, 2, '2025-02-10','2025-02-12', 1, 3200.00,  6400.00, 1152.00, 3200.00, 3200.00, 0),
('RES-2025-000003', 3, 15, 1, 3, '2025-02-15','2025-02-20', 2, 7500.00, 37500.00, 6750.00,15000.00,15000.00, 1),
('RES-2025-000004', 4, 23, 3, 1, '2025-03-05','2025-03-10', 2,14000.00, 70000.00,12600.00,28000.00,    0.00, 1),
('RES-2025-000005', 5, 1,  2, 2, '2025-01-20','2025-01-22', 1, 2800.00,  5600.00, 1008.00, 2800.00, 2800.00, 0),
('RES-2025-000006', 6, 18, 4, 4, '2025-04-13','2025-04-18', 2, 9500.00, 47500.00, 8550.00,19000.00, 9500.00, 1),
('RES-2025-000007', 7, 25, 1, 2, '2025-05-01','2025-05-07', 4,28000.00,168000.00,30240.00,56000.00,56000.00, 1);


-- Huéspedes adicionales en la misma habitación
CREATE TABLE reserva_huespedes_adicionales (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id   INT UNSIGNED NOT NULL,
    huesped_id   INT UNSIGNED NOT NULL,
    es_titular   TINYINT(1) DEFAULT 0,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE,
    FOREIGN KEY (huesped_id) REFERENCES huespedes(id),
    UNIQUE KEY uk_res_hue (reserva_id, huesped_id)
);

-- Solicitudes especiales vinculadas a reservas
CREATE TABLE solicitudes_especiales (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id  INT UNSIGNED NOT NULL,
    tipo        ENUM('cama_extra','cuna','almohada_especial','dieta','decoracion',
                     'traslado','early_checkin','late_checkout','accesibilidad','otro') NOT NULL,
    descripcion VARCHAR(255),
    atendida    TINYINT(1) DEFAULT 0,
    creado_en   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE
);

INSERT INTO solicitudes_especiales (reserva_id, tipo, descripcion) VALUES
(1,'almohada_especial','Sin plumas, alergia'),
(3,'decoracion','Aniversario - flores y champaña'),
(7,'cama_extra','Bebé de 8 meses, solicita cuna');


-- ================================================================
-- ██ 8. CHECK-IN / CHECK-OUT
-- ================================================================

CREATE TABLE check_ins (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id      INT UNSIGNED NOT NULL UNIQUE,
    huesped_id      INT UNSIGNED NOT NULL,
    habitacion_id   SMALLINT UNSIGNED NOT NULL,
    staff_id        INT UNSIGNED,
    fecha_hora      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    llave_entregada TINYINT(1) DEFAULT 1,
    num_llaves      TINYINT UNSIGNED DEFAULT 1,
    observaciones   TEXT,
    FOREIGN KEY (reserva_id)   REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)   REFERENCES huespedes(id),
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
);

CREATE TABLE check_outs (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id       INT UNSIGNED NOT NULL UNIQUE,
    huesped_id       INT UNSIGNED NOT NULL,
    habitacion_id    SMALLINT UNSIGNED NOT NULL,
    staff_id         INT UNSIGNED,
    fecha_hora       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    llaves_devueltas TINYINT UNSIGNED DEFAULT 1,
    cargo_extra      DECIMAL(10,2) DEFAULT 0.00,
    motivo_cargo     VARCHAR(200),
    satisfaccion     TINYINT UNSIGNED,   -- 1-5 escala rápida
    FOREIGN KEY (reserva_id)   REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)   REFERENCES huespedes(id),
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
);

INSERT INTO check_ins (reserva_id, huesped_id, habitacion_id, fecha_hora) VALUES
(5, 5, 1, '2025-01-20 15:30:00');

INSERT INTO check_outs (reserva_id, huesped_id, habitacion_id, fecha_hora, satisfaccion) VALUES
(5, 5, 1, '2025-01-22 11:45:00', 5);


-- ================================================================
-- ██ 9. EMPLEADOS
-- ================================================================

CREATE TABLE departamentos (
    id     TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL
);

INSERT INTO departamentos (nombre) VALUES
('Recepción'),('Amas de Llaves'),('Restaurante & Bar'),('Mantenimiento'),
('Seguridad'),('Administración'),('Spa & Bienestar'),('Cocina');

CREATE TABLE cargos (
    id              TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    departamento_id TINYINT UNSIGNED NOT NULL,
    nombre          VARCHAR(80) NOT NULL,
    nivel           TINYINT UNSIGNED DEFAULT 1,    -- 1=operativo,2=supervisor,3=jefatura
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
);

INSERT INTO cargos (departamento_id, nombre, nivel) VALUES
(1,'Recepcionista',1),(1,'Jefe de Recepción',3),(1,'Conserje',1),
(2,'Camarera',1),(2,'Supervisora de Piso',2),(2,'Gobernanta',3),
(3,'Mesero',1),(3,'Bartender',1),(3,'Capitán de Meseros',2),
(4,'Técnico',1),(4,'Jefe de Mantenimiento',3),
(5,'Guardia',1),(5,'Jefe de Seguridad',3),
(6,'Contador',2),(6,'Gerente General',3),
(7,'Esteticista',1),(7,'Masajista',1),
(8,'Cocinero',1),(8,'Chef',3);

CREATE TABLE empleados (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cargo_id        TINYINT UNSIGNED NOT NULL,
    cedula          VARCHAR(20) NOT NULL UNIQUE,
    nombre          VARCHAR(80) NOT NULL,
    apellido        VARCHAR(80) NOT NULL,
    email           VARCHAR(120) UNIQUE,
    telefono        VARCHAR(25),
    fecha_ingreso   DATE NOT NULL,
    fecha_egreso    DATE,
    salario         DECIMAL(10,2),
    activo          TINYINT(1) DEFAULT 1,
    FOREIGN KEY (cargo_id) REFERENCES cargos(id),
    INDEX idx_cargo (cargo_id)
);

INSERT INTO empleados (cargo_id, cedula, nombre, apellido, email, fecha_ingreso, salario, activo) VALUES
(2,'001-1111111-1','Pedro',    'Herrera',  'pedro@anacaona.do', '2020-01-15', 45000.00, 1),
(1,'001-2222222-2','Yesenia',  'Santos',   'yes@anacaona.do',   '2021-03-01', 28000.00, 1),
(1,'001-3333333-3','Roberto',  'Familia',  'rob@anacaona.do',   '2022-06-10', 28000.00, 1),
(6,'001-4444444-4','Carmen',   'Reyes',    'carmen@anacaona.do','2018-07-20', 38000.00, 1),
(5,'001-5555555-5','Gloria',   'Pichardo', 'gloria@anacaona.do','2019-02-01', 35000.00, 1),
(18,'001-6666666-6','Chef José','Almonte', 'jose@anacaona.do',  '2017-05-15', 60000.00, 1),
(15,'001-7777777-7','Lic. Ana', 'Castillo','ana.c@anacaona.do', '2016-01-10', 80000.00, 1);


CREATE TABLE usuarios_sistema (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    empleado_id  INT UNSIGNED NOT NULL UNIQUE,
    username     VARCHAR(40) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol          ENUM('admin','gerente','recepcion','housekeeping','restaurante','mantenimiento','seguridad') NOT NULL,
    activo       TINYINT(1) DEFAULT 1,
    ultimo_login DATETIME,
    creado_en    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);

INSERT INTO usuarios_sistema (empleado_id, username, password_hash, rol) VALUES
(7, 'admin',      SHA2('admin2025!',256),  'admin'),
(1, 'pedro.h',    SHA2('recep2025!',256),  'gerente'),
(2, 'yesenia.s',  SHA2('recep2025!',256),  'recepcion'),
(3, 'roberto.f',  SHA2('recep2025!',256),  'recepcion'),
(5, 'gloria.p',   SHA2('house2025!',256),  'housekeeping'),
(6, 'chef.jose',  SHA2('rest2025!',256),   'restaurante');

-- Turnos de trabajo
CREATE TABLE turnos (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    empleado_id  INT UNSIGNED NOT NULL,
    fecha        DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida  TIME NOT NULL,
    tipo         ENUM('mañana','tarde','noche') NOT NULL,
    asistio      TINYINT(1),    -- NULL=pendiente,1=sí,0=falta
    notas        VARCHAR(200),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
    INDEX idx_fecha_emp (fecha, empleado_id)
);


-- ================================================================
-- ██ 10. FACTURACIÓN Y PAGOS
-- ================================================================

CREATE TABLE metodos_pago (
    id     TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(40) NOT NULL
);

INSERT INTO metodos_pago (nombre) VALUES
('Efectivo DOP'),('Efectivo USD'),('Tarjeta Visa'),('Tarjeta MasterCard'),
('Tarjeta AmEx'),('Transferencia Bancaria'),('Cheque'),('OTA (Booking/Expedia)'),('Crédito Hotel');

CREATE TABLE facturas (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    numero         VARCHAR(20) NOT NULL UNIQUE,    -- FAC-2025-0001
    reserva_id     INT UNSIGNED NOT NULL,
    huesped_id     INT UNSIGNED NOT NULL,
    fecha_emision  DATE NOT NULL DEFAULT (CURDATE()),
    subtotal       DECIMAL(10,2) NOT NULL,
    impuesto       DECIMAL(10,2) NOT NULL DEFAULT 0,
    descuento      DECIMAL(10,2) NOT NULL DEFAULT 0,
    total          DECIMAL(10,2) NOT NULL,
    estado         ENUM('borrador','emitida','pagada','anulada','vencida') NOT NULL DEFAULT 'borrador',
    tipo           ENUM('hospedaje','restaurante','spa','mixta','otro') NOT NULL DEFAULT 'hospedaje',
    notas          TEXT,
    creado_por     INT UNSIGNED,
    creado_en      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id)  REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)  REFERENCES huespedes(id),
    FOREIGN KEY (creado_por)  REFERENCES empleados(id),
    INDEX idx_reserva (reserva_id),
    INDEX idx_estado  (estado)
);

INSERT INTO facturas (numero, reserva_id, huesped_id, subtotal, impuesto, total, estado) VALUES
('FAC-2025-0001', 1, 1, 13500.00, 2430.00, 15930.00, 'pagada'),
('FAC-2025-0002', 2, 2,  6400.00, 1152.00,  7552.00, 'pagada'),
('FAC-2025-0005', 5, 5,  5600.00, 1008.00,  6608.00, 'pagada');

CREATE TABLE items_factura (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    factura_id   INT UNSIGNED NOT NULL,
    descripcion  VARCHAR(200) NOT NULL,
    cantidad     DECIMAL(8,2) NOT NULL DEFAULT 1,
    precio_unit  DECIMAL(10,2) NOT NULL,
    subtotal     DECIMAL(10,2) NOT NULL,
    tipo         ENUM('noche','desayuno','almuerzo','cena','minibar','telefono',
                      'lavanderia','spa','parking','otro') NOT NULL DEFAULT 'noche',
    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE
);

INSERT INTO items_factura (factura_id, descripcion, cantidad, precio_unit, subtotal, tipo) VALUES
(1,'Hospedaje - Superior (3 noches)',3,4500.00,13500.00,'noche'),
(2,'Hospedaje - Estándar Doble (2 noches)',2,3200.00,6400.00,'noche'),
(3,'Hospedaje - Estándar Simple (2 noches)',2,2800.00,5600.00,'noche');

CREATE TABLE pagos (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    factura_id      INT UNSIGNED NOT NULL,
    metodo_id       TINYINT UNSIGNED NOT NULL,
    monto           DECIMAL(10,2) NOT NULL,
    referencia      VARCHAR(80),
    moneda          CHAR(3) DEFAULT 'DOP',
    tasa_cambio     DECIMAL(10,4) DEFAULT 1.0000,
    monto_usd       DECIMAL(10,2),
    es_deposito     TINYINT(1) DEFAULT 0,
    pagado_en       DATETIME DEFAULT CURRENT_TIMESTAMP,
    registrado_por  INT UNSIGNED,
    notas           VARCHAR(255),
    FOREIGN KEY (factura_id)     REFERENCES facturas(id),
    FOREIGN KEY (metodo_id)      REFERENCES metodos_pago(id),
    FOREIGN KEY (registrado_por) REFERENCES empleados(id)
);

INSERT INTO pagos (factura_id, metodo_id, monto, referencia, es_deposito, registrado_por) VALUES
(1, 3, 4500.00, 'DEP-TXN-001', 1, 2),
(1, 3, 11430.00,'TXN-CH1-001', 0, 2),
(2, 8, 7552.00, 'BK-98765432', 0, 2),
(3, 1, 6608.00, NULL,          0, 3);

-- Cargos extras en habitación (minibar, room service, etc.)
CREATE TABLE cargos_habitacion (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id      INT UNSIGNED NOT NULL,
    habitacion_id   SMALLINT UNSIGNED NOT NULL,
    tipo            ENUM('minibar','room_service','telefono','lavanderia','spa',
                         'parking','danio','otro') NOT NULL,
    descripcion     VARCHAR(200) NOT NULL,
    monto           DECIMAL(10,2) NOT NULL,
    facturado       TINYINT(1) DEFAULT 0,
    registrado_por  INT UNSIGNED,
    registrado_en   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id)     REFERENCES reservas(id),
    FOREIGN KEY (habitacion_id)  REFERENCES habitaciones(id),
    FOREIGN KEY (registrado_por) REFERENCES empleados(id)
);


-- ================================================================
-- ██ 11. HOUSEKEEPING (AMAS DE LLAVES)
-- ================================================================

CREATE TABLE asignaciones_limpieza (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    habitacion_id   SMALLINT UNSIGNED NOT NULL,
    empleada_id     INT UNSIGNED NOT NULL,
    fecha           DATE NOT NULL,
    tipo            ENUM('diaria','salida','llegada','profunda','inspeccion') NOT NULL,
    estado          ENUM('pendiente','en_proceso','completada','verificada') NOT NULL DEFAULT 'pendiente',
    hora_inicio     TIME,
    hora_fin        TIME,
    duracion_min    SMALLINT UNSIGNED,
    observaciones   TEXT,
    inspeccionada_por INT UNSIGNED,    -- supervisor
    FOREIGN KEY (habitacion_id)     REFERENCES habitaciones(id),
    FOREIGN KEY (empleada_id)       REFERENCES empleados(id),
    FOREIGN KEY (inspeccionada_por) REFERENCES empleados(id),
    INDEX idx_fecha_hab (fecha, habitacion_id)
);

CREATE TABLE incidencias_limpieza (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    asignacion_id  INT UNSIGNED NOT NULL,
    tipo           ENUM('objeto_olvidado','danio','faltante','otro') NOT NULL,
    descripcion    TEXT NOT NULL,
    atendida       TINYINT(1) DEFAULT 0,
    creado_en      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asignacion_id) REFERENCES asignaciones_limpieza(id)
);

CREATE TABLE objetos_olvidados (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    habitacion_id  SMALLINT UNSIGNED NOT NULL,
    descripcion    VARCHAR(200) NOT NULL,
    encontrado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado         ENUM('en_custodia','devuelto','descartado') DEFAULT 'en_custodia',
    huesped_id     INT UNSIGNED,
    empleado_id    INT UNSIGNED,
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id),
    FOREIGN KEY (huesped_id)    REFERENCES huespedes(id),
    FOREIGN KEY (empleado_id)   REFERENCES empleados(id)
);


-- ================================================================
-- ██ 12. MANTENIMIENTO
-- ================================================================

CREATE TABLE ordenes_mantenimiento (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    habitacion_id  SMALLINT UNSIGNED,
    area           VARCHAR(80),         -- 'Lobby', 'Piscina', 'Estacionamiento'
    tipo           ENUM('correctivo','preventivo','emergencia') NOT NULL DEFAULT 'correctivo',
    prioridad      ENUM('baja','media','alta','critica') NOT NULL DEFAULT 'media',
    descripcion    TEXT NOT NULL,
    reportado_por  INT UNSIGNED,
    asignado_a     INT UNSIGNED,
    estado         ENUM('abierta','en_proceso','completada','cancelada') NOT NULL DEFAULT 'abierta',
    fecha_reporte  DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_inicio   DATETIME,
    fecha_cierre   DATETIME,
    costo_material DECIMAL(10,2) DEFAULT 0.00,
    notas_cierre   TEXT,
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id),
    FOREIGN KEY (reportado_por) REFERENCES empleados(id),
    FOREIGN KEY (asignado_a)    REFERENCES empleados(id),
    INDEX idx_estado (estado),
    INDEX idx_prio   (prioridad)
);

INSERT INTO ordenes_mantenimiento (habitacion_id, tipo, prioridad, descripcion, reportado_por, estado) VALUES
(3, 'correctivo','alta',    'Aire acondicionado no enfría', 2, 'en_proceso'),
(7, 'correctivo','media',   'Ducha con presión baja',       2, 'abierta'),
(NULL,'preventivo','baja',  'Revisión mensual piscina',     1, 'abierta');


-- ================================================================
-- ██ 13. RESTAURANTE & MINIBAR DEL HOTEL
-- ================================================================

CREATE TABLE categorias_menu (
    id     SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    tipo   ENUM('desayuno','almuerzo','cena','snack','bebida','postre') NOT NULL
);

INSERT INTO categorias_menu (nombre, tipo) VALUES
('Desayunos Clásicos','desayuno'),('Desayunos Buffet','desayuno'),
('Entradas','almuerzo'),('Platos Principales','almuerzo'),('Ensaladas','almuerzo'),
('Postres','postre'),('Bebidas Calientes','bebida'),('Bebidas Frías','bebida'),('Cócteles','bebida'),
('Cenas Gourmet','cena'),('Snacks Room Service','snack');

CREATE TABLE productos_menu (
    id           SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    categoria_id SMALLINT UNSIGNED NOT NULL,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  TEXT,
    precio       DECIMAL(10,2) NOT NULL,
    disponible   TINYINT(1) DEFAULT 1,
    es_minibar   TINYINT(1) DEFAULT 0,
    FOREIGN KEY (categoria_id) REFERENCES categorias_menu(id)
);

INSERT INTO productos_menu (categoria_id, nombre, precio, es_minibar) VALUES
(1,'Desayuno Americano', 650.00,0),(1,'Desayuno Dominicano',580.00,0),
(2,'Buffet Desayuno',    850.00,0),
(4,'Filete de Res',     1800.00,0),(4,'Pechuga de Pollo',   1200.00,0),
(4,'Langosta a la Plancha',3500.00,0),
(6,'Flan de Vainilla',   350.00,0),(6,'Cheesecake',         420.00,0),
(7,'Café Americano',     150.00,0),(7,'Cappuccino',          200.00,0),
(8,'Jugo Natural',       220.00,0),(8,'Agua Mineral 500ml', 120.00,1),
(9,'Mojito',             350.00,0),(9,'Piña Colada',         380.00,0),
(11,'Club Sándwich',     680.00,0),(11,'Alitas BBQ',         750.00,0);

CREATE TABLE pedidos_restaurante (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id     INT UNSIGNED,     -- NULL si no es huésped
    huesped_id     INT UNSIGNED,
    tipo           ENUM('restaurante','room_service','bar','minibar') NOT NULL DEFAULT 'restaurante',
    mesa           VARCHAR(10),
    estado         ENUM('recibido','preparando','servido','cancelado') NOT NULL DEFAULT 'recibido',
    total          DECIMAL(10,2) NOT NULL DEFAULT 0,
    facturado      TINYINT(1) DEFAULT 0,
    atendido_por   INT UNSIGNED,
    creado_en      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id)   REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)   REFERENCES huespedes(id),
    FOREIGN KEY (atendido_por) REFERENCES empleados(id)
);

CREATE TABLE items_pedido (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pedido_id     INT UNSIGNED NOT NULL,
    producto_id   SMALLINT UNSIGNED NOT NULL,
    cantidad      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    precio_unit   DECIMAL(10,2) NOT NULL,
    subtotal      DECIMAL(10,2) NOT NULL,
    notas         VARCHAR(200),
    FOREIGN KEY (pedido_id)   REFERENCES pedidos_restaurante(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos_menu(id)
);


-- ================================================================
-- ██ 14. SPA & SERVICIOS ADICIONALES
-- ================================================================

CREATE TABLE servicios_spa (
    id          SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT,
    duracion_min SMALLINT UNSIGNED NOT NULL,
    precio      DECIMAL(10,2) NOT NULL,
    disponible  TINYINT(1) DEFAULT 1
);

INSERT INTO servicios_spa (nombre, duracion_min, precio) VALUES
('Masaje Relajante 60min',     60,  2800.00),
('Masaje de Piedras Calientes',90,  3500.00),
('Facial Hidratante',          45,  2200.00),
('Exfoliación Corporal',       60,  2500.00),
('Paquete Romántico (Pareja)', 120, 6800.00);

CREATE TABLE citas_spa (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    servicio_id   SMALLINT UNSIGNED NOT NULL,
    huesped_id    INT UNSIGNED NOT NULL,
    reserva_id    INT UNSIGNED,
    terapeuta_id  INT UNSIGNED,
    fecha_hora    DATETIME NOT NULL,
    estado        ENUM('agendada','confirmada','completada','cancelada','no_show') NOT NULL DEFAULT 'agendada',
    precio_cobrado DECIMAL(10,2),
    facturado     TINYINT(1) DEFAULT 0,
    notas         VARCHAR(255),
    FOREIGN KEY (servicio_id)  REFERENCES servicios_spa(id),
    FOREIGN KEY (huesped_id)   REFERENCES huespedes(id),
    FOREIGN KEY (reserva_id)   REFERENCES reservas(id),
    FOREIGN KEY (terapeuta_id) REFERENCES empleados(id)
);


-- ================================================================
-- ██ 15. INVENTARIO
-- ================================================================

CREATE TABLE categorias_inventario (
    id     SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL
);

INSERT INTO categorias_inventario (nombre) VALUES
('Lencería de Cama'),('Toallas'),('Amenidades Baño'),('Minibar'),
('Artículos de Limpieza'),('Papelería'),('Electrónicos'),('Mantenimiento');

CREATE TABLE inventario (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    categoria_id    SMALLINT UNSIGNED NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    unidad          VARCHAR(20) DEFAULT 'unidad',
    stock_actual    DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo    DECIMAL(10,2) NOT NULL DEFAULT 5,
    precio_costo    DECIMAL(10,2),
    proveedor       VARCHAR(100),
    activo          TINYINT(1) DEFAULT 1,
    FOREIGN KEY (categoria_id) REFERENCES categorias_inventario(id)
);

INSERT INTO inventario (categoria_id, nombre, unidad, stock_actual, stock_minimo, precio_costo) VALUES
(1,'Sábanas Queen',       'par', 80,  20, 850.00),
(1,'Sábanas King',        'par', 60,  15, 950.00),
(2,'Toallas de Baño',     'unid',200, 50, 320.00),
(2,'Toallas de Piscina',  'unid',120, 30, 380.00),
(3,'Shampoo (30ml)',      'unid',500,100,  25.00),
(3,'Jabón de Baño',       'unid',500,100,  18.00),
(4,'Agua Mineral 500ml',  'unid',300, 60,  55.00),
(4,'Snacks Variados',     'unid',200, 40,  80.00),
(5,'Desinfectante (1L)',  'botll', 50, 10, 280.00);

CREATE TABLE movimientos_inventario (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    item_id       INT UNSIGNED NOT NULL,
    tipo          ENUM('entrada','salida','ajuste') NOT NULL,
    cantidad      DECIMAL(10,2) NOT NULL,
    motivo        VARCHAR(200),
    empleado_id   INT UNSIGNED,
    referencia_id INT UNSIGNED,    -- reserva_id o pedido_id según contexto
    movido_en     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id)     REFERENCES inventario(id),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);


-- ================================================================
-- ██ 16. NOTIFICACIONES Y COMUNICACIONES
-- ================================================================

CREATE TABLE plantillas_notificacion (
    id       SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo   VARCHAR(40) NOT NULL UNIQUE,
    asunto   VARCHAR(150),
    cuerpo   TEXT NOT NULL,
    canal    ENUM('email','sms','sistema','whatsapp') NOT NULL DEFAULT 'email'
);

INSERT INTO plantillas_notificacion (codigo, asunto, cuerpo, canal) VALUES
('CONF_RESERVA','Confirmación de su reserva - Hotel Anacaona',
 'Estimado {nombre}, su reserva {codigo} para la habitación {habitacion} del {entrada} al {salida} ha sido CONFIRMADA. Total: RD$ {total}. ¡Le esperamos!','email'),
('RECUERDO_24H','Recordatorio: su llegada es mañana',
 'Estimado {nombre}, le recordamos que mañana {entrada} es su check-in en Hotel Anacaona. Código: {codigo}.','email'),
('CANCEL_RESERVA','Cancelación de reserva - Hotel Anacaona',
 'Estimado {nombre}, su reserva {codigo} ha sido cancelada. Si tiene dudas, contáctenos.','email'),
('CHECKOUT_MSG','Gracias por su visita',
 'Estimado {nombre}, gracias por hospedarse con nosotros. Su factura #{factura} está disponible.','email'),
('MANT_ASIGNADA','Orden de mantenimiento asignada',
 'Orden #{orden} asignada. Habitación: {habitacion}. Prioridad: {prioridad}.','sistema');

CREATE TABLE notificaciones (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plantilla_id   SMALLINT UNSIGNED,
    reserva_id     INT UNSIGNED,
    huesped_id     INT UNSIGNED,
    empleado_id    INT UNSIGNED,
    destinatario   VARCHAR(150),     -- email o teléfono
    asunto         VARCHAR(150),
    mensaje        TEXT NOT NULL,
    canal          ENUM('email','sms','sistema','whatsapp') NOT NULL DEFAULT 'email',
    estado         ENUM('pendiente','enviado','fallido') NOT NULL DEFAULT 'pendiente',
    intentos       TINYINT UNSIGNED DEFAULT 0,
    enviado_en     DATETIME,
    creado_en      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plantilla_id) REFERENCES plantillas_notificacion(id),
    FOREIGN KEY (reserva_id)   REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)   REFERENCES huespedes(id),
    FOREIGN KEY (empleado_id)  REFERENCES empleados(id),
    INDEX idx_estado (estado)
);


-- ================================================================
-- ██ 17. RESEÑAS Y SATISFACCIÓN
-- ================================================================

CREATE TABLE resenas (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reserva_id   INT UNSIGNED NOT NULL UNIQUE,
    huesped_id   INT UNSIGNED NOT NULL,
    puntaje_general   TINYINT UNSIGNED NOT NULL,    -- 1-10
    puntaje_limpieza  TINYINT UNSIGNED,
    puntaje_servicio  TINYINT UNSIGNED,
    puntaje_ubicacion TINYINT UNSIGNED,
    puntaje_comida    TINYINT UNSIGNED,
    comentario   TEXT,
    respuesta    TEXT,     -- respuesta del hotel
    respondido_por INT UNSIGNED,
    publicada    TINYINT(1) DEFAULT 1,
    fuente       VARCHAR(40) DEFAULT 'interna',    -- 'interna','booking','tripadvisor'
    creado_en    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reserva_id)      REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)      REFERENCES huespedes(id),
    FOREIGN KEY (respondido_por)  REFERENCES empleados(id),
    CHECK (puntaje_general BETWEEN 1 AND 10)
);

INSERT INTO resenas (reserva_id, huesped_id, puntaje_general, puntaje_limpieza, puntaje_servicio, comentario) VALUES
(5, 5, 9, 10, 9, 'Excelente estadía, el personal muy atento y la habitación impecable.');


-- ================================================================
-- ██ 18. PARKING
-- ================================================================

CREATE TABLE estacionamiento (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    numero       VARCHAR(10) NOT NULL UNIQUE,
    tipo         ENUM('auto','moto','bus','discapacitado') DEFAULT 'auto',
    disponible   TINYINT(1) DEFAULT 1
);

INSERT INTO estacionamiento (numero, tipo) VALUES
('P-01','auto'),('P-02','auto'),('P-03','auto'),('P-04','auto'),('P-05','auto'),
('P-06','auto'),('P-07','auto'),('P-08','auto'),('P-09','auto'),('P-10','auto'),
('P-D1','discapacitado'),('P-D2','discapacitado'),('M-01','moto'),('M-02','moto');

CREATE TABLE uso_parking (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    espacio_id      INT UNSIGNED NOT NULL,
    reserva_id      INT UNSIGNED,
    huesped_id      INT UNSIGNED,
    placa           VARCHAR(15) NOT NULL,
    marca_modelo    VARCHAR(60),
    entrada         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    salida          DATETIME,
    costo           DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (espacio_id)  REFERENCES estacionamiento(id),
    FOREIGN KEY (reserva_id)  REFERENCES reservas(id),
    FOREIGN KEY (huesped_id)  REFERENCES huespedes(id)
);


-- ================================================================
-- ██ 19. AUDITORÍA
-- ================================================================

CREATE TABLE auditoria (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tabla        VARCHAR(60) NOT NULL,
    operacion    ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    registro_id  INT UNSIGNED NOT NULL,
    datos_antes  JSON,
    datos_despues JSON,
    usuario_id   INT UNSIGNED,
    ip           VARCHAR(45),
    fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tabla (tabla),
    INDEX idx_fecha (fecha)
);


-- ================================================================
-- ██ 20. TRIGGERS
-- ================================================================

DELIMITER $$

-- T01: Código automático de reserva
CREATE TRIGGER trg_reserva_codigo_auto
BEFORE INSERT ON reservas FOR EACH ROW
BEGIN
    DECLARE next_num INT;
    IF NEW.codigo IS NULL OR NEW.codigo = '' THEN
        SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(codigo,'-',-1) AS UNSIGNED)),0)+1
        INTO next_num FROM reservas;
        SET NEW.codigo = CONCAT('RES-', YEAR(CURDATE()), '-', LPAD(next_num,6,'0'));
    END IF;
END$$

-- T02: Calcular precio total automáticamente
CREATE TRIGGER trg_calcular_precio_reserva
BEFORE INSERT ON reservas FOR EACH ROW
BEGIN
    DECLARE noches INT;
    DECLARE impuesto DECIMAL(5,2);
    SELECT impuesto_pct INTO impuesto FROM hotel LIMIT 1;
    SET noches = DATEDIFF(NEW.fecha_salida, NEW.fecha_entrada);
    IF noches < 1 THEN SET noches = 1; END IF;
    IF NEW.precio_noche > 0 AND NEW.precio_total = 0 THEN
        SET NEW.precio_total   = NEW.precio_noche * noches;
        SET NEW.impuesto_total = ROUND(NEW.precio_total * impuesto / 100, 2);
        SET NEW.deposito_req   = NEW.precio_noche;
    END IF;
END$$

-- T03: Validar disponibilidad de habitación
CREATE TRIGGER trg_validar_disponibilidad_hab
BEFORE INSERT ON reservas FOR EACH ROW
BEGIN
    DECLARE conflictos INT;
    SELECT COUNT(*) INTO conflictos FROM reservas
    WHERE habitacion_id = NEW.habitacion_id
      AND estado_id NOT IN (5,6)       -- excluir cancelada y no_show
      AND fecha_entrada  < NEW.fecha_salida
      AND fecha_salida   > NEW.fecha_entrada;
    IF conflictos > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La habitación no está disponible en esas fechas.';
    END IF;
END$$

-- T04: Cambiar estado habitación al hacer check-in
CREATE TRIGGER trg_checkin_ocupa_habitacion
AFTER INSERT ON check_ins FOR EACH ROW
BEGIN
    UPDATE habitaciones SET estado = 'ocupada' WHERE id = NEW.habitacion_id;
    UPDATE reservas SET estado_id = 3 WHERE id = NEW.reserva_id;  -- en_curso
END$$

-- T05: Cambiar estado habitación al hacer check-out
CREATE TRIGGER trg_checkout_libera_habitacion
AFTER INSERT ON check_outs FOR EACH ROW
BEGIN
    UPDATE habitaciones SET estado = 'limpieza', estado_limpieza = 'sucia'
    WHERE id = NEW.habitacion_id;
    UPDATE reservas SET estado_id = 4 WHERE id = NEW.reserva_id;  -- completada
    -- Crear asignación de limpieza post-checkout automáticamente
    INSERT INTO asignaciones_limpieza (habitacion_id, empleada_id, fecha, tipo)
    SELECT NEW.habitacion_id, e.id, CURDATE(), 'salida'
    FROM empleados e
    JOIN cargos c ON c.id = e.cargo_id
    WHERE c.departamento_id = 2 AND e.activo = 1
    LIMIT 1;
END$$

-- T06: Notificación al confirmar reserva
CREATE TRIGGER trg_notif_confirmacion
AFTER UPDATE ON reservas FOR EACH ROW
BEGIN
    IF NEW.estado_id = 2 AND OLD.estado_id = 1 THEN
        INSERT INTO notificaciones (reserva_id, huesped_id, asunto, mensaje, canal, destinatario)
        SELECT NEW.id, NEW.huesped_id,
               'Reserva Confirmada - Hotel Anacaona',
               CONCAT('Estimado/a ', h.nombre, ' ', h.apellido,
                      ', su reserva ', NEW.codigo,
                      ' del ', NEW.fecha_entrada, ' al ', NEW.fecha_salida,
                      ' ha sido CONFIRMADA. Total: RD$ ', NEW.precio_total, '. ¡Le esperamos!'),
               'email', h.email
        FROM huespedes h WHERE h.id = NEW.huesped_id;
    END IF;
    -- Notificación de cancelación
    IF NEW.estado_id = 5 AND OLD.estado_id != 5 THEN
        INSERT INTO notificaciones (reserva_id, huesped_id, asunto, mensaje, canal, destinatario)
        SELECT NEW.id, NEW.huesped_id,
               'Cancelación de Reserva - Hotel Anacaona',
               CONCAT('Su reserva ', NEW.codigo, ' ha sido cancelada.'),
               'email', h.email
        FROM huespedes h WHERE h.id = NEW.huesped_id;
    END IF;
END$$

-- T07: Registrar historial en auditoría al cambiar estado reserva
CREATE TRIGGER trg_auditoria_reservas
AFTER UPDATE ON reservas FOR EACH ROW
BEGIN
    IF NEW.estado_id != OLD.estado_id THEN
        INSERT INTO auditoria (tabla, operacion, registro_id, datos_antes, datos_despues)
        VALUES ('reservas', 'UPDATE', NEW.id,
            JSON_OBJECT('estado_id', OLD.estado_id, 'precio_total', OLD.precio_total),
            JSON_OBJECT('estado_id', NEW.estado_id, 'precio_total', NEW.precio_total));
    END IF;
END$$

-- T08: Actualizar total pedido restaurante al agregar items
CREATE TRIGGER trg_actualizar_total_pedido
AFTER INSERT ON items_pedido FOR EACH ROW
BEGIN
    UPDATE pedidos_restaurante
    SET total = (SELECT SUM(subtotal) FROM items_pedido WHERE pedido_id = NEW.pedido_id)
    WHERE id = NEW.pedido_id;
END$$

-- T09: Alerta stock mínimo de inventario
CREATE TRIGGER trg_alerta_stock_minimo
AFTER UPDATE ON inventario FOR EACH ROW
BEGIN
    IF NEW.stock_actual <= NEW.stock_minimo AND OLD.stock_actual > OLD.stock_minimo THEN
        INSERT INTO notificaciones (asunto, mensaje, canal)
        VALUES (
            CONCAT('⚠ Stock bajo: ', NEW.nombre),
            CONCAT('El artículo "', NEW.nombre, '" tiene stock actual de ',
                   NEW.stock_actual, ' unidades, por debajo del mínimo (', NEW.stock_minimo, ').'),
            'sistema'
        );
    END IF;
END$$

-- T10: Marcar habitación en mantenimiento al abrir orden urgente
CREATE TRIGGER trg_mantenimiento_bloquea_hab
AFTER INSERT ON ordenes_mantenimiento FOR EACH ROW
BEGIN
    IF NEW.prioridad IN ('alta','critica') AND NEW.habitacion_id IS NOT NULL THEN
        UPDATE habitaciones SET estado = 'mantenimiento' WHERE id = NEW.habitacion_id;
    END IF;
END$$

DELIMITER ;


-- ================================================================
-- ██ 21. PROCEDIMIENTOS ALMACENADOS
-- ================================================================

DELIMITER $$

-- ── CREAR RESERVA COMPLETA ──────────────────────────────────
CREATE PROCEDURE sp_crear_reserva(
    IN p_huesped_id    INT UNSIGNED,
    IN p_habitacion_id SMALLINT UNSIGNED,
    IN p_canal_id      TINYINT UNSIGNED,
    IN p_entrada       DATE,
    IN p_salida        DATE,
    IN p_adultos       TINYINT UNSIGNED,
    IN p_ninos         TINYINT UNSIGNED,
    IN p_desayuno      TINYINT(1),
    IN p_notas         TEXT,
    OUT p_reserva_id   INT UNSIGNED,
    OUT p_codigo       VARCHAR(20),
    OUT p_total        DECIMAL(10,2)
)
BEGIN
    DECLARE v_precio    DECIMAL(10,2);
    DECLARE v_cap       TINYINT UNSIGNED;
    DECLARE v_noches    INT;
    DECLARE v_impuesto  DECIMAL(5,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT th.precio_base, th.capacidad_max
    INTO v_precio, v_cap
    FROM habitaciones h JOIN tipos_habitacion th ON th.id = h.tipo_id
    WHERE h.id = p_habitacion_id AND h.activa = 1 AND h.estado = 'disponible';

    IF v_precio IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Habitación no disponible o no existe.';
    END IF;

    IF (p_adultos + p_ninos) > v_cap THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El número de personas supera la capacidad.';
    END IF;

    SELECT impuesto_pct INTO v_impuesto FROM hotel LIMIT 1;
    SET v_noches = DATEDIFF(p_salida, p_entrada);
    IF v_noches < 1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Las fechas son inválidas.'; END IF;

    SET v_precio = v_precio + IF(p_desayuno, 650.00, 0.00);

    INSERT INTO reservas (
        huesped_id, habitacion_id, canal_id, estado_id,
        fecha_entrada, fecha_salida,
        num_adultos, num_ninos,
        precio_noche, precio_total, impuesto_total, deposito_req,
        incluye_desayuno, notas_huesped
    ) VALUES (
        p_huesped_id, p_habitacion_id, p_canal_id, 1,
        p_entrada, p_salida,
        p_adultos, p_ninos,
        v_precio,
        ROUND(v_precio * v_noches, 2),
        ROUND(v_precio * v_noches * v_impuesto / 100, 2),
        v_precio,
        p_desayuno, p_notas
    );

    SET p_reserva_id = LAST_INSERT_ID();
    SELECT codigo, precio_total INTO p_codigo, p_total FROM reservas WHERE id = p_reserva_id;

    -- Confirmar automáticamente si canal es directo (1) o teléfono (2)
    IF p_canal_id IN (1,2) THEN
        UPDATE reservas SET estado_id = 2 WHERE id = p_reserva_id;
    END IF;

    COMMIT;
END$$


-- ── HACER CHECK-IN ──────────────────────────────────────────
CREATE PROCEDURE sp_check_in(
    IN p_reserva_id INT UNSIGNED,
    IN p_staff_id   INT UNSIGNED
)
BEGIN
    DECLARE v_hab SMALLINT UNSIGNED;
    DECLARE v_hue INT UNSIGNED;
    DECLARE v_est TINYINT UNSIGNED;

    SELECT habitacion_id, huesped_id, estado_id INTO v_hab, v_hue, v_est
    FROM reservas WHERE id = p_reserva_id;

    IF v_est != 2 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La reserva debe estar confirmada para hacer check-in.';
    END IF;

    INSERT INTO check_ins (reserva_id, huesped_id, habitacion_id, staff_id)
    VALUES (p_reserva_id, v_hue, v_hab, p_staff_id);

    SELECT 'Check-in realizado' AS resultado, p_reserva_id AS reserva_id;
END$$


-- ── HACER CHECK-OUT ─────────────────────────────────────────
CREATE PROCEDURE sp_check_out(
    IN  p_reserva_id   INT UNSIGNED,
    IN  p_staff_id     INT UNSIGNED,
    IN  p_cargo_extra  DECIMAL(10,2),
    IN  p_satisfaccion TINYINT UNSIGNED,
    OUT p_factura_id   INT UNSIGNED
)
BEGIN
    DECLARE v_hab     SMALLINT UNSIGNED;
    DECLARE v_hue     INT UNSIGNED;
    DECLARE v_total   DECIMAL(10,2);
    DECLARE v_imp     DECIMAL(10,2);
    DECLARE v_num_fac VARCHAR(20);

    SELECT habitacion_id, huesped_id, precio_total, impuesto_total
    INTO v_hab, v_hue, v_total, v_imp
    FROM reservas WHERE id = p_reserva_id AND estado_id = 3;

    IF v_hab IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay check-in activo para esta reserva.';
    END IF;

    INSERT INTO check_outs (reserva_id, huesped_id, habitacion_id, staff_id, cargo_extra, satisfaccion)
    VALUES (p_reserva_id, v_hue, v_hab, p_staff_id, IFNULL(p_cargo_extra,0), p_satisfaccion);

    -- Generar factura
    SET v_num_fac = CONCAT('FAC-', YEAR(CURDATE()), '-', LPAD(
        (SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(numero,'-',-1) AS UNSIGNED)),0)+1 FROM facturas),6,'0'));

    INSERT INTO facturas (numero, reserva_id, huesped_id, subtotal, impuesto, total, estado, creado_por)
    VALUES (v_num_fac, p_reserva_id, v_hue,
            v_total + IFNULL(p_cargo_extra,0),
            v_imp,
            v_total + IFNULL(p_cargo_extra,0) + v_imp,
            'emitida', p_staff_id);

    SET p_factura_id = LAST_INSERT_ID();
    SELECT 'Check-out realizado' AS resultado, v_num_fac AS numero_factura, p_factura_id AS factura_id;
END$$


-- ── DISPONIBILIDAD DE HABITACIONES ─────────────────────────
CREATE PROCEDURE sp_disponibilidad(
    IN p_entrada DATE,
    IN p_salida  DATE,
    IN p_adultos TINYINT UNSIGNED,
    IN p_tipo_id TINYINT UNSIGNED     -- NULL = todos los tipos
)
BEGIN
    SELECT
        h.id, h.numero, h.piso,
        th.nombre AS tipo, th.descripcion,
        th.capacidad_max, th.camas, th.area_m2,
        th.precio_base,
        ROUND(th.precio_base * DATEDIFF(p_salida, p_entrada), 2) AS total_estadia,
        h.accesible
    FROM habitaciones h
    JOIN tipos_habitacion th ON th.id = h.tipo_id
    WHERE h.activa = 1
      AND h.estado = 'disponible'
      AND th.capacidad_max >= p_adultos
      AND (p_tipo_id IS NULL OR th.id = p_tipo_id)
      AND h.id NOT IN (
          SELECT habitacion_id FROM reservas
          WHERE estado_id NOT IN (5,6)
            AND fecha_entrada  < p_salida
            AND fecha_salida   > p_entrada
      )
    ORDER BY th.precio_base;
END$$


-- ── CANCELAR RESERVA ────────────────────────────────────────
CREATE PROCEDURE sp_cancelar_reserva(
    IN p_reserva_id INT UNSIGNED,
    IN p_usuario_id INT UNSIGNED,
    IN p_motivo     VARCHAR(255)
)
BEGIN
    UPDATE reservas
    SET estado_id = 5,
        notas_internas = CONCAT(IFNULL(notas_internas,''), ' | CANCELACIÓN: ', p_motivo)
    WHERE id = p_reserva_id AND estado_id IN (1,2);
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede cancelar: estado no permite cancelación.';
    END IF;
END$$


-- ── DASHBOARD KPIs ──────────────────────────────────────────
CREATE PROCEDURE sp_dashboard_kpis(IN p_fecha DATE)
BEGIN
    -- KPIs generales
    SELECT
        (SELECT COUNT(*) FROM habitaciones WHERE activa=1)             AS total_habitaciones,
        (SELECT COUNT(*) FROM habitaciones WHERE estado='disponible')  AS disponibles,
        (SELECT COUNT(*) FROM habitaciones WHERE estado='ocupada')     AS ocupadas,
        (SELECT COUNT(*) FROM habitaciones WHERE estado='mantenimiento') AS en_mantenimiento,
        ROUND((SELECT COUNT(*) FROM habitaciones WHERE estado='ocupada') /
              NULLIF((SELECT COUNT(*) FROM habitaciones WHERE activa=1),0)*100,1) AS ocupacion_pct,
        (SELECT COUNT(*) FROM reservas WHERE fecha_entrada = p_fecha AND estado_id IN (1,2)) AS llegadas_hoy,
        (SELECT COUNT(*) FROM reservas WHERE fecha_salida  = p_fecha AND estado_id IN (3,4)) AS salidas_hoy,
        (SELECT COUNT(*) FROM reservas WHERE estado_id = 3)            AS en_casa,
        (SELECT COALESCE(SUM(total),0) FROM facturas
         WHERE DATE(creado_en) = p_fecha AND estado != 'anulada')      AS ingresos_hoy,
        (SELECT COALESCE(SUM(total),0) FROM facturas
         WHERE MONTH(creado_en) = MONTH(p_fecha)
           AND YEAR(creado_en)  = YEAR(p_fecha)
           AND estado != 'anulada')                                    AS ingresos_mes,
        (SELECT COUNT(*) FROM ordenes_mantenimiento WHERE estado='abierta') AS mant_abiertos,
        (SELECT COUNT(*) FROM notificaciones WHERE estado='pendiente') AS notif_pendientes;
END$$

DELIMITER ;


-- ================================================================
-- ██ 22. VISTAS PARA DASHBOARD Y REPORTES
-- ================================================================

-- Vista maestra de reservas
CREATE OR REPLACE VIEW v_reservas AS
SELECT
    r.id, r.codigo,
    CONCAT(hu.nombre,' ',hu.apellido) AS huesped,
    hu.email, hu.telefono, hu.pais_id  AS pais,
    h.numero AS habitacion, th.nombre AS tipo_habitacion,
    h.piso, er.nombre AS estado, er.color AS estado_color,
    c.nombre AS canal,
    r.fecha_entrada, r.fecha_salida,
    DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
    r.num_adultos, r.num_ninos,
    r.precio_noche, r.precio_total, r.impuesto_total,
    ROUND(r.precio_total + r.impuesto_total - r.descuento_monto, 2) AS total_con_impuesto,
    r.deposito_req, r.deposito_pagado,
    ROUND(r.precio_total + r.impuesto_total - r.descuento_monto - r.deposito_pagado, 2) AS saldo_pendiente,
    r.incluye_desayuno, r.incluye_cena,
    r.notas_huesped, r.creado_en
FROM reservas r
JOIN huespedes       hu ON hu.id = r.huesped_id
JOIN habitaciones    h  ON h.id  = r.habitacion_id
JOIN tipos_habitacion th ON th.id = h.tipo_id
JOIN estados_reserva er ON er.id = r.estado_id
JOIN canales          c ON c.id  = r.canal_id;


-- Ocupación diaria (últimos 90 días + próximos 30)
CREATE OR REPLACE VIEW v_ocupacion_diaria AS
SELECT
    d.fecha,
    COUNT(r.id)   AS reservas_activas,
    SUM(CASE WHEN er.nombre='en_curso'   THEN 1 ELSE 0 END) AS en_casa,
    SUM(CASE WHEN er.nombre='confirmada' THEN 1 ELSE 0 END) AS confirmadas,
    (SELECT COUNT(*) FROM habitaciones WHERE activa=1)       AS total_habitaciones,
    ROUND(COUNT(r.id)/(SELECT COUNT(*) FROM habitaciones WHERE activa=1)*100,1) AS pct_ocupacion
FROM (
    SELECT DATE(NOW()) - INTERVAL n DAY AS fecha
    FROM (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
          UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14
          UNION SELECT 15 UNION SELECT 20 UNION SELECT 25 UNION SELECT 30
    ) nums
) d
LEFT JOIN reservas r ON r.fecha_entrada <= d.fecha AND r.fecha_salida > d.fecha
    AND r.estado_id NOT IN (5,6)
LEFT JOIN estados_reserva er ON er.id = r.estado_id
GROUP BY d.fecha ORDER BY d.fecha;


-- Ingresos por mes
CREATE OR REPLACE VIEW v_ingresos_por_mes AS
SELECT
    DATE_FORMAT(creado_en,'%Y-%m')     AS mes,
    COUNT(*)                            AS facturas,
    SUM(CASE WHEN estado!='anulada' THEN subtotal  ELSE 0 END) AS subtotal,
    SUM(CASE WHEN estado!='anulada' THEN impuesto  ELSE 0 END) AS impuesto,
    SUM(CASE WHEN estado!='anulada' THEN total     ELSE 0 END) AS total,
    SUM(CASE WHEN estado='anulada'  THEN 1         ELSE 0 END) AS anuladas
FROM facturas
WHERE creado_en >= NOW() - INTERVAL 12 MONTH
GROUP BY mes ORDER BY mes;


-- Rendimiento por tipo de habitación
CREATE OR REPLACE VIEW v_revpar AS
SELECT
    th.nombre                                      AS tipo,
    COUNT(DISTINCT h.id)                           AS habitaciones,
    COUNT(r.id)                                    AS reservas,
    COALESCE(SUM(r.precio_total),0)               AS ingresos_totales,
    ROUND(AVG(r.precio_noche),2)                   AS adr,          -- tarifa promedio diaria
    ROUND(COALESCE(SUM(r.precio_total),0)/
          NULLIF(COUNT(DISTINCT h.id),0),2)        AS revpar        -- ingreso por habitación disponible
FROM tipos_habitacion th
JOIN habitaciones h ON h.tipo_id = th.id AND h.activa = 1
LEFT JOIN reservas r ON r.habitacion_id = h.id AND r.estado_id NOT IN (5,6)
GROUP BY th.id, th.nombre;


-- Huéspedes frecuentes
CREATE OR REPLACE VIEW v_huespedes_frecuentes AS
SELECT
    hu.id, CONCAT(hu.nombre,' ',hu.apellido) AS huesped,
    hu.email, hu.pais_id, hu.nivel_vip,
    COUNT(r.id)                    AS total_estancias,
    COALESCE(SUM(r.precio_total),0) AS gasto_total,
    MAX(r.fecha_entrada)           AS ultima_visita,
    ROUND(AVG(DATEDIFF(r.fecha_salida, r.fecha_entrada)),1) AS noches_promedio
FROM huespedes hu
LEFT JOIN reservas r ON r.huesped_id = hu.id AND r.estado_id NOT IN (5,6)
GROUP BY hu.id ORDER BY total_estancias DESC;


-- Vista de housekeeping diario
CREATE OR REPLACE VIEW v_housekeeping_hoy AS
SELECT
    h.numero, h.piso, h.estado, h.estado_limpieza,
    th.nombre AS tipo,
    al.tipo   AS tarea, al.estado AS tarea_estado,
    CONCAT(e.nombre,' ',e.apellido) AS asignada_a,
    al.hora_inicio, al.hora_fin
FROM habitaciones h
JOIN tipos_habitacion th ON th.id = h.tipo_id
LEFT JOIN asignaciones_limpieza al ON al.habitacion_id = h.id AND al.fecha = CURDATE()
LEFT JOIN empleados e ON e.id = al.empleada_id
ORDER BY h.piso, h.numero;


-- Mantenimiento pendiente
CREATE OR REPLACE VIEW v_mantenimiento_pendiente AS
SELECT
    om.id, h.numero AS habitacion, om.area,
    om.tipo, om.prioridad, om.descripcion,
    CONCAT(e1.nombre,' ',e1.apellido) AS reportado_por,
    CONCAT(e2.nombre,' ',e2.apellido) AS asignado_a,
    om.estado, om.fecha_reporte,
    TIMESTAMPDIFF(HOUR, om.fecha_reporte, NOW()) AS horas_abierta
FROM ordenes_mantenimiento om
LEFT JOIN habitaciones h  ON h.id  = om.habitacion_id
LEFT JOIN empleados    e1 ON e1.id = om.reportado_por
LEFT JOIN empleados    e2 ON e2.id = om.asignado_a
WHERE om.estado IN ('abierta','en_proceso')
ORDER BY FIELD(om.prioridad,'critica','alta','media','baja'), om.fecha_reporte;


-- Reporte de canales de distribución
CREATE OR REPLACE VIEW v_canales_rendimiento AS
SELECT
    c.nombre AS canal,
    COUNT(r.id)                        AS reservas,
    COALESCE(SUM(r.precio_total),0)   AS ingresos_brutos,
    ROUND(c.comision,2)               AS comision_pct,
    ROUND(COALESCE(SUM(r.precio_total),0) * (1 - c.comision/100),2) AS ingresos_netos,
    ROUND(AVG(DATEDIFF(r.fecha_salida,r.fecha_entrada)),1) AS noches_promedio
FROM canales c
LEFT JOIN reservas r ON r.canal_id = c.id AND r.estado_id NOT IN (5,6)
GROUP BY c.id, c.nombre, c.comision
ORDER BY reservas DESC;


-- Próximas llegadas y salidas (7 días)
CREATE OR REPLACE VIEW v_agenda_7dias AS
SELECT
    'LLEGADA' AS tipo_evento,
    r.codigo, CONCAT(hu.nombre,' ',hu.apellido) AS huesped,
    hu.telefono, h.numero AS habitacion, r.fecha_entrada AS fecha,
    r.num_adultos + r.num_ninos AS personas,
    er.nombre AS estado
FROM reservas r
JOIN huespedes hu ON hu.id = r.huesped_id
JOIN habitaciones h ON h.id = r.habitacion_id
JOIN estados_reserva er ON er.id = r.estado_id
WHERE r.fecha_entrada BETWEEN CURDATE() AND CURDATE() + INTERVAL 7 DAY
  AND r.estado_id IN (1,2)
UNION ALL
SELECT
    'SALIDA', r.codigo, CONCAT(hu.nombre,' ',hu.apellido),
    hu.telefono, h.numero, r.fecha_salida,
    r.num_adultos + r.num_ninos, er.nombre
FROM reservas r
JOIN huespedes hu ON hu.id = r.huesped_id
JOIN habitaciones h ON h.id = r.habitacion_id
JOIN estados_reserva er ON er.id = r.estado_id
WHERE r.fecha_salida BETWEEN CURDATE() AND CURDATE() + INTERVAL 7 DAY
  AND r.estado_id = 3
ORDER BY fecha, tipo_evento;


-- ================================================================
-- ██ 23. EVENTOS PROGRAMADOS
-- ================================================================

SET GLOBAL event_scheduler = ON;

DELIMITER $$

-- Recordatorio 24 horas antes de cada llegada
CREATE EVENT IF NOT EXISTS evt_recordatorio_llegada
ON SCHEDULE EVERY 1 HOUR DO
BEGIN
    INSERT INTO notificaciones (reserva_id, huesped_id, asunto, mensaje, canal, destinatario)
    SELECT r.id, r.huesped_id,
           'Su llegada es mañana - Hotel Anacaona',
           CONCAT('Estimado/a ', h.nombre, ', mañana ', r.fecha_entrada,
                  ' es su check-in. Código: ', r.codigo, '. Hora: 15:00. ¡Le esperamos!'),
           'email', h.email
    FROM reservas r
    JOIN huespedes h ON h.id = r.huesped_id
    WHERE r.estado_id = 2
      AND r.fecha_entrada = DATE(NOW() + INTERVAL 1 DAY)
      AND r.id NOT IN (
          SELECT reserva_id FROM notificaciones
          WHERE asunto LIKE 'Su llegada es mañana%'
            AND creado_en > NOW() - INTERVAL 2 HOUR
      );
END$$

-- Auto-marcar no-show a las 23:59 del día de llegada
CREATE EVENT IF NOT EXISTS evt_marcar_no_show
ON SCHEDULE EVERY 1 HOUR DO
BEGIN
    UPDATE reservas SET estado_id = 6
    WHERE estado_id = 2
      AND fecha_entrada < CURDATE()
      AND id NOT IN (SELECT reserva_id FROM check_ins);
END$$

-- Cerrar facturas vencidas (+30 días sin pago)
CREATE EVENT IF NOT EXISTS evt_facturas_vencidas
ON SCHEDULE EVERY 1 DAY STARTS (CURDATE() + INTERVAL 1 DAY + INTERVAL 2 HOUR)
DO
BEGIN
    UPDATE facturas SET estado = 'vencida'
    WHERE estado = 'emitida'
      AND creado_en < NOW() - INTERVAL 30 DAY;
END$$

DELIMITER ;


-- ================================================================
-- ██ 24. ÍNDICES ADICIONALES DE RENDIMIENTO
-- ================================================================

CREATE INDEX idx_reservas_rango   ON reservas (fecha_entrada, fecha_salida, estado_id);
CREATE INDEX idx_facturas_fecha   ON facturas  (DATE(creado_en), estado);
CREATE INDEX idx_notif_pendiente  ON notificaciones (estado, creado_en);
CREATE INDEX idx_huesped_doc      ON huespedes (tipo_documento, num_documento);
CREATE INDEX idx_mant_prioridad   ON ordenes_mantenimiento (prioridad, estado);


-- ================================================================
-- FIN DEL SCRIPT  |  hotel_reservas
-- ================================================================
-- Ejemplos de uso:
--
-- CALL sp_disponibilidad('2025-03-01', '2025-03-05', 2, NULL);
--
-- CALL sp_crear_reserva(1, 9, 1, '2025-03-01', '2025-03-04', 2, 0, 1, 'Vista piscina preferida',
--                       @rid, @cod, @total);
-- SELECT @rid, @cod, @total;
--
-- CALL sp_check_in(@rid, 2);
-- CALL sp_check_out(@rid, 2, 0.00, 9, @fid);
-- SELECT @fid;
--
-- CALL sp_dashboard_kpis(CURDATE());
-- SELECT * FROM v_reservas;
-- SELECT * FROM v_agenda_7dias;
-- SELECT * FROM v_housekeeping_hoy;
-- SELECT * FROM v_mantenimiento_pendiente;
-- SELECT * FROM v_ingresos_por_mes;
-- SELECT * FROM v_revpar;
-- SELECT * FROM v_huespedes_frecuentes;
-- ================================================================

SET FOREIGN_KEY_CHECKS = 1;
