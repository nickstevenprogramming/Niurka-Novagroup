from marshmallow import fields
from app.extensions import ma
from app.models.inventario import CategoriaInventario, Inventario, MovimientoInventario


class CategoriaInventarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CategoriaInventario
        load_instance = True

    id = ma.auto_field(dump_only=True)


class InventarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventario
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    bajo_stock = fields.Boolean(dump_only=True)
    categoria_nombre = fields.Method('get_categoria')

    def get_categoria(self, obj):
        return obj.categoria.nombre if obj.categoria else None


class MovimientoInventarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MovimientoInventario
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    movido_en = ma.auto_field(dump_only=True)


cat_inventario_schema = CategoriaInventarioSchema()
cats_inventario_schema = CategoriaInventarioSchema(many=True)
inventario_schema = InventarioSchema()
inventarios_schema = InventarioSchema(many=True)
movimiento_schema = MovimientoInventarioSchema()
movimientos_schema = MovimientoInventarioSchema(many=True)
