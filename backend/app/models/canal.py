from app.extensions import db


class Canal(db.Model):
    __tablename__ = 'canales'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    comision = db.Column(db.Numeric(5, 2), default=0.00)
    activo = db.Column(db.Boolean, default=True)

    reservas = db.relationship('Reserva', backref='canal', lazy='dynamic')

    def __repr__(self):
        return f'<Canal {self.nombre}>'
