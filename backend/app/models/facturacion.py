from app.extensions import db


class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<MetodoPago {self.nombre}>'


class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(20), nullable=False, unique=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False, server_default=db.func.current_date())
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    impuesto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    descuento = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(
        db.Enum('borrador', 'emitida', 'pagada', 'anulada', 'vencida',
                name='estado_factura_enum'),
        nullable=False, default='borrador'
    )
    tipo = db.Column(
        db.Enum('hospedaje', 'restaurante', 'spa', 'mixta', 'otro',
                name='tipo_factura_enum'),
        nullable=False, default='hospedaje'
    )
    notas = db.Column(db.Text)
    creado_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    # Relaciones
    huesped = db.relationship('Huesped', backref='facturas', lazy='joined')
    items = db.relationship('ItemFactura', backref='factura', lazy='joined',
                            cascade='all, delete-orphan')
    pagos = db.relationship('Pago', backref='factura', lazy='dynamic')
    creador = db.relationship('Empleado', backref='facturas_creadas', lazy='joined')

    @property
    def total_pagado(self):
        return sum(float(p.monto) for p in self.pagos)

    @property
    def saldo(self):
        return float(self.total or 0) - self.total_pagado

    def __repr__(self):
        return f'<Factura {self.numero}>'


class ItemFactura(db.Model):
    __tablename__ = 'items_factura'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.Numeric(8, 2), nullable=False, default=1)
    precio_unit = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(
        db.Enum('noche', 'desayuno', 'almuerzo', 'cena', 'minibar', 'telefono',
                'lavanderia', 'spa', 'parking', 'otro',
                name='tipo_item_factura_enum'),
        nullable=False, default='noche'
    )


class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    metodo_id = db.Column(db.SmallInteger, db.ForeignKey('metodos_pago.id'), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    referencia = db.Column(db.String(80))
    moneda = db.Column(db.String(3), default='DOP')
    tasa_cambio = db.Column(db.Numeric(10, 4), default=1.0000)
    monto_usd = db.Column(db.Numeric(10, 2))
    es_deposito = db.Column(db.Boolean, default=False)
    pagado_en = db.Column(db.DateTime, server_default=db.func.now())
    registrado_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    notas = db.Column(db.String(255))

    metodo = db.relationship('MetodoPago', backref='pagos', lazy='joined')
    registrador = db.relationship('Empleado', backref='pagos_registrados', lazy='joined')

    def __repr__(self):
        return f'<Pago {self.monto} {self.moneda}>'


class CargoHabitacion(db.Model):
    __tablename__ = 'cargos_habitacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    tipo = db.Column(
        db.Enum('minibar', 'room_service', 'telefono', 'lavanderia', 'spa',
                'parking', 'danio', 'otro',
                name='tipo_cargo_habitacion_enum'),
        nullable=False
    )
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    facturado = db.Column(db.Boolean, default=False)
    registrado_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    registrado_en = db.Column(db.DateTime, server_default=db.func.now())

    habitacion = db.relationship('Habitacion', backref='cargos', lazy='joined')
    registrador = db.relationship('Empleado', lazy='joined')

    def __repr__(self):
        return f'<CargoHabitacion {self.tipo} {self.monto}>'
