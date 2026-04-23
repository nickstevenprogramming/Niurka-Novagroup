from app.extensions import db


class Resena(db.Model):
    __tablename__ = 'resenas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False, unique=True)
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'), nullable=False)
    puntaje_general = db.Column(db.SmallInteger, nullable=False)
    puntaje_limpieza = db.Column(db.SmallInteger)
    puntaje_servicio = db.Column(db.SmallInteger)
    puntaje_ubicacion = db.Column(db.SmallInteger)
    puntaje_comida = db.Column(db.SmallInteger)
    comentario = db.Column(db.Text)
    respuesta = db.Column(db.Text)
    respondido_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    publicada = db.Column(db.Boolean, default=True)
    fuente = db.Column(db.String(40), default='interna')
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    respondedor = db.relationship('Empleado', backref='respuestas_resenas', lazy='joined')

    def __repr__(self):
        return f'<Resena {self.puntaje_general}/10>'
