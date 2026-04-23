"""
Rutas de Huéspedes — CRUD + búsqueda + VIP + blacklist.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.huesped import Huesped, Pais
from app.schemas.huesped_schema import (
    huesped_schema, huespedes_schema, huesped_list_schema, paises_schema
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('huespedes', description='Gestión de huéspedes')


@ns.route('/')
class HuespedList(Resource):
    @jwt_required()
    def get(self):
        """Listar huéspedes con filtros y búsqueda."""
        query = Huesped.query

        # Búsqueda por nombre/apellido/email
        buscar = request.args.get('buscar')
        if buscar:
            patron = f'%{buscar}%'
            query = query.filter(
                db.or_(
                    Huesped.nombre.ilike(patron),
                    Huesped.apellido.ilike(patron),
                    Huesped.email.ilike(patron),
                    Huesped.num_documento.ilike(patron)
                )
            )

        # Filtros
        nivel_vip = request.args.get('nivel_vip', type=int)
        pais_id = request.args.get('pais_id')
        blacklist = request.args.get('blacklist', type=int)

        if nivel_vip is not None:
            query = query.filter_by(nivel_vip=nivel_vip)
        if pais_id:
            query = query.filter_by(pais_id=pais_id)
        if blacklist is not None:
            query = query.filter_by(blacklist=bool(blacklist))

        query = query.order_by(Huesped.apellido, Huesped.nombre)
        return paginate(query, huesped_list_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Registrar nuevo huésped."""
        data = request.json
        huesped = huesped_schema.load(data, session=db.session)
        db.session.add(huesped)
        db.session.commit()
        return success_response(huesped_schema.dump(huesped), 'Huésped registrado.', 201)


@ns.route('/<int:id>')
class HuespedDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Detalle de huésped con historial de reservas."""
        huesped = Huesped.query.get_or_404(id)
        result = huesped_schema.dump(huesped)

        # Agregar historial de reservas
        from app.schemas.reserva_schema import reserva_list_schema
        reservas = huesped.reservas.order_by(db.text('fecha_entrada DESC')).limit(20).all()
        result['historial_reservas'] = reserva_list_schema.dump(reservas)

        return success_response(result)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def put(self, id):
        """Actualizar datos de huésped."""
        huesped = Huesped.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(huesped, key) and key not in ('id', 'creado_en'):
                setattr(huesped, key, value)
        db.session.commit()
        return success_response(huesped_schema.dump(huesped), 'Huésped actualizado.')


@ns.route('/<int:id>/vip')
class HuespedVIP(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def patch(self, id):
        """Cambiar nivel VIP de un huésped."""
        huesped = Huesped.query.get_or_404(id)
        data = request.json
        if 'nivel_vip' not in data:
            return error_response('Se requiere nivel_vip (0-3).', 400)
        huesped.nivel_vip = data['nivel_vip']
        db.session.commit()
        return success_response(message=f'Nivel VIP actualizado a {huesped.nivel_vip}.')


@ns.route('/<int:id>/blacklist')
class HuespedBlacklist(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def patch(self, id):
        """Agregar/quitar de blacklist."""
        huesped = Huesped.query.get_or_404(id)
        data = request.json
        huesped.blacklist = data.get('blacklist', not huesped.blacklist)
        db.session.commit()
        estado = 'agregado a' if huesped.blacklist else 'removido de'
        return success_response(message=f'Huésped {estado} la blacklist.')


@ns.route('/paises')
class PaisList(Resource):
    @jwt_required()
    def get(self):
        """Listar países disponibles."""
        paises = Pais.query.order_by(Pais.nombre).all()
        return success_response(paises_schema.dump(paises))
