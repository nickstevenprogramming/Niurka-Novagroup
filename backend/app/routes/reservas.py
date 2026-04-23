"""
Rutas de Reservas — CRUD + disponibilidad + calendario.
"""

from datetime import date, datetime
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.reserva import Reserva, SolicitudEspecial
from app.schemas.reserva_schema import (
    reserva_schema, reserva_list_schema, crear_reserva_schema, solicitud_schema
)
from app.schemas.habitacion_schema import habitaciones_schema
from app.services.reserva_service import ReservaService
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('reservas', description='Gestión de reservas')


@ns.route('/')
class ReservaList(Resource):
    @jwt_required()
    def get(self):
        """Listar reservas con filtros."""
        query = Reserva.query

        # Filtros
        estado_id = request.args.get('estado_id', type=int)
        huesped_id = request.args.get('huesped_id', type=int)
        habitacion_id = request.args.get('habitacion_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        canal_id = request.args.get('canal_id', type=int)

        if estado_id:
            query = query.filter_by(estado_id=estado_id)
        if huesped_id:
            query = query.filter_by(huesped_id=huesped_id)
        if habitacion_id:
            query = query.filter_by(habitacion_id=habitacion_id)
        if fecha_desde:
            query = query.filter(Reserva.fecha_entrada >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Reserva.fecha_entrada <= fecha_hasta)
        if canal_id:
            query = query.filter_by(canal_id=canal_id)

        query = query.order_by(Reserva.fecha_entrada.desc())
        return paginate(query, reserva_list_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Crear nueva reserva con validaciones completas."""
        data = crear_reserva_schema.load(request.json)
        claims = get_jwt()
        staff_id = claims.get('empleado_id')

        reserva, error = ReservaService.crear_reserva(data, staff_id)
        if error:
            return error_response(error, 400)

        return success_response(reserva_schema.dump(reserva), 'Reserva creada.', 201)


@ns.route('/<int:id>')
class ReservaDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Detalle completo de una reserva."""
        reserva = Reserva.query.get_or_404(id)
        return success_response(reserva_schema.dump(reserva))

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def put(self, id):
        """Actualizar reserva."""
        reserva = Reserva.query.get_or_404(id)
        data = request.json

        campos_editables = [
            'fecha_entrada', 'fecha_salida', 'num_adultos', 'num_ninos',
            'incluye_desayuno', 'incluye_almuerzo', 'incluye_cena',
            'notas_huesped', 'notas_internas', 'hora_llegada_est', 'canal_id'
        ]
        for key in campos_editables:
            if key in data:
                setattr(reserva, key, data[key])

        db.session.commit()
        return success_response(reserva_schema.dump(reserva), 'Reserva actualizada.')


@ns.route('/<int:id>/estado')
class ReservaEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def patch(self, id):
        """Cambiar estado de una reserva."""
        reserva = Reserva.query.get_or_404(id)
        data = request.json
        nuevo_estado = data.get('estado_id')

        if nuevo_estado is None:
            return error_response('Se requiere estado_id.', 400)

        reserva.estado_id = nuevo_estado
        db.session.commit()
        return success_response(
            reserva_schema.dump(reserva),
            f'Estado actualizado a {reserva.estado.nombre}.'
        )


@ns.route('/<int:id>/cancelar')
class ReservaCancelar(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self, id):
        """Cancelar una reserva con motivo."""
        motivo = request.json.get('motivo', 'Sin motivo especificado')
        reserva, error = ReservaService.cancelar_reserva(id, motivo)
        if error:
            return error_response(error, 400)
        return success_response(reserva_schema.dump(reserva), 'Reserva cancelada.')


@ns.route('/disponibilidad')
class Disponibilidad(Resource):
    @jwt_required()
    def get(self):
        """Consultar habitaciones disponibles."""
        fecha_entrada = request.args.get('entrada')
        fecha_salida = request.args.get('salida')
        adultos = request.args.get('adultos', 1, type=int)
        tipo_id = request.args.get('tipo_id', type=int)

        if not fecha_entrada or not fecha_salida:
            return error_response('Se requieren parámetros: entrada, salida.', 400)

        try:
            entrada = datetime.strptime(fecha_entrada, '%Y-%m-%d').date()
            salida = datetime.strptime(fecha_salida, '%Y-%m-%d').date()
        except ValueError:
            return error_response('Formato de fecha inválido. Use YYYY-MM-DD.', 400)

        if salida <= entrada:
            return error_response('La fecha de salida debe ser posterior a la entrada.', 400)

        disponibles = ReservaService.buscar_disponibles(entrada, salida, adultos, tipo_id)
        return success_response({
            'fecha_entrada': entrada.isoformat(),
            'fecha_salida': salida.isoformat(),
            'noches': (salida - entrada).days,
            'adultos': adultos,
            'habitaciones_disponibles': habitaciones_schema.dump(disponibles),
            'total_disponibles': len(disponibles),
        })


@ns.route('/<int:id>/solicitudes')
class ReservaSolicitudes(Resource):
    @jwt_required()
    def get(self, id):
        """Listar solicitudes especiales de una reserva."""
        reserva = Reserva.query.get_or_404(id)
        from app.schemas.reserva_schema import solicitudes_schema
        return success_response(solicitudes_schema.dump(reserva.solicitudes.all()))

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self, id):
        """Agregar solicitud especial a una reserva."""
        reserva = Reserva.query.get_or_404(id)
        data = request.json
        solicitud = SolicitudEspecial(reserva_id=id, **data)
        db.session.add(solicitud)
        db.session.commit()
        return success_response(solicitud_schema.dump(solicitud), 'Solicitud agregada.', 201)
