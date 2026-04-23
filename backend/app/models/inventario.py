from app.extensions import db


class CategoriaInventario(db.Model):
    __tablename__ = 'categorias_inventario'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)

    items = db.relationship('Inventario', backref='categoria', lazy='dynamic')

    def __repr__(self):
        return f'<CategoriaInventario {self.nombre}>'


class Inventario(db.Model):
    __tablename__ = 'inventario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria_id = db.Column(db.SmallInteger, db.ForeignKey('categorias_inventario.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    unidad = db.Column(db.String(20), default='unidad')
    stock_actual = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock_minimo = db.Column(db.Numeric(10, 2), nullable=False, default=5)
    precio_costo = db.Column(db.Numeric(10, 2))
    proveedor = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    movimientos = db.relationship('MovimientoInventario', backref='item', lazy='dynamic')

    @property
    def bajo_stock(self):
        return float(self.stock_actual) <= float(self.stock_minimo)

    def __repr__(self):
        return f'<Inventario {self.nombre}>'


class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    tipo = db.Column(
        db.Enum('entrada', 'salida', 'ajuste', name='tipo_mov_inv_enum'),
        nullable=False
    )
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    motivo = db.Column(db.String(200))
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    referencia_id = db.Column(db.Integer)
    movido_en = db.Column(db.DateTime, server_default=db.func.now())

    empleado = db.relationship('Empleado', backref='movimientos_inventario', lazy='joined')

    def __repr__(self):
        return f'<MovimientoInventario {self.tipo} {self.cantidad}>'
