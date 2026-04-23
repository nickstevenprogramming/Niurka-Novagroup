"""
Rutas de Housekeeping — Limpieza + incidencias + objetos perdidos.
"""

from datetime import date
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.housekeeping import AsignacionLimpieza, IncidenciaLimpieza, ObjetoOlvidado
from app.models.habitacion import Habitacion
from app.schemas.housekeeping_schema import (
    asignacion_schema, asignaciones_schema,
    incidencia_schema, incidencias_schema,
    objeto_olvidado_schema, objetos_olvidados_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('housekeeping', description='Amas de llaves y limpieza')


@ns.route('/hoy')
class HousekeepingHoy(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def get(self):
        """Vista del día — todas las habitaciones y su estado de limpieza."""
        habitaciones = Habitacion.query.filter_by(activa=True).order_by(
            Habitacion.piso, Habitacion.numero
        ).all()

        result = []
        for h in habitaciones:
            asig = AsignacionLimpieza.query.filter_by(
                habitacion_id=h.id, fecha=date.today()
            ).first()

            result.append({
                'habitacion_id': h.id,
                'numero': h.numero,
                'piso': h.piso,
                'tipo': h.tipo.nombre,
                'estado': h.estado,
                'estado_limpieza': h.estado_limpieza,
                'asignacion': asignacion_schema.dump(asig) if asig else None,
            })

        return success_response(result)


@ns.route('/asignaciones')
class AsignacionList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def get(self):
        """Listar asignaciones de limpieza."""
        query = AsignacionLimpieza.query
        fecha = request.args.get('fecha', date.today().isoformat())
        empleada_id = request.args.get('empleada_id', type=int)

        query = query.filter_by(fecha=fecha)
        if empleada_id:
            query = query.filter_by(empleada_id=empleada_id)

        return paginate(query, asignaciones_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def post(self):
        """Crear asignación de limpieza."""
        data = request.json
        asig = asignacion_schema.load(data, session=db.session)
        db.session.add(asig)
        db.session.commit()
        return success_response(asignacion_schema.dump(asig), 'Asignación creada.', 201)


@ns.route('/asignaciones/<int:id>/estado')
class AsignacionEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def patch(self, id):
        """Actualizar estado de asignación y habitación."""
        asig = AsignacionLimpieza.query.get_or_404(id)
        data = request.json

        if 'estado' in data:
            asig.estado = data['estado']
        if 'hora_inicio' in data:
            asig.hora_inicio = data['hora_inicio']
        if 'hora_fin' in data:
            asig.hora_fin = data['hora_fin']
        if 'observaciones' in data:
            asig.observaciones = data['observaciones']

        # Si se completó, actualizar estado de habitación
        if asig.estado == 'completada':
            hab = Habitacion.query.get(asig.habitacion_id)
            if hab:
                hab.estado_limpieza = 'inspeccion'

        if asig.estado == 'verificada':
            hab = Habitacion.query.get(asig.habitacion_id)
            if hab:
                hab.estado_limpieza = 'limpia'
                if hab.estado == 'limpieza':
                    hab.estado = 'disponible'
                hab.ultima_limpieza = db.func.now()

        db.session.commit()
        return success_response(asignacion_schema.dump(asig), 'Estado actualizado.')


@ns.route('/incidencias')
class IncidenciaList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def post(self):
        """Reportar incidencia de limpieza."""
        data = request.json
        incidencia = incidencia_schema.load(data, session=db.session)
        db.session.add(incidencia)
        db.session.commit()
        return success_response(incidencia_schema.dump(incidencia), 'Incidencia reportada.', 201)


@ns.route('/objetos-perdidos')
class ObjetoPerdidoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping', 'recepcion'])
    def get(self):
        """Listar objetos olvidados."""
        query = ObjetoOlvidado.query
        estado = request.args.get('estado')
        if estado:
            query = query.filter_by(estado=estado)
        query = query.order_by(ObjetoOlvidado.encontrado_en.desc())
        return paginate(query, objetos_olvidados_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def post(self):
        """Registrar objeto olvidado."""
        data = request.json
        objeto = objeto_olvidado_schema.load(data, session=db.session)
        db.session.add(objeto)
        db.session.commit()
        return success_response(objeto_olvidado_schema.dump(objeto), 'Objeto registrado.', 201)


@ns.route('/objetos-perdidos/<int:id>')
class ObjetoPerdidoDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping', 'recepcion'])
    def patch(self, id):
        """Actualizar estado de objeto (devuelto, descartado)."""
        obj = ObjetoOlvidado.query.get_or_404(id)
        data = request.json
        if 'estado' in data:
            obj.estado = data['estado']
        if 'huesped_id' in data:
            obj.huesped_id = data['huesped_id']
        db.session.commit()
        return success_response(objeto_olvidado_schema.dump(obj), 'Objeto actualizado.')
