from app.extensions import db


class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tabla = db.Column(db.String(60), nullable=False)
    operacion = db.Column(
        db.Enum('INSERT', 'UPDATE', 'DELETE', name='op_auditoria_enum'),
        nullable=False
    )
    registro_id = db.Column(db.Integer, nullable=False)
    datos_antes = db.Column(db.JSON)
    datos_despues = db.Column(db.JSON)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios_sistema.id'))
    ip = db.Column(db.String(45))
    fecha = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    usuario = db.relationship('UsuarioSistema', backref='auditoria', lazy='joined')

    def __repr__(self):
        return f'<Auditoria {self.tabla} {self.operacion} {self.registro_id}>'
