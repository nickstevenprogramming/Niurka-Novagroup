"""
Utilidad de paginación reutilizable.
"""

from flask import request, current_app


def paginate(query, schema, **kwargs):
    """
    Pagina una query de SQLAlchemy y devuelve resultado serializado.

    Args:
        query: SQLAlchemy query object
        schema: instancia de Marshmallow schema (ya con many=True)

    Returns:
        dict con data paginada y metadata
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page',
                                 current_app.config.get('DEFAULT_PAGE_SIZE', 20),
                                 type=int)

    max_per_page = current_app.config.get('MAX_PAGE_SIZE', 100)
    per_page = min(per_page, max_per_page)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'success': True,
        'data': schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    }


def success_response(data=None, message=None, status_code=200):
    """Respuesta de éxito estandarizada."""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return response, status_code


def error_response(message, status_code=400, errors=None):
    """Respuesta de error estandarizada."""
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return response, status_code
