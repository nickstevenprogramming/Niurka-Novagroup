from app.extensions import db


class Hotel(db.Model):
    __tablename__ = 'hotel'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(80))
    pais = db.Column(db.String(60), default='República Dominicana')
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    sitio_web = db.Column(db.String(120))
    estrellas = db.Column(db.SmallInteger, default=3)
    check_in_hora = db.Column(db.Time, nullable=False)
    check_out_hora = db.Column(db.Time, nullable=False)
    moneda = db.Column(db.String(3), default='DOP')
    impuesto_pct = db.Column(db.Numeric(5, 2), default=18.00)
    politica_cancel = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Hotel {self.nombre}>'
