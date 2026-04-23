from marshmallow import fields, validate
from app.extensions import ma
from app.models.habitacion import TipoHabitacion, Amenidad, Habitacion


class AmenidadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Amenidad
        load_instance = True

    id = ma.auto_field(dump_only=True)


class TipoHabitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TipoHabitacion
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    amenidades = ma.Nested(AmenidadSchema, many=True, dump_only=True)


class HabitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Habitacion
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    tipo = ma.Nested(TipoHabitacionSchema, dump_only=True, exclude=('amenidades',))
    estado = fields.String(validate=validate.OneOf(
        ['disponible', 'ocupada', 'mantenimiento', 'bloqueada', 'limpieza']
    ))
    estado_limpieza = fields.String(validate=validate.OneOf(
        ['limpia', 'sucia', 'en_proceso', 'inspeccion']
    ))


class HabitacionListSchema(ma.SQLAlchemyAutoSchema):
    """Schema ligero para listados."""
    class Meta:
        model = Habitacion
        load_instance = True
        include_fk = True
        fields = ('id', 'numero', 'piso', 'estado', 'estado_limpieza',
                  'tipo_id', 'tipo_nombre', 'accesible', 'activa')

    tipo_nombre = fields.Method('get_tipo_nombre')

    def get_tipo_nombre(self, obj):
        return obj.tipo.nombre if obj.tipo else None


amenidad_schema = AmenidadSchema()
amenidades_schema = AmenidadSchema(many=True)
tipo_habitacion_schema = TipoHabitacionSchema()
tipos_habitacion_schema = TipoHabitacionSchema(many=True)
habitacion_schema = HabitacionSchema()
habitaciones_schema = HabitacionSchema(many=True)
habitacion_list_schema = HabitacionListSchema(many=True)
