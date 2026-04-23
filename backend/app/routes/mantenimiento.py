"""
Rutas de Mantenimiento.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.mantenimiento import OrdenMantenimiento
from app.models.habitacion import Habitacion
from app.schemas.mantenimiento_schema import orden_mant_schema, ordenes_mant_schema
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('mantenimiento', description='Órdenes de mantenimiento')


@ns.route('/')
class OrdenList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'mantenimiento', 'recepcion'])
    def get(self):
        """Listar órdenes de mantenimiento."""
        query = OrdenMantenimiento.query
        estado = request.args.get('estado')
        prioridad = request.args.get('prioridad')

        if estado:
            query = query.filter_by(estado=estado)
        if prioridad:
            query = query.filter_by(prioridad=prioridad)

        query = query.order_by(
            db.case(
                (OrdenMantenimiento.prioridad == 'critica', 1),
                (OrdenMantenimiento.prioridad == 'alta', 2),
                (OrdenMantenimiento.prioridad == 'media', 3),
                (OrdenMantenimiento.prioridad == 'baja', 4),
            ),
            OrdenMantenimiento.fecha_reporte
        )
        return paginate(query, ordenes_mant_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'mantenimiento', 'recepcion', 'housekeeping'])
    def post(self):
        """Crear orden de mantenimiento."""
        data = request.json
        claims = get_jwt()
        data['reportado_por'] = claims.get('empleado_id')

        orden = orden_mant_schema.load(data, session=db.session)
        db.session.add(orden)

        # Bloquear habitación si es alta/crítica
        if orden.prioridad in ('alta', 'critica') and orden.habitacion_id:
            hab = Habitacion.query.get(orden.habitacion_id)
            if hab:
                hab.estado = 'mantenimiento'

        db.session.commit()
        return success_response(orden_mant_schema.dump(orden), 'Orden creada.', 201)


@ns.route('/<int:id>')
class OrdenDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'mantenimiento'])
    def get(self, id):
        """Detalle de orden."""
        orden = OrdenMantenimiento.query.get_or_404(id)
        return success_response(orden_mant_schema.dump(orden))


@ns.route('/<int:id>/estado')
class OrdenEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'mantenimiento'])
    def patch(self, id):
        """Actualizar estado de orden."""
        orden = OrdenMantenimiento.query.get_or_404(id)
        data = request.json

        if 'estado' in data:
            orden.estado = data['estado']
        if 'notas_cierre' in data:
            orden.notas_cierre = data['notas_cierre']
        if 'costo_material' in data:
            orden.costo_material = data['costo_material']

        # Si se completa, liberar habitación
        if orden.estado == 'completada' and orden.habitacion_id:
            hab = Habitacion.query.get(orden.habitacion_id)
            if hab and hab.estado == 'mantenimiento':
                hab.estado = 'disponible'
            orden.fecha_cierre = db.func.now()

        db.session.commit()
        return success_response(orden_mant_schema.dump(orden), 'Orden actualizada.')


@ns.route('/<int:id>/asignar')
class OrdenAsignar(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'mantenimiento'])
    def patch(self, id):
        """Asignar técnico a una orden."""
        orden = OrdenMantenimiento.query.get_or_404(id)
        data = request.json
        orden.asignado_a = data.get('empleado_id')
        if orden.estado == 'abierta':
            orden.estado = 'en_proceso'
            orden.fecha_inicio = db.func.now()
        db.session.commit()
        return success_response(orden_mant_schema.dump(orden), 'Técnico asignado.')
