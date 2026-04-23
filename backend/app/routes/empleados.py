"""
Rutas de Empleados — CRUD + departamentos + cargos + turnos + usuarios.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.empleado import Empleado, Departamento, Cargo, UsuarioSistema, Turno
from app.schemas.empleado_schema import (
    empleado_schema, empleados_schema, empleado_list_schema,
    departamento_schema, departamentos_schema,
    cargo_schema, cargos_schema,
    usuario_schema, usuarios_schema,
    turno_schema, turnos_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('empleados', description='Gestión de empleados')


# ── EMPLEADOS ──

@ns.route('/')
class EmpleadoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Listar empleados."""
        query = Empleado.query
        activo = request.args.get('activo', type=int)
        depto_id = request.args.get('departamento_id', type=int)

        if activo is not None:
            query = query.filter_by(activo=bool(activo))
        if depto_id:
            query = query.join(Cargo).filter(Cargo.departamento_id == depto_id)

        query = query.order_by(Empleado.apellido)
        return paginate(query, empleado_list_schema)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear empleado."""
        data = request.json
        empleado = empleado_schema.load(data, session=db.session)
        db.session.add(empleado)
        db.session.commit()
        return success_response(empleado_schema.dump(empleado), 'Empleado creado.', 201)


@ns.route('/<int:id>')
class EmpleadoDetail(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self, id):
        """Detalle de empleado."""
        empleado = Empleado.query.get_or_404(id)
        return success_response(empleado_schema.dump(empleado))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self, id):
        """Actualizar empleado."""
        empleado = Empleado.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(empleado, key) and key not in ('id',):
                setattr(empleado, key, value)
        db.session.commit()
        return success_response(empleado_schema.dump(empleado), 'Empleado actualizado.')


# ── DEPARTAMENTOS ──

@ns.route('/departamentos')
class DepartamentoList(Resource):
    @jwt_required()
    def get(self):
        """Listar departamentos."""
        deptos = Departamento.query.all()
        return success_response(departamentos_schema.dump(deptos))

    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """Crear departamento."""
        data = request.json
        depto = departamento_schema.load(data, session=db.session)
        db.session.add(depto)
        db.session.commit()
        return success_response(departamento_schema.dump(depto), 'Departamento creado.', 201)


# ── CARGOS ──

@ns.route('/cargos')
class CargoList(Resource):
    @jwt_required()
    def get(self):
        """Listar cargos."""
        cargos_list = Cargo.query.all()
        return success_response(cargos_schema.dump(cargos_list))

    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """Crear cargo."""
        data = request.json
        cargo_obj = cargo_schema.load(data, session=db.session)
        db.session.add(cargo_obj)
        db.session.commit()
        return success_response(cargo_schema.dump(cargo_obj), 'Cargo creado.', 201)


# ── USUARIOS DEL SISTEMA ──

@ns.route('/usuarios')
class UsuarioList(Resource):
    @jwt_required()
    @role_required(['admin'])
    def get(self):
        """Listar usuarios del sistema."""
        usuarios = UsuarioSistema.query.all()
        return success_response(usuarios_schema.dump(usuarios))

    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """Crear usuario del sistema."""
        data = request.json
        usuario = UsuarioSistema(
            empleado_id=data['empleado_id'],
            username=data['username'],
            rol=data['rol']
        )
        usuario.set_password(data['password'])
        db.session.add(usuario)
        db.session.commit()
        return success_response(usuario_schema.dump(usuario), 'Usuario creado.', 201)


@ns.route('/usuarios/<int:id>')
class UsuarioDetail(Resource):
    @jwt_required()
    @role_required(['admin'])
    def put(self, id):
        """Actualizar usuario (rol, activo)."""
        usuario = UsuarioSistema.query.get_or_404(id)
        data = request.json
        if 'rol' in data:
            usuario.rol = data['rol']
        if 'activo' in data:
            usuario.activo = data['activo']
        if 'password' in data:
            usuario.set_password(data['password'])
        db.session.commit()
        return success_response(usuario_schema.dump(usuario), 'Usuario actualizado.')


# ── TURNOS ──

@ns.route('/turnos')
class TurnoList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Listar turnos (filtro por fecha y empleado)."""
        query = Turno.query
        fecha = request.args.get('fecha')
        empleado_id = request.args.get('empleado_id', type=int)

        if fecha:
            query = query.filter_by(fecha=fecha)
        if empleado_id:
            query = query.filter_by(empleado_id=empleado_id)

        query = query.order_by(Turno.fecha.desc(), Turno.hora_entrada)
        return paginate(query, turnos_schema)

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def post(self):
        """Crear turno."""
        data = request.json
        turno = turno_schema.load(data, session=db.session)
        db.session.add(turno)
        db.session.commit()
        return success_response(turno_schema.dump(turno), 'Turno creado.', 201)
