from app.extensions import db


class EstadoReserva(db.Model):
    __tablename__ = 'estados_reserva'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(7))

    reservas = db.relationship('Reserva', backref='estado', lazy='dynamic')

    def __repr__(self):
        return f'<EstadoReserva {self.nombre}>'


class Reserva(db.Model):
    __tablename__ = 'reservas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(14), nullable=False, unique=True)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    canal_id = db.Column(db.SmallInteger, db.ForeignKey('canales.id'), nullable=False, default=1)
    tarifa_id = db.Column(db.Integer, db.ForeignKey('tarifas_especiales.id'))
    estado_id = db.Column(db.SmallInteger, db.ForeignKey('estados_reserva.id'), nullable=False, default=1)
    fecha_entrada = db.Column(db.Date, nullable=False)
    fecha_salida = db.Column(db.Date, nullable=False)
    hora_llegada_est = db.Column(db.Time)
    num_adultos = db.Column(db.SmallInteger, nullable=False, default=1)
    num_ninos = db.Column(db.SmallInteger, nullable=False, default=0)
    precio_noche = db.Column(db.Numeric(10, 2), nullable=False)
    precio_total = db.Column(db.Numeric(10, 2), nullable=False)
    impuesto_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    descuento_monto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    deposito_req = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    deposito_pagado = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    incluye_desayuno = db.Column(db.Boolean, default=False)
    incluye_almuerzo = db.Column(db.Boolean, default=False)
    incluye_cena = db.Column(db.Boolean, default=False)
    codigo_externo = db.Column(db.String(60))
    notas_huesped = db.Column(db.Text)
    notas_internas = db.Column(db.Text)
    staff_creador_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())
    actualizado_en = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relaciones
    tarifa = db.relationship('TarifaEspecial', backref='reservas', lazy='joined')
    solicitudes = db.relationship('SolicitudEspecial', backref='reserva', lazy='dynamic',
                                  cascade='all, delete-orphan')
    huespedes_adicionales = db.relationship('ReservaHuespedAdicional', backref='reserva',
                                            lazy='dynamic', cascade='all, delete-orphan')
    check_in = db.relationship('CheckIn', backref='reserva', uselist=False, lazy='joined')
    check_out = db.relationship('CheckOut', backref='reserva', uselist=False, lazy='joined')
    facturas = db.relationship('Factura', backref='reserva', lazy='dynamic')
    cargos = db.relationship('CargoHabitacion', backref='reserva', lazy='dynamic')
    resena = db.relationship('Resena', backref='reserva', uselist=False, lazy='joined')

    @property
    def noches(self):
        if self.fecha_salida and self.fecha_entrada:
            return (self.fecha_salida - self.fecha_entrada).days
        return 0

    @property
    def total_con_impuesto(self):
        return float(self.precio_total or 0) + float(self.impuesto_total or 0) - float(self.descuento_monto or 0)

    @property
    def saldo_pendiente(self):
        return self.total_con_impuesto - float(self.deposito_pagado or 0)

    def __repr__(self):
        return f'<Reserva {self.codigo}>'


class ReservaHuespedAdicional(db.Model):
    __tablename__ = 'reserva_huespedes_adicionales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id', ondelete='CASCADE'), nullable=False)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    es_titular = db.Column(db.Boolean, default=False)

    huesped = db.relationship('Huesped', lazy='joined')


class SolicitudEspecial(db.Model):
    __tablename__ = 'solicitudes_especiales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(
        db.Enum('cama_extra', 'cuna', 'almohada_especial', 'dieta', 'decoracion',
                'traslado', 'early_checkin', 'late_checkout', 'accesibilidad', 'otro',
                name='tipo_solicitud_enum'),
        nullable=False
    )
    descripcion = db.Column(db.String(255))
    atendida = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<SolicitudEspecial {self.tipo}>'
