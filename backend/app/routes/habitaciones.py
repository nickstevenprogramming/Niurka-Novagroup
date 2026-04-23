"""
Rutas de Habitaciones — CRUD + tipos + amenidades.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.habitacion import Habitacion, TipoHabitacion, Amenidad
from app.schemas.habitacion_schema import (
    habitacion_schema, habitaciones_schema, habitacion_list_schema,
    tipo_habitacion_schema, tipos_habitacion_schema,
    amenidad_schema, amenidades_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('habitaciones', description='Gestión de habitaciones')


# ── HABITACIONES ──

@ns.route('/')
class HabitacionList(Resource):
    @jwt_required()
    def get(self):
        """Listar habitaciones con filtros opcionales."""
        query = Habitacion.query

        # Filtros
        estado = request.args.get('estado')
        piso = request.args.get('piso', type=int)
        tipo_id = request.args.get('tipo_id', type=int)
        activa = request.args.get('activa', type=int)

        if estado:
            query = query.filter_by(estado=estado)
        if piso:
            query = query.filter_by(piso=piso)
        if tipo_id:
            query = query.filter_by(tipo_id=tipo_id)
        if activa is not None:
            query = query.filter_by(activa=bool(activa))

        query = query.order_by(Habitacion.piso, Habitacion.numero)
        return paginate(query, habitaciones_schema)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear nueva habitación."""
        data = request.json
        habitacion = habitacion_schema.load(data, session=db.session)
        db.session.add(habitacion)
        db.session.commit()
        return success_response(habitacion_schema.dump(habitacion), 'Habitación creada.', 201)


@ns.route('/<int:id>')
class HabitacionDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Obtener detalle de una habitación."""
        hab = Habitacion.query.get_or_404(id)
        return success_response(habitacion_schema.dump(hab))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar una habitación."""
        hab = Habitacion.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(hab, key) and key not in ('id',):
                setattr(hab, key, value)
        db.session.commit()
        return success_response(habitacion_schema.dump(hab), 'Habitación actualizada.')


@ns.route('/<int:id>/estado')
class HabitacionEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion', 'housekeeping', 'mantenimiento'])
    def patch(self, id):
        """Cambiar estado de una habitación."""
        hab = Habitacion.query.get_or_404(id)
        data = request.json
        if 'estado' in data:
            hab.estado = data['estado']
        if 'estado_limpieza' in data:
            hab.estado_limpieza = data['estado_limpieza']
        db.session.commit()
        return success_response(habitacion_schema.dump(hab), 'Estado actualizado.')


# ── TIPOS DE HABITACIÓN ──

@ns.route('/tipos')
class TipoHabitacionList(Resource):
    @jwt_required()
    def get(self):
        """Listar tipos de habitación con amenidades."""
        tipos = TipoHabitacion.query.filter_by(activo=True).all()
        return success_response(tipos_habitacion_schema.dump(tipos))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear tipo de habitación."""
        data = request.json
        tipo = tipo_habitacion_schema.load(data, session=db.session)
        db.session.add(tipo)
        db.session.commit()
        return success_response(tipo_habitacion_schema.dump(tipo), 'Tipo creado.', 201)


@ns.route('/tipos/<int:id>')
class TipoHabitacionDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Detalle de tipo de habitación."""
        tipo = TipoHabitacion.query.get_or_404(id)
        return success_response(tipo_habitacion_schema.dump(tipo))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar tipo de habitación."""
        tipo = TipoHabitacion.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(tipo, key) and key not in ('id',):
                setattr(tipo, key, value)
        db.session.commit()
        return success_response(tipo_habitacion_schema.dump(tipo), 'Tipo actualizado.')


# ── AMENIDADES ──

@ns.route('/amenidades')
class AmenidadList(Resource):
    @jwt_required()
    def get(self):
        """Listar amenidades."""
        amenidades = Amenidad.query.all()
        return success_response(amenidades_schema.dump(amenidades))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear amenidad."""
        data = request.json
        amenidad = amenidad_schema.load(data, session=db.session)
        db.session.add(amenidad)
        db.session.commit()
        return success_response(amenidad_schema.dump(amenidad), 'Amenidad creada.', 201)
