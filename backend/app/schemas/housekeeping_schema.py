from marshmallow import fields
from app.extensions import ma
from app.models.housekeeping import AsignacionLimpieza, IncidenciaLimpieza, ObjetoOlvidado


class IncidenciaLimpiezaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IncidenciaLimpieza
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)


class AsignacionLimpiezaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AsignacionLimpieza
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    empleada_nombre = fields.Method('get_empleada_nombre')
    habitacion_numero = fields.Method('get_habitacion_numero')

    def get_empleada_nombre(self, obj):
        return obj.empleada.nombre_completo if obj.empleada else None

    def get_habitacion_numero(self, obj):
        return obj.habitacion.numero if obj.habitacion else None


class ObjetoOlvidadoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ObjetoOlvidado
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    encontrado_en = ma.auto_field(dump_only=True)


asignacion_schema = AsignacionLimpiezaSchema()
asignaciones_schema = AsignacionLimpiezaSchema(many=True)
incidencia_schema = IncidenciaLimpiezaSchema()
incidencias_schema = IncidenciaLimpiezaSchema(many=True)
objeto_olvidado_schema = ObjetoOlvidadoSchema()
objetos_olvidados_schema = ObjetoOlvidadoSchema(many=True)
