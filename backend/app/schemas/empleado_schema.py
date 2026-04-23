from marshmallow import fields
from app.extensions import ma
from app.models.empleado import Departamento, Cargo, Empleado, UsuarioSistema, Turno


class DepartamentoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Departamento
        load_instance = True

    id = ma.auto_field(dump_only=True)


class CargoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cargo
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    departamento = ma.Nested(DepartamentoSchema, dump_only=True)


class EmpleadoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Empleado
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    nombre_completo = fields.String(dump_only=True)
    cargo = ma.Nested(CargoSchema, dump_only=True)


class EmpleadoListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Empleado
        load_instance = True
        fields = ('id', 'nombre', 'apellido', 'nombre_completo', 'email',
                  'cargo_id', 'activo', 'fecha_ingreso')

    nombre_completo = fields.String(dump_only=True)


class UsuarioSistemaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UsuarioSistema
        load_instance = True
        include_fk = True
        exclude = ('password_hash',)

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    ultimo_login = ma.auto_field(dump_only=True)
    empleado_nombre = fields.Method('get_empleado_nombre')

    def get_empleado_nombre(self, obj):
        return obj.empleado.nombre_completo if obj.empleado else None


class TurnoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Turno
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)


departamento_schema = DepartamentoSchema()
departamentos_schema = DepartamentoSchema(many=True)
cargo_schema = CargoSchema()
cargos_schema = CargoSchema(many=True)
empleado_schema = EmpleadoSchema()
empleados_schema = EmpleadoSchema(many=True)
empleado_list_schema = EmpleadoListSchema(many=True)
usuario_schema = UsuarioSistemaSchema()
usuarios_schema = UsuarioSistemaSchema(many=True)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)
