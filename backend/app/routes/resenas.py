"""
Rutas de Reseñas — CRUD + respuestas.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.resena import Resena
from app.schemas.resena_schema import resena_schema, resenas_schema
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('resenas', description='Reseñas y satisfacción')


@ns.route('/')
class ResenaList(Resource):
    @jwt_required()
    def get(self):
        """Listar reseñas."""
        query = Resena.query
        publicada = request.args.get('publicada', type=int)
        if publicada is not None:
            query = query.filter_by(publicada=bool(publicada))
        query = query.order_by(Resena.creado_en.desc())
        return paginate(query, resenas_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Crear reseña."""
        data = request.json
        resena = resena_schema.load(data, session=db.session)
        db.session.add(resena)
        db.session.commit()
        return success_response(resena_schema.dump(resena), 'Reseña creada.', 201)


@ns.route('/<int:id>')
class ResenaDetail(Resource):
    @jwt_required()
    def get(self, id):
        """Detalle de reseña."""
        resena = Resena.query.get_or_404(id)
        return success_response(resena_schema.dump(resena))


@ns.route('/<int:id>/respuesta')
class ResenaRespuesta(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self, id):
        """Responder a una reseña."""
        resena = Resena.query.get_or_404(id)
        data = request.json
        claims = get_jwt()

        resena.respuesta = data.get('respuesta')
        resena.respondido_por = claims.get('empleado_id')
        db.session.commit()

        return success_response(resena_schema.dump(resena), 'Respuesta publicada.')
