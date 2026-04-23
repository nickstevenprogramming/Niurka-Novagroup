from marshmallow import fields
from app.extensions import ma
from app.models.restaurante import CategoriaMenu, ProductoMenu, PedidoRestaurante, ItemPedido


class CategoriaMenuSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CategoriaMenu
        load_instance = True

    id = ma.auto_field(dump_only=True)


class ProductoMenuSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductoMenu
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    categoria_nombre = fields.Method('get_categoria')

    def get_categoria(self, obj):
        return obj.categoria.nombre if obj.categoria else None


class ItemPedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemPedido
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    producto_nombre = fields.Method('get_producto')

    def get_producto(self, obj):
        return obj.producto.nombre if obj.producto else None


class PedidoRestauranteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PedidoRestaurante
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    items = ma.Nested(ItemPedidoSchema, many=True, dump_only=True)
    huesped_nombre = fields.Method('get_huesped')

    def get_huesped(self, obj):
        return f'{obj.huesped.nombre} {obj.huesped.apellido}' if obj.huesped else None


categoria_menu_schema = CategoriaMenuSchema()
categorias_menu_schema = CategoriaMenuSchema(many=True)
producto_menu_schema = ProductoMenuSchema()
productos_menu_schema = ProductoMenuSchema(many=True)
item_pedido_schema = ItemPedidoSchema()
pedido_schema = PedidoRestauranteSchema()
pedidos_schema = PedidoRestauranteSchema(many=True)
