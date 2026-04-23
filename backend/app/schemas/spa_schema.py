from marshmallow import fields
from app.extensions import ma
from app.models.spa import ServicioSpa, CitaSpa


class ServicioSpaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServicioSpa
        load_instance = True

    id = ma.auto_field(dump_only=True)


class CitaSpaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CitaSpa
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    servicio_nombre = fields.Method('get_servicio')
    huesped_nombre = fields.Method('get_huesped')
    terapeuta_nombre = fields.Method('get_terapeuta')

    def get_servicio(self, obj):
        return obj.servicio.nombre if obj.servicio else None

    def get_huesped(self, obj):
        return f'{obj.huesped.nombre} {obj.huesped.apellido}' if obj.huesped else None

    def get_terapeuta(self, obj):
        return obj.terapeuta.nombre_completo if obj.terapeuta else None


servicio_spa_schema = ServicioSpaSchema()
servicios_spa_schema = ServicioSpaSchema(many=True)
cita_spa_schema = CitaSpaSchema()
citas_spa_schema = CitaSpaSchema(many=True)
