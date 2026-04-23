"""
Rutas de Restaurante — Menú + pedidos + room service.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.restaurante import CategoriaMenu, ProductoMenu, PedidoRestaurante, ItemPedido
from app.schemas.restaurante_schema import (
    categoria_menu_schema, categorias_menu_schema,
    producto_menu_schema, productos_menu_schema,
    pedido_schema, pedidos_schema, item_pedido_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('restaurante', description='Restaurante y room service')


# ── MENÚ ──

@ns.route('/menu/categorias')
class CategoriaList(Resource):
    @jwt_required()
    def get(self):
        """Listar categorías del menú."""
        cats = CategoriaMenu.query.all()
        return success_response(categorias_menu_schema.dump(cats))

    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante'])
    def post(self):
        """Crear categoría."""
        data = request.json
        cat = categoria_menu_schema.load(data, session=db.session)
        db.session.add(cat)
        db.session.commit()
        return success_response(categoria_menu_schema.dump(cat), 'Categoría creada.', 201)


@ns.route('/menu/productos')
class ProductoList(Resource):
    @jwt_required()
    def get(self):
        """Listar productos del menú."""
        query = ProductoMenu.query
        categoria_id = request.args.get('categoria_id', type=int)
        disponible = request.args.get('disponible', type=int)
        minibar = request.args.get('minibar', type=int)

        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        if disponible is not None:
            query = query.filter_by(disponible=bool(disponible))
        if minibar is not None:
            query = query.filter_by(es_minibar=bool(minibar))

        return success_response(productos_menu_schema.dump(query.all()))

    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante'])
    def post(self):
        """Crear producto."""
        data = request.json
        prod = producto_menu_schema.load(data, session=db.session)
        db.session.add(prod)
        db.session.commit()
        return success_response(producto_menu_schema.dump(prod), 'Producto creado.', 201)


@ns.route('/menu/productos/<int:id>')
class ProductoDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante'])
    def put(self, id):
        """Actualizar producto."""
        prod = ProductoMenu.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(prod, key) and key not in ('id',):
                setattr(prod, key, value)
        db.session.commit()
        return success_response(producto_menu_schema.dump(prod), 'Producto actualizado.')


# ── PEDIDOS ──

@ns.route('/pedidos')
class PedidoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante', 'recepcion'])
    def get(self):
        """Listar pedidos."""
        query = PedidoRestaurante.query
        estado = request.args.get('estado')
        tipo = request.args.get('tipo')

        if estado:
            query = query.filter_by(estado=estado)
        if tipo:
            query = query.filter_by(tipo=tipo)

        query = query.order_by(PedidoRestaurante.creado_en.desc())
        return paginate(query, pedidos_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante', 'recepcion'])
    def post(self):
        """Crear pedido."""
        data = request.json
        claims = get_jwt()

        pedido = PedidoRestaurante(
            reserva_id=data.get('reserva_id'),
            huesped_id=data.get('huesped_id'),
            tipo=data.get('tipo', 'restaurante'),
            mesa=data.get('mesa'),
            atendido_por=claims.get('empleado_id'),
        )
        db.session.add(pedido)
        db.session.flush()

        # Agregar ítems
        total = 0
        for item_data in data.get('items', []):
            producto = ProductoMenu.query.get(item_data['producto_id'])
            if not producto:
                continue
            cantidad = item_data.get('cantidad', 1)
            subtotal = float(producto.precio) * cantidad

            item = ItemPedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unit=float(producto.precio),
                subtotal=subtotal,
                notas=item_data.get('notas')
            )
            db.session.add(item)
            total += subtotal

        pedido.total = total
        db.session.commit()
        return success_response(pedido_schema.dump(pedido), 'Pedido creado.', 201)


@ns.route('/pedidos/<int:id>/estado')
class PedidoEstado(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante'])
    def patch(self, id):
        """Cambiar estado del pedido."""
        pedido = PedidoRestaurante.query.get_or_404(id)
        data = request.json
        if 'estado' in data:
            pedido.estado = data['estado']
        db.session.commit()
        return success_response(pedido_schema.dump(pedido), 'Pedido actualizado.')


@ns.route('/pedidos/<int:id>/items')
class PedidoItems(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'restaurante'])
    def post(self, id):
        """Agregar ítems a un pedido existente."""
        pedido = PedidoRestaurante.query.get_or_404(id)
        data = request.json

        producto = ProductoMenu.query.get(data['producto_id'])
        if not producto:
            return error_response('Producto no encontrado.', 404)

        cantidad = data.get('cantidad', 1)
        subtotal = float(producto.precio) * cantidad

        item = ItemPedido(
            pedido_id=id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unit=float(producto.precio),
            subtotal=subtotal,
            notas=data.get('notas')
        )
        db.session.add(item)
        pedido.total = float(pedido.total) + subtotal
        db.session.commit()

        return success_response(pedido_schema.dump(pedido), 'Ítem agregado.')
