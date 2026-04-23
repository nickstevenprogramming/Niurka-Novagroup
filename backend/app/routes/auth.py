"""
Rutas de Autenticación — Login, refresh, perfil, cambiar contraseña.
"""

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.extensions import db
from app.models.empleado import UsuarioSistema
from app.schemas.auth_schema import login_schema, cambiar_password_schema
from app.utils.pagination import success_response, error_response

ns = Namespace('auth', description='Autenticación y autorización')


@ns.route('/login')
class Login(Resource):
    def post(self):
        """Iniciar sesión — devuelve JWT access y refresh tokens."""
        data = login_schema.load(request.json)

        usuario = UsuarioSistema.query.filter_by(
            username=data['username'], activo=True
        ).first()

        if not usuario or not usuario.check_password(data['password']):
            return error_response('Credenciales inválidas.', 401)

        # Actualizar último login
        usuario.ultimo_login = datetime.now()
        db.session.commit()

        # Claims adicionales en el token
        additional_claims = {
            'rol': usuario.rol,
            'empleado_id': usuario.empleado_id,
            'username': usuario.username,
        }

        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=str(usuario.id),
            additional_claims=additional_claims
        )

        return success_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'rol': usuario.rol,
                'empleado_id': usuario.empleado_id,
                'nombre': usuario.empleado.nombre_completo,
            }
        }, 'Login exitoso.')


@ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Renovar access token usando el refresh token."""
        identity = get_jwt_identity()
        claims = get_jwt()

        access_token = create_access_token(
            identity=identity,
            additional_claims={
                'rol': claims.get('rol'),
                'empleado_id': claims.get('empleado_id'),
                'username': claims.get('username'),
            }
        )
        return success_response({'access_token': access_token}, 'Token renovado.')


@ns.route('/perfil')
class Perfil(Resource):
    @jwt_required()
    def get(self):
        """Obtener datos del usuario logueado."""
        identity = get_jwt_identity()
        usuario = UsuarioSistema.query.get(int(identity))

        if not usuario:
            return error_response('Usuario no encontrado.', 404)

        return success_response({
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol,
            'empleado_id': usuario.empleado_id,
            'nombre': usuario.empleado.nombre_completo,
            'email': usuario.empleado.email,
            'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None,
        })


@ns.route('/cambiar-password')
class CambiarPassword(Resource):
    @jwt_required()
    def post(self):
        """Cambiar contraseña del usuario logueado."""
        data = cambiar_password_schema.load(request.json)
        identity = get_jwt_identity()
        usuario = UsuarioSistema.query.get(int(identity))

        if not usuario:
            return error_response('Usuario no encontrado.', 404)

        if not usuario.check_password(data['password_actual']):
            return error_response('La contraseña actual es incorrecta.', 400)

        usuario.set_password(data['password_nuevo'])
        db.session.commit()

        return success_response(message='Contraseña actualizada exitosamente.')
