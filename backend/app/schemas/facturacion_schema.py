from marshmallow import fields
from app.extensions import ma
from app.models.facturacion import MetodoPago, Factura, ItemFactura, Pago, CargoHabitacion


class MetodoPagoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MetodoPago
        load_instance = True

    id = ma.auto_field(dump_only=True)


class ItemFacturaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemFactura
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)


class PagoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pago
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    pagado_en = ma.auto_field(dump_only=True)
    metodo = ma.Nested(MetodoPagoSchema, dump_only=True)


class FacturaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Factura
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    numero = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    total_pagado = fields.Float(dump_only=True)
    saldo = fields.Float(dump_only=True)
    items = ma.Nested(ItemFacturaSchema, many=True, dump_only=True)
    pagos = ma.Nested(PagoSchema, many=True, dump_only=True)
    huesped_nombre = fields.Method('get_huesped_nombre')

    def get_huesped_nombre(self, obj):
        return f'{obj.huesped.nombre} {obj.huesped.apellido}' if obj.huesped else None


class CargoHabitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CargoHabitacion
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    registrado_en = ma.auto_field(dump_only=True)


metodo_pago_schema = MetodoPagoSchema()
metodos_pago_schema = MetodoPagoSchema(many=True)
item_factura_schema = ItemFacturaSchema()
pago_schema = PagoSchema()
pagos_schema = PagoSchema(many=True)
factura_schema = FacturaSchema()
facturas_schema = FacturaSchema(many=True)
cargo_habitacion_schema = CargoHabitacionSchema()
cargos_habitacion_schema = CargoHabitacionSchema(many=True)
