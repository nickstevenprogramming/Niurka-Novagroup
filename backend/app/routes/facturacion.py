"""
Rutas de Facturación — Facturas + pagos + cargos.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.facturacion import Factura, ItemFactura, Pago, CargoHabitacion, MetodoPago
from app.schemas.facturacion_schema import (
    factura_schema, facturas_schema, item_factura_schema,
    pago_schema, pagos_schema, metodos_pago_schema,
    cargo_habitacion_schema, cargos_habitacion_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('facturacion', description='Facturación y pagos')


@ns.route('/facturas')
class FacturaList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def get(self):
        """Listar facturas."""
        query = Factura.query
        estado = request.args.get('estado')
        reserva_id = request.args.get('reserva_id', type=int)

        if estado:
            query = query.filter_by(estado=estado)
        if reserva_id:
            query = query.filter_by(reserva_id=reserva_id)

        query = query.order_by(Factura.creado_en.desc())
        return paginate(query, facturas_schema)


@ns.route('/facturas/<int:id>')
class FacturaDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def get(self, id):
        """Detalle de factura con ítems y pagos."""
        factura = Factura.query.get_or_404(id)
        return success_response(factura_schema.dump(factura))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def patch(self, id):
        """Actualizar estado de factura."""
        factura = Factura.query.get_or_404(id)
        data = request.json
        if 'estado' in data:
            factura.estado = data['estado']
        db.session.commit()
        return success_response(factura_schema.dump(factura), 'Factura actualizada.')


@ns.route('/facturas/<int:id>/items')
class FacturaItems(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self, id):
        """Agregar ítem a factura."""
        factura = Factura.query.get_or_404(id)
        data = request.json
        item = ItemFactura(
            factura_id=id,
            descripcion=data['descripcion'],
            cantidad=data.get('cantidad', 1),
            precio_unit=data['precio_unit'],
            subtotal=float(data.get('cantidad', 1)) * float(data['precio_unit']),
            tipo=data.get('tipo', 'otro')
        )
        db.session.add(item)

        # Recalcular total
        factura.subtotal = float(factura.subtotal) + item.subtotal
        factura.total = float(factura.subtotal) + float(factura.impuesto) - float(factura.descuento)

        db.session.commit()
        return success_response(factura_schema.dump(factura), 'Ítem agregado.')


@ns.route('/pagos')
class PagoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def get(self):
        """Listar pagos."""
        query = Pago.query
        factura_id = request.args.get('factura_id', type=int)
        if factura_id:
            query = query.filter_by(factura_id=factura_id)
        query = query.order_by(Pago.pagado_en.desc())
        return paginate(query, pagos_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Registrar un pago."""
        data = request.json
        claims = get_jwt()

        factura = Factura.query.get(data['factura_id'])
        if not factura:
            return error_response('Factura no encontrada.', 404)

        pago = Pago(
            factura_id=data['factura_id'],
            metodo_id=data['metodo_id'],
            monto=data['monto'],
            referencia=data.get('referencia'),
            moneda=data.get('moneda', 'DOP'),
            tasa_cambio=data.get('tasa_cambio', 1.0),
            monto_usd=data.get('monto_usd'),
            es_deposito=data.get('es_deposito', False),
            registrado_por=claims.get('empleado_id'),
            notas=data.get('notas')
        )
        db.session.add(pago)

        # Auto-marcar factura como pagada si saldo = 0
        db.session.flush()
        if factura.saldo <= 0:
            factura.estado = 'pagada'

        db.session.commit()
        return success_response(pago_schema.dump(pago), 'Pago registrado.', 201)


@ns.route('/metodos-pago')
class MetodoPagoList(Resource):
    @jwt_required()
    def get(self):
        """Listar métodos de pago."""
        metodos = MetodoPago.query.all()
        return success_response(metodos_pago_schema.dump(metodos))


@ns.route('/cargos-habitacion')
class CargoHabitacionList(Resource):
    @jwt_required()
    def get(self):
        """Listar cargos a habitación."""
        query = CargoHabitacion.query
        reserva_id = request.args.get('reserva_id', type=int)
        if reserva_id:
            query = query.filter_by(reserva_id=reserva_id)
        return paginate(query, cargos_habitacion_schema)

    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion', 'restaurante'])
    def post(self):
        """Registrar cargo a habitación (minibar, room service, etc.)."""
        data = request.json
        claims = get_jwt()
        cargo = CargoHabitacion(
            registrado_por=claims.get('empleado_id'),
            **data
        )
        db.session.add(cargo)
        db.session.commit()
        return success_response(cargo_habitacion_schema.dump(cargo), 'Cargo registrado.', 201)
