from app.extensions import db


class ServicioSpa(db.Model):
    __tablename__ = 'servicios_spa'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    duracion_min = db.Column(db.SmallInteger, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    disponible = db.Column(db.Boolean, default=True)

    citas = db.relationship('CitaSpa', backref='servicio', lazy='dynamic')

    def __repr__(self):
        return f'<ServicioSpa {self.nombre}>'


class CitaSpa(db.Model):
    __tablename__ = 'citas_spa'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    servicio_id = db.Column(db.SmallInteger, db.ForeignKey('servicios_spa.id'), nullable=False)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    fecha_hora = db.Column(db.DateTime, nullable=False)
    estado = db.Column(
        db.Enum('agendada', 'confirmada', 'completada', 'cancelada', 'no_show',
                name='estado_cita_spa_enum'),
        nullable=False, default='agendada'
    )
    precio_cobrado = db.Column(db.Numeric(10, 2))
    facturado = db.Column(db.Boolean, default=False)
    notas = db.Column(db.String(255))

    huesped = db.relationship('Huesped', backref='citas_spa', lazy='joined')
    reserva = db.relationship('Reserva', backref='citas_spa', lazy='joined')
    terapeuta = db.relationship('Empleado', backref='citas_spa', lazy='joined')

    def __repr__(self):
        return f'<CitaSpa {self.servicio_id} {self.fecha_hora}>'
