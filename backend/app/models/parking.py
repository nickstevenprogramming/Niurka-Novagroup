from app.extensions import db


class Estacionamiento(db.Model):
    __tablename__ = 'estacionamiento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    tipo = db.Column(
        db.Enum('auto', 'moto', 'bus', 'discapacitado', name='tipo_parking_enum'),
        default='auto'
    )
    disponible = db.Column(db.Boolean, default=True)

    usos = db.relationship('UsoParking', backref='espacio', lazy='dynamic')

    def __repr__(self):
        return f'<Estacionamiento {self.numero}>'


class UsoParking(db.Model):
    __tablename__ = 'uso_parking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    espacio_id = db.Column(db.Integer, db.ForeignKey('estacionamiento.id'), nullable=False)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'))
    placa = db.Column(db.String(15), nullable=False)
    marca_modelo = db.Column(db.String(60))
    entrada = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    salida = db.Column(db.DateTime)
    costo = db.Column(db.Numeric(10, 2), default=0.00)

    reserva = db.relationship('Reserva', backref='uso_parking', lazy='joined')
    huesped = db.relationship('Huesped', backref='uso_parking', lazy='joined')

    def __repr__(self):
        return f'<UsoParking {self.placa}>'
