from app.extensions import db


class CategoriaMenu(db.Model):
    __tablename__ = 'categorias_menu'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    tipo = db.Column(
        db.Enum('desayuno', 'almuerzo', 'cena', 'snack', 'bebida', 'postre',
                name='tipo_cat_menu_enum'),
        nullable=False
    )

    productos = db.relationship('ProductoMenu', backref='categoria', lazy='dynamic')

    def __repr__(self):
        return f'<CategoriaMenu {self.nombre}>'


class ProductoMenu(db.Model):
    __tablename__ = 'productos_menu'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    categoria_id = db.Column(db.SmallInteger, db.ForeignKey('categorias_menu.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    es_minibar = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ProductoMenu {self.nombre}>'


class PedidoRestaurante(db.Model):
    __tablename__ = 'pedidos_restaurante'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'))
    tipo = db.Column(
        db.Enum('restaurante', 'room_service', 'bar', 'minibar',
                name='tipo_pedido_enum'),
        nullable=False, default='restaurante'
    )
    mesa = db.Column(db.String(10))
    estado = db.Column(
        db.Enum('recibido', 'preparando', 'servido', 'cancelado',
                name='estado_pedido_enum'),
        nullable=False, default='recibido'
    )
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    facturado = db.Column(db.Boolean, default=False)
    atendido_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    reserva = db.relationship('Reserva', backref='pedidos', lazy='joined')
    huesped = db.relationship('Huesped', backref='pedidos', lazy='joined')
    mesero = db.relationship('Empleado', backref='pedidos_atendidos', lazy='joined')
    items = db.relationship('ItemPedido', backref='pedido', lazy='joined',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PedidoRestaurante {self.id} {self.tipo}>'


class ItemPedido(db.Model):
    __tablename__ = 'items_pedido'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(
        db.Integer, db.ForeignKey('pedidos_restaurante.id', ondelete='CASCADE'), nullable=False
    )
    producto_id = db.Column(db.SmallInteger, db.ForeignKey('productos_menu.id'), nullable=False)
    cantidad = db.Column(db.SmallInteger, nullable=False, default=1)
    precio_unit = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.String(200))

    producto = db.relationship('ProductoMenu', lazy='joined')

    def __repr__(self):
        return f'<ItemPedido {self.producto_id} x{self.cantidad}>'
