"""
App Factory — Hotel Anacaona & Spa Backend API.
"""

import os
from flask import Flask
from config import config_map


def create_app(config_name=None):
    """Crea y configura la aplicación Flask."""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ── Registrar extensiones ──
    _register_extensions(app)

    # ── Registrar la API ──
    _register_api(app)

    # ── Registrar error handlers ──
    _register_error_handlers(app)

    # ── Callbacks JWT ──
    _register_jwt_callbacks(app)

    return app


def _register_extensions(app):
    """Inicializa todas las extensiones Flask."""
    from app.extensions import db, migrate, jwt, cors, mail, ma

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)
    ma.init_app(app)


def _register_api(app):
    """Registra Flask-RESTX API y todos los namespaces."""
    from app.routes import create_api
    create_api(app)


def _register_error_handlers(app):
    """Registra manejadores de error globales."""
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)


def _register_jwt_callbacks(app):
    """Configura callbacks de JWT."""
    from app.extensions import jwt

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'message': 'El token ha expirado.',
            'error': 'token_expired'
        }, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'success': False,
            'message': 'Token inválido.',
            'error': 'invalid_token'
        }, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'success': False,
            'message': 'Token de autorización requerido.',
            'error': 'authorization_required'
        }, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'message': 'El token ha sido revocado.',
            'error': 'token_revoked'
        }, 401
