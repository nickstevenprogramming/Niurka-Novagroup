from marshmallow import fields
from app.extensions import ma
from app.models.resena import Resena


class ResenaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Resena
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    huesped_nombre = fields.Method('get_huesped')

    def get_huesped(self, obj):
        return obj.huesped.nombre_completo if obj.huesped else None


resena_schema = ResenaSchema()
resenas_schema = ResenaSchema(many=True)
