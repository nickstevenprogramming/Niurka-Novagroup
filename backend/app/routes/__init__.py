"""
Registro centralizado de la API Flask-RESTX y todos los namespaces.
"""

from flask_restx import Api

# Importar namespaces
from app.routes.auth import ns as auth_ns
from app.routes.hotel import ns as hotel_ns
from app.routes.habitaciones import ns as habitaciones_ns
from app.routes.tarifas import ns as tarifas_ns
from app.routes.huespedes import ns as huespedes_ns
from app.routes.reservas import ns as reservas_ns
from app.routes.checkin_checkout import ns as checkin_ns
from app.routes.empleados import ns as empleados_ns
from app.routes.facturacion import ns as facturacion_ns
from app.routes.housekeeping import ns as housekeeping_ns
from app.routes.mantenimiento import ns as mantenimiento_ns
from app.routes.restaurante import ns as restaurante_ns
from app.routes.spa import ns as spa_ns
from app.routes.inventario import ns as inventario_ns
from app.routes.notificaciones import ns as notificaciones_ns
from app.routes.resenas import ns as resenas_ns
from app.routes.parking import ns as parking_ns
from app.routes.dashboard import ns as dashboard_ns


def create_api(app):
    """Crea la instancia de Flask-RESTX API y registra todos los namespaces."""

    api = Api(
        app,
        version='1.0',
        title='🏨 Hotel Anacaona & Spa — API',
        description=(
            'API REST completa para el Sistema de Gestión de Reservas.\n\n'
            '**Módulos:** Habitaciones · Reservas · Huéspedes · Empleados · '
            'Facturación · Pagos · Inventario · Restaurante · Spa · '
            'Housekeeping · Mantenimiento · Reseñas · Notificaciones · '
            'Parking · Dashboard\n\n'
            '**Autenticación:** JWT Bearer Token'
        ),
        prefix='/api/v1',
        doc='/api/v1/docs',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Ingrese: Bearer <tu_token_jwt>'
            }
        },
        security='Bearer'
    )

    # ── Registrar Namespaces ──
    api.add_namespace(auth_ns,           path='/auth')
    api.add_namespace(hotel_ns,          path='/hotel')
    api.add_namespace(habitaciones_ns,   path='/habitaciones')
    api.add_namespace(tarifas_ns,        path='/tarifas')
    api.add_namespace(huespedes_ns,      path='/huespedes')
    api.add_namespace(reservas_ns,       path='/reservas')
    api.add_namespace(checkin_ns,        path='/operaciones')
    api.add_namespace(empleados_ns,      path='/empleados')
    api.add_namespace(facturacion_ns,    path='/facturacion')
    api.add_namespace(housekeeping_ns,   path='/housekeeping')
    api.add_namespace(mantenimiento_ns,  path='/mantenimiento')
    api.add_namespace(restaurante_ns,    path='/restaurante')
    api.add_namespace(spa_ns,            path='/spa')
    api.add_namespace(inventario_ns,     path='/inventario')
    api.add_namespace(notificaciones_ns, path='/notificaciones')
    api.add_namespace(resenas_ns,        path='/resenas')
    api.add_namespace(parking_ns,        path='/parking')
    api.add_namespace(dashboard_ns,      path='/dashboard')

    return api
