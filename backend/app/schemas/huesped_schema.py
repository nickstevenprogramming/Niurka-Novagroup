from marshmallow import fields
from app.extensions import ma
from app.models.huesped import Huesped, Pais


class PaisSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pais
        load_instance = True


class HuespedSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Huesped
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    nombre_completo = fields.String(dump_only=True)
    pais = ma.Nested(PaisSchema, dump_only=True)


class HuespedListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Huesped
        load_instance = True
        fields = ('id', 'nombre', 'apellido', 'nombre_completo', 'email',
                  'telefono', 'pais_id', 'nivel_vip', 'blacklist')

    nombre_completo = fields.String(dump_only=True)


pais_schema = PaisSchema()
paises_schema = PaisSchema(many=True)
huesped_schema = HuespedSchema()
huespedes_schema = HuespedSchema(many=True)
huesped_list_schema = HuespedListSchema(many=True)
