from app.extensions import db


class HabitacionAmenidad(db.Model):
    """Tabla pivote tipo_habitacion ↔ amenidad."""
    __tablename__ = 'habitacion_amenidades'

    tipo_habitacion_id = db.Column(
        db.SmallInteger, db.ForeignKey('tipos_habitacion.id'), primary_key=True
    )
    amenidad_id = db.Column(
        db.SmallInteger, db.ForeignKey('amenidades.id'), primary_key=True
    )


class TipoHabitacion(db.Model):
    __tablename__ = 'tipos_habitacion'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    descripcion = db.Column(db.Text)
    capacidad_min = db.Column(db.SmallInteger, nullable=False, default=1)
    capacidad_max = db.Column(db.SmallInteger, nullable=False, default=2)
    camas = db.Column(db.String(60))
    area_m2 = db.Column(db.Numeric(6, 2))
    piso_minimo = db.Column(db.SmallInteger, default=1)
    piso_maximo = db.Column(db.SmallInteger, default=1)
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    habitaciones = db.relationship('Habitacion', backref='tipo', lazy='dynamic')
    amenidades = db.relationship(
        'Amenidad', secondary='habitacion_amenidades',
        backref=db.backref('tipos_habitacion', lazy='dynamic'), lazy='joined'
    )
    tarifas_especiales = db.relationship('TarifaEspecial', backref='tipo_habitacion', lazy='dynamic')

    def __repr__(self):
        return f'<TipoHabitacion {self.nombre}>'


class Amenidad(db.Model):
    __tablename__ = 'amenidades'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    icono = db.Column(db.String(10))

    def __repr__(self):
        return f'<Amenidad {self.nombre}>'


class Habitacion(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    tipo_id = db.Column(db.SmallInteger, db.ForeignKey('tipos_habitacion.id'), nullable=False)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    piso = db.Column(db.SmallInteger, nullable=False)
    estado = db.Column(
        db.Enum('disponible', 'ocupada', 'mantenimiento', 'bloqueada', 'limpieza',
                name='estado_habitacion'),
        nullable=False, default='disponible'
    )
    estado_limpieza = db.Column(
        db.Enum('limpia', 'sucia', 'en_proceso', 'inspeccion', name='estado_limpieza_enum'),
        nullable=False, default='limpia'
    )
    fumadores = db.Column(db.Boolean, default=False)
    accesible = db.Column(db.Boolean, default=False)
    notas_internas = db.Column(db.Text)
    ultima_limpieza = db.Column(db.DateTime)
    activa = db.Column(db.Boolean, default=True)

    # Relaciones
    reservas = db.relationship('Reserva', backref='habitacion', lazy='dynamic')
    asignaciones_limpieza = db.relationship('AsignacionLimpieza', backref='habitacion', lazy='dynamic')
    ordenes_mantenimiento = db.relationship('OrdenMantenimiento', backref='habitacion', lazy='dynamic')

    def __repr__(self):
        return f'<Habitacion {self.numero}>'
