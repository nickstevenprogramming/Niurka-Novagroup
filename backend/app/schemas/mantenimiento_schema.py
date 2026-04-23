from marshmallow import fields
from app.extensions import ma
from app.models.mantenimiento import OrdenMantenimiento


class OrdenMantenimientoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrdenMantenimiento
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    fecha_reporte = ma.auto_field(dump_only=True)
    reportador_nombre = fields.Method('get_reportador')
    tecnico_nombre = fields.Method('get_tecnico')
    habitacion_numero = fields.Method('get_habitacion')

    def get_reportador(self, obj):
        return obj.reportador.nombre_completo if obj.reportador else None

    def get_tecnico(self, obj):
        return obj.tecnico.nombre_completo if obj.tecnico else None

    def get_habitacion(self, obj):
        return obj.habitacion.numero if obj.habitacion else None


orden_mant_schema = OrdenMantenimientoSchema()
ordenes_mant_schema = OrdenMantenimientoSchema(many=True)
