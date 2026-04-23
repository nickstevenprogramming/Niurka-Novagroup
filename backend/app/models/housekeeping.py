from app.extensions import db


class AsignacionLimpieza(db.Model):
    __tablename__ = 'asignaciones_limpieza'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    empleada_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(
        db.Enum('diaria', 'salida', 'llegada', 'profunda', 'inspeccion',
                name='tipo_limpieza_enum'),
        nullable=False
    )
    estado = db.Column(
        db.Enum('pendiente', 'en_proceso', 'completada', 'verificada',
                name='estado_limpieza_asig_enum'),
        nullable=False, default='pendiente'
    )
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)
    duracion_min = db.Column(db.SmallInteger)
    observaciones = db.Column(db.Text)
    inspeccionada_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))

    empleada = db.relationship('Empleado', foreign_keys=[empleada_id],
                                backref='asignaciones_limpieza', lazy='joined')
    inspector = db.relationship('Empleado', foreign_keys=[inspeccionada_por], lazy='joined')
    incidencias = db.relationship('IncidenciaLimpieza', backref='asignacion',
                                   lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AsignacionLimpieza hab={self.habitacion_id} {self.fecha}>'


class IncidenciaLimpieza(db.Model):
    __tablename__ = 'incidencias_limpieza'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asignacion_id = db.Column(
        db.Integer, db.ForeignKey('asignaciones_limpieza.id'), nullable=False
    )
    tipo = db.Column(
        db.Enum('objeto_olvidado', 'danio', 'faltante', 'otro',
                name='tipo_incidencia_enum'),
        nullable=False
    )
    descripcion = db.Column(db.Text, nullable=False)
    atendida = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<IncidenciaLimpieza {self.tipo}>'


class ObjetoOlvidado(db.Model):
    __tablename__ = 'objetos_olvidados'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    encontrado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    estado = db.Column(
        db.Enum('en_custodia', 'devuelto', 'descartado', name='estado_objeto_enum'),
        default='en_custodia'
    )
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'))
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))

    habitacion = db.relationship('Habitacion', backref='objetos_olvidados', lazy='joined')
    huesped = db.relationship('Huesped', lazy='joined')
    empleado = db.relationship('Empleado', lazy='joined')

    def __repr__(self):
        return f'<ObjetoOlvidado {self.descripcion[:30]}>'
