"""
Rutas de Dashboard — KPIs, estadísticas y reportes.
"""

from datetime import date, datetime
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.reserva import Reserva
from app.models.auditoria import Auditoria
from app.services.dashboard_service import DashboardService
from app.schemas.reserva_schema import reserva_list_schema
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response

ns = Namespace('dashboard', description='Dashboard y reportes')


@ns.route('/kpis')
class DashboardKPIs(Resource):
    @jwt_required()
    def get(self):
        """KPIs generales del hotel."""
        fecha_str = request.args.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
        kpis = DashboardService.get_kpis(fecha)
        return success_response(kpis)


@ns.route('/ingresos')
class DashboardIngresos(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Ingresos por mes."""
        meses = request.args.get('meses', 12, type=int)
        data = DashboardService.get_ingresos_por_mes(meses)
        return success_response(data)


@ns.route('/huespedes-frecuentes')
class DashboardHuespedes(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Top huéspedes por estancias y gasto."""
        limit = request.args.get('limit', 10, type=int)
        data = DashboardService.get_huespedes_frecuentes(limit)
        return success_response(data)


@ns.route('/canales')
class DashboardCanales(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Rendimiento por canal de distribución."""
        data = DashboardService.get_canales_rendimiento()
        return success_response(data)


@ns.route('/agenda')
class DashboardAgenda(Resource):
    @jwt_required()
    def get(self):
        """Agenda de llegadas y salidas próximos 7 días."""
        from datetime import timedelta
        hoy = date.today()
        fin = hoy + timedelta(days=7)

        llegadas = Reserva.query.filter(
            Reserva.fecha_entrada.between(hoy, fin),
            Reserva.estado_id.in_([1, 2])
        ).order_by(Reserva.fecha_entrada).all()

        salidas = Reserva.query.filter(
            Reserva.fecha_salida.between(hoy, fin),
            Reserva.estado_id == 3
        ).order_by(Reserva.fecha_salida).all()

        return success_response({
            'llegadas': reserva_list_schema.dump(llegadas),
            'salidas': reserva_list_schema.dump(salidas),
        })


@ns.route('/auditoria')
class DashboardAuditoria(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'seguridad'])
    def get(self):
        """Log de auditoría."""
        query = Auditoria.query
        tabla = request.args.get('tabla')
        if tabla:
            query = query.filter_by(tabla=tabla)
        query = query.order_by(Auditoria.fecha.desc())

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        result = [{
            'id': a.id, 'tabla': a.tabla, 'operacion': a.operacion,
            'registro_id': a.registro_id,
            'datos_antes': a.datos_antes,
            'datos_despues': a.datos_despues,
            'fecha': a.fecha.isoformat() if a.fecha else None,
        } for a in pagination.items]

        return success_response({
            'data': result,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
            }
        })
