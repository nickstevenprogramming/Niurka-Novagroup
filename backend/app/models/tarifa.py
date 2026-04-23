from app.extensions import db


class Temporada(db.Model):
    __tablename__ = 'temporadas'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    multiplicador = db.Column(db.Numeric(4, 2), nullable=False, default=1.00)
    activa = db.Column(db.Boolean, default=True)

    tarifas = db.relationship('TarifaEspecial', backref='temporada', lazy='dynamic')

    def __repr__(self):
        return f'<Temporada {self.nombre}>'


class TarifaEspecial(db.Model):
    __tablename__ = 'tarifas_especiales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_habitacion_id = db.Column(
        db.SmallInteger, db.ForeignKey('tipos_habitacion.id'), nullable=False
    )
    temporada_id = db.Column(db.SmallInteger, db.ForeignKey('temporadas.id'))
    nombre = db.Column(db.String(80), nullable=False)
    precio_noche = db.Column(db.Numeric(10, 2), nullable=False)
    min_noches = db.Column(db.SmallInteger, default=1)
    incluye_desayuno = db.Column(db.Boolean, default=False)
    activa = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<TarifaEspecial {self.nombre}>'
