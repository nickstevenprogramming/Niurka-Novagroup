"""
Rutas de Inventario — Stock + movimientos.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.inventario import CategoriaInventario, Inventario, MovimientoInventario
from app.schemas.inventario_schema import (
    cat_inventario_schema, cats_inventario_schema,
    inventario_schema, inventarios_schema,
    movimiento_schema, movimientos_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('inventario', description='Control de inventario')


@ns.route('/categorias')
class CategoriaList(Resource):
    @jwt_required()
    def get(self):
        """Listar categorías de inventario."""
        cats = CategoriaInventario.query.all()
        return success_response(cats_inventario_schema.dump(cats))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear categoría."""
        data = request.json
        cat = cat_inventario_schema.load(data, session=db.session)
        db.session.add(cat)
        db.session.commit()
        return success_response(cat_inventario_schema.dump(cat), 'Categoría creada.', 201)


@ns.route('/items')
class InventarioList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def get(self):
        """Listar ítems de inventario."""
        query = Inventario.query
        categoria_id = request.args.get('categoria_id', type=int)
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        return paginate(query, inventarios_schema)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear ítem de inventario."""
        data = request.json
        item = inventario_schema.load(data, session=db.session)
        db.session.add(item)
        db.session.commit()
        return success_response(inventario_schema.dump(item), 'Ítem creado.', 201)


@ns.route('/items/<int:id>')
class InventarioDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar ítem."""
        item = Inventario.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(item, key) and key not in ('id',):
                setattr(item, key, value)
        db.session.commit()
        return success_response(inventario_schema.dump(item), 'Ítem actualizado.')


@ns.route('/movimientos')
class MovimientoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def get(self):
        """Listar movimientos de inventario."""
        query = MovimientoInventario.query
        item_id = request.args.get('item_id', type=int)
        if item_id:
            query = query.filter_by(item_id=item_id)
        query = query.order_by(MovimientoInventario.movido_en.desc())
        return paginate(query, movimientos_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def post(self):
        """Registrar movimiento (entrada/salida/ajuste) y actualizar stock."""
        data = request.json
        claims = get_jwt()

        item = Inventario.query.get(data.get('item_id'))
        if not item:
            return error_response('Ítem no encontrado.', 404)

        cantidad = float(data['cantidad'])
        tipo = data['tipo']

        # Actualizar stock
        if tipo == 'entrada':
            item.stock_actual = float(item.stock_actual) + cantidad
        elif tipo == 'salida':
            if float(item.stock_actual) < cantidad:
                return error_response('Stock insuficiente.', 400)
            item.stock_actual = float(item.stock_actual) - cantidad
        elif tipo == 'ajuste':
            item.stock_actual = cantidad  # ajuste = nuevo valor absoluto

        mov = MovimientoInventario(
            item_id=data['item_id'],
            tipo=tipo,
            cantidad=cantidad,
            motivo=data.get('motivo'),
            empleado_id=claims.get('empleado_id'),
            referencia_id=data.get('referencia_id')
        )
        db.session.add(mov)
        db.session.commit()

        return success_response(movimiento_schema.dump(mov), f'Movimiento registrado. Stock actual: {item.stock_actual}', 201)


@ns.route('/alertas-stock')
class AlertaStock(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'housekeeping'])
    def get(self):
        """Ítems con stock por debajo del mínimo."""
        items = Inventario.query.filter(
            Inventario.stock_actual <= Inventario.stock_minimo,
            Inventario.activo == True
        ).all()
        return success_response(inventarios_schema.dump(items))
