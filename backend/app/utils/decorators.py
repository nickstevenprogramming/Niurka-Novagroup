"""
Decoradores personalizados para autenticación y autorización.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def role_required(allowed_roles):
    """
    Decorador que verifica que el usuario tenga uno de los roles permitidos.

    Uso:
        @role_required(['admin', 'gerente', 'recepcion'])
        def mi_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('rol', '')

            if user_role not in allowed_roles:
                return {
                    'success': False,
                    'message': f'Acceso denegado. Se requiere uno de los roles: {", ".join(allowed_roles)}'
                }, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Shortcut: solo admin."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('rol') != 'admin':
            return {
                'success': False,
                'message': 'Acceso denegado. Se requiere rol de administrador.'
            }, 403
        return fn(*args, **kwargs)
    return wrapper


def gerencia_required(fn):
    """Shortcut: admin o gerente."""
    return role_required(['admin', 'gerente'])(fn)
