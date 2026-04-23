from app.extensions import db


class CheckIn(db.Model):
    __tablename__ = 'check_ins'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False, unique=True)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    fecha_hora = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    llave_entregada = db.Column(db.Boolean, default=True)
    num_llaves = db.Column(db.SmallInteger, default=1)
    observaciones = db.Column(db.Text)

    huesped = db.relationship('Huesped', lazy='joined')
    habitacion = db.relationship('Habitacion', lazy='joined')
    staff = db.relationship('Empleado', lazy='joined')

    def __repr__(self):
        return f'<CheckIn reserva={self.reserva_id}>'


class CheckOut(db.Model):
    __tablename__ = 'check_outs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False, unique=True)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    fecha_hora = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    llaves_devueltas = db.Column(db.SmallInteger, default=1)
    cargo_extra = db.Column(db.Numeric(10, 2), default=0.00)
    motivo_cargo = db.Column(db.String(200))
    satisfaccion = db.Column(db.SmallInteger)

    huesped = db.relationship('Huesped', lazy='joined')
    habitacion = db.relationship('Habitacion', lazy='joined')
    staff = db.relationship('Empleado', lazy='joined')

    def __repr__(self):
        return f'<CheckOut reserva={self.reserva_id}>'
