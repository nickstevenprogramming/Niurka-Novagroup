"""
Rutas de Spa — Servicios + citas.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.spa import ServicioSpa, CitaSpa
from app.schemas.spa_schema import (
    servicio_spa_schema, servicios_spa_schema,
    cita_spa_schema, citas_spa_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('spa', description='Spa y bienestar')


@ns.route('/servicios')
class ServicioList(Resource):
    @jwt_required()
    def get(self):
        """Listar servicios de spa."""
        servicios = ServicioSpa.query.filter_by(disponible=True).all()
        return success_response(servicios_spa_schema.dump(servicios))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear servicio de spa."""
        data = request.json
        servicio = servicio_spa_schema.load(data, session=db.session)
        db.session.add(servicio)
        db.session.commit()
        return success_response(servicio_spa_schema.dump(servicio), 'Servicio creado.', 201)


@ns.route('/servicios/<int:id>')
class ServicioDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar servicio de spa."""
        servicio = ServicioSpa.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(servicio, key) and key not in ('id',):
                setattr(servicio, key, value)
        db.session.commit()
        return success_response(servicio_spa_schema.dump(servicio), 'Servicio actualizado.')


@ns.route('/citas')
class CitaList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def get(self):
        """Listar citas de spa."""
        query = CitaSpa.query
        estado = request.args.get('estado')
        fecha = request.args.get('fecha')

        if estado:
            query = query.filter_by(estado=estado)
        if fecha:
            query = query.filter(db.func.date(CitaSpa.fecha_hora) == fecha)

        query = query.order_by(CitaSpa.fecha_hora)
        return paginate(query, citas_spa_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Agendar cita de spa."""
        data = request.json
        servicio = ServicioSpa.query.get(data.get('servicio_id'))
        if not servicio:
            return error_response('Servicio no encontrado.', 404)

        data['precio_cobrado'] = data.get('precio_cobrado', float(servicio.precio))
        cita = cita_spa_schema.load(data, session=db.session)
        db.session.add(cita)
        db.session.commit()
        return success_response(cita_spa_schema.dump(cita), 'Cita agendada.', 201)


@ns.route('/citas/<int:id>/estado')
class CitaEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def patch(self, id):
        """Actualizar estado de cita."""
        cita = CitaSpa.query.get_or_404(id)
        data = request.json
        if 'estado' in data:
            cita.estado = data['estado']
        db.session.commit()
        return success_response(cita_spa_schema.dump(cita), 'Cita actualizada.')
