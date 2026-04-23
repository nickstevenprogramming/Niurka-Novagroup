"""
Rutas de Tarifas y Temporadas.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.tarifa import Temporada, TarifaEspecial
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('tarifas', description='Temporadas y tarifas especiales')


@ns.route('/temporadas')
class TemporadaList(Resource):
    @jwt_required()
    def get(self):
        """Listar temporadas."""
        temporadas = Temporada.query.order_by(Temporada.fecha_inicio.desc()).all()
        from app.extensions import ma
        result = [{
            'id': t.id, 'nombre': t.nombre,
            'fecha_inicio': t.fecha_inicio.isoformat(),
            'fecha_fin': t.fecha_fin.isoformat(),
            'multiplicador': float(t.multiplicador),
            'activa': t.activa
        } for t in temporadas]
        return success_response(result)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear temporada."""
        data = request.json
        temporada = Temporada(**data)
        db.session.add(temporada)
        db.session.commit()
        return success_response({'id': temporada.id, 'nombre': temporada.nombre},
                                 'Temporada creada.', 201)


@ns.route('/temporadas/<int:id>')
class TemporadaDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar temporada."""
        temp = Temporada.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(temp, key) and key not in ('id',):
                setattr(temp, key, value)
        db.session.commit()
        return success_response(message='Temporada actualizada.')

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def delete(self, id):
        """Eliminar temporada."""
        temp = Temporada.query.get_or_404(id)
        db.session.delete(temp)
        db.session.commit()
        return success_response(message='Temporada eliminada.')


@ns.route('/especiales')
class TarifaEspecialList(Resource):
    @jwt_required()
    def get(self):
        """Listar tarifas especiales."""
        tarifas = TarifaEspecial.query.filter_by(activa=True).all()
        result = [{
            'id': t.id, 'nombre': t.nombre,
            'tipo_habitacion_id': t.tipo_habitacion_id,
            'temporada_id': t.temporada_id,
            'precio_noche': float(t.precio_noche),
            'min_noches': t.min_noches,
            'incluye_desayuno': t.incluye_desayuno,
        } for t in tarifas]
        return success_response(result)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear tarifa especial."""
        data = request.json
        tarifa = TarifaEspecial(**data)
        db.session.add(tarifa)
        db.session.commit()
        return success_response({'id': tarifa.id, 'nombre': tarifa.nombre},
                                 'Tarifa creada.', 201)


@ns.route('/especiales/<int:id>')
class TarifaEspecialDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar tarifa especial."""
        tarifa = TarifaEspecial.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(tarifa, key) and key not in ('id',):
                setattr(tarifa, key, value)
        db.session.commit()
        return success_response(message='Tarifa actualizada.')
