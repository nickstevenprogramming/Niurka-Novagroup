from app.extensions import db


class Pais(db.Model):
    __tablename__ = 'paises'

    codigo = db.Column(db.String(2), primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Pais {self.codigo}>'


class Huesped(db.Model):
    __tablename__ = 'huespedes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_documento = db.Column(
        db.Enum('cedula', 'pasaporte', 'licencia', 'otro', name='tipo_doc_enum'),
        nullable=False, default='pasaporte'
    )
    num_documento = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(25))
    telefono2 = db.Column(db.String(25))
    fecha_nacimiento = db.Column(db.Date)
    genero = db.Column(db.Enum('M', 'F', 'otro', name='genero_enum'))
    pais_id = db.Column(db.String(2), db.ForeignKey('paises.codigo'))
    ciudad_origen = db.Column(db.String(80))
    direccion = db.Column(db.String(200))
    empresa = db.Column(db.String(100))
    ruc_empresa = db.Column(db.String(30))
    nivel_vip = db.Column(db.SmallInteger, default=0)
    notas = db.Column(db.Text)
    blacklist = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    # Relaciones
    pais = db.relationship('Pais', backref='huespedes', lazy='joined')
    reservas = db.relationship('Reserva', backref='huesped', lazy='dynamic')
    resenas = db.relationship('Resena', backref='huesped', lazy='dynamic')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def __repr__(self):
        return f'<Huesped {self.nombre} {self.apellido}>'
