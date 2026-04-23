"""
Manejadores de error globales para la API.
"""

from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Registra todos los manejadores de error en la app Flask."""

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'success': False,
            'message': 'Error de validación.',
            'errors': error.messages
        }), 422

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        from app.extensions import db
        db.session.rollback()
        msg = str(error.orig) if error.orig else str(error)
        return jsonify({
            'success': False,
            'message': 'Error de integridad en la base de datos.',
            'detail': msg
        }), 409

    @app.errorhandler(OperationalError)
    def handle_db_error(error):
        from app.extensions import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error de conexión con la base de datos.',
        }), 503

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': error.description or 'Solicitud incorrecta.'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Recurso no encontrado.'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Método HTTP no permitido.'
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        from app.extensions import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor.'
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'success': False,
            'message': error.description or 'Error HTTP.',
        }), error.code
