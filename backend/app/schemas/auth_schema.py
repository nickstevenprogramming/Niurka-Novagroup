from marshmallow import fields, validate

from app.extensions import ma


class LoginSchema(ma.Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))


class CambiarPasswordSchema(ma.Schema):
    password_actual = fields.String(required=True)
    password_nuevo = fields.String(required=True, validate=validate.Length(min=6))


class PerfilSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    rol = fields.String()
    empleado_id = fields.Integer()
    empleado_nombre = fields.String()
    ultimo_login = fields.DateTime()


login_schema = LoginSchema()
cambiar_password_schema = CambiarPasswordSchema()
perfil_schema = PerfilSchema()
