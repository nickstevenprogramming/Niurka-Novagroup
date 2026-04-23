from hashlib import sha256
from app.extensions import db


class Departamento(db.Model):
    __tablename__ = 'departamentos'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)

    cargos = db.relationship('Cargo', backref='departamento', lazy='dynamic')

    def __repr__(self):
        return f'<Departamento {self.nombre}>'


class Cargo(db.Model):
    __tablename__ = 'cargos'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    departamento_id = db.Column(db.SmallInteger, db.ForeignKey('departamentos.id'), nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    nivel = db.Column(db.SmallInteger, default=1)

    empleados = db.relationship('Empleado', backref='cargo', lazy='dynamic')

    def __repr__(self):
        return f'<Cargo {self.nombre}>'


class Empleado(db.Model):
    __tablename__ = 'empleados'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cargo_id = db.Column(db.SmallInteger, db.ForeignKey('cargos.id'), nullable=False)
    cedula = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(25))
    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_egreso = db.Column(db.Date)
    salario = db.Column(db.Numeric(10, 2))
    activo = db.Column(db.Boolean, default=True)

    usuario = db.relationship('UsuarioSistema', backref='empleado', uselist=False, lazy='joined')
    turnos = db.relationship('Turno', backref='empleado', lazy='dynamic')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'


class UsuarioSistema(db.Model):
    __tablename__ = 'usuarios_sistema'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False, unique=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(
        db.Enum('admin', 'gerente', 'recepcion', 'housekeeping',
                'restaurante', 'mantenimiento', 'seguridad',
                name='rol_enum'),
        nullable=False
    )
    activo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        """Hashea la contraseña con SHA-256 (compatible con la BD existente)."""
        self.password_hash = sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Verifica la contraseña contra el hash SHA-256."""
        return self.password_hash == sha256(password.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f'<UsuarioSistema {self.username}>'


class Turno(db.Model):
    __tablename__ = 'turnos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)
    tipo = db.Column(
        db.Enum('mañana', 'tarde', 'noche', name='tipo_turno_enum'),
        nullable=False
    )
    asistio = db.Column(db.Boolean)
    notas = db.Column(db.String(200))

    def __repr__(self):
        return f'<Turno {self.empleado_id} {self.fecha}>'
