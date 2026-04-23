from marshmallow import fields, validate
from app.extensions import ma
from app.models.reserva import Reserva, EstadoReserva, SolicitudEspecial, ReservaHuespedAdicional


class EstadoReservaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EstadoReserva
        load_instance = True


class SolicitudEspecialSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SolicitudEspecial
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)


class ReservaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reserva
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    codigo = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    actualizado_en = ma.auto_field(dump_only=True)

    # Campos computados
    noches = fields.Integer(dump_only=True)
    total_con_impuesto = fields.Float(dump_only=True)
    saldo_pendiente = fields.Float(dump_only=True)

    # Relaciones anidadas
    estado = ma.Nested(EstadoReservaSchema, dump_only=True)
    solicitudes = ma.Nested(SolicitudEspecialSchema, many=True, dump_only=True)

    # Info plana de relaciones
    huesped_nombre = fields.Method('get_huesped_nombre')
    habitacion_numero = fields.Method('get_habitacion_numero')
    canal_nombre = fields.Method('get_canal_nombre')

    def get_huesped_nombre(self, obj):
        return obj.huesped.nombre_completo if obj.huesped else None

    def get_habitacion_numero(self, obj):
        return obj.habitacion.numero if obj.habitacion else None

    def get_canal_nombre(self, obj):
        return obj.canal.nombre if obj.canal else None


class ReservaListSchema(ma.SQLAlchemyAutoSchema):
    """Schema ligero para listados de reservas."""
    class Meta:
        model = Reserva
        load_instance = True
        fields = ('id', 'codigo', 'huesped_id', 'habitacion_id', 'estado_id',
                  'fecha_entrada', 'fecha_salida', 'noches', 'precio_total',
                  'total_con_impuesto', 'saldo_pendiente',
                  'huesped_nombre', 'habitacion_numero', 'estado_nombre', 'estado_color')

    noches = fields.Integer(dump_only=True)
    total_con_impuesto = fields.Float(dump_only=True)
    saldo_pendiente = fields.Float(dump_only=True)
    huesped_nombre = fields.Method('get_huesped_nombre')
    habitacion_numero = fields.Method('get_habitacion_numero')
    estado_nombre = fields.Method('get_estado_nombre')
    estado_color = fields.Method('get_estado_color')

    def get_huesped_nombre(self, obj):
        return obj.huesped.nombre_completo if obj.huesped else None

    def get_habitacion_numero(self, obj):
        return obj.habitacion.numero if obj.habitacion else None

    def get_estado_nombre(self, obj):
        return obj.estado.nombre if obj.estado else None

    def get_estado_color(self, obj):
        return obj.estado.color if obj.estado else None


class CrearReservaSchema(ma.Schema):
    """Schema de entrada para crear una reserva."""
    huesped_id = fields.Integer(required=True)
    habitacion_id = fields.Integer(required=True)
    canal_id = fields.Integer(load_default=1)
    tarifa_id = fields.Integer(allow_none=True)
    fecha_entrada = fields.Date(required=True)
    fecha_salida = fields.Date(required=True)
    num_adultos = fields.Integer(required=True, validate=validate.Range(min=1))
    num_ninos = fields.Integer(load_default=0)
    incluye_desayuno = fields.Boolean(load_default=False)
    incluye_almuerzo = fields.Boolean(load_default=False)
    incluye_cena = fields.Boolean(load_default=False)
    notas_huesped = fields.String(allow_none=True)
    hora_llegada_est = fields.Time(allow_none=True)


estado_reserva_schema = EstadoReservaSchema()
estados_reserva_schema = EstadoReservaSchema(many=True)
solicitud_schema = SolicitudEspecialSchema()
solicitudes_schema = SolicitudEspecialSchema(many=True)
reserva_schema = ReservaSchema()
reservas_schema = ReservaSchema(many=True)
reserva_list_schema = ReservaListSchema(many=True)
crear_reserva_schema = CrearReservaSchema()
