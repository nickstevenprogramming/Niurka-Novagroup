from app.extensions import db


class PlantillaNotificacion(db.Model):
    __tablename__ = 'plantillas_notificacion'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(40), nullable=False, unique=True)
    asunto = db.Column(db.String(150))
    cuerpo = db.Column(db.Text, nullable=False)
    canal = db.Column(
        db.Enum('email', 'sms', 'sistema', 'whatsapp', name='canal_notif_enum'),
        nullable=False, default='email'
    )

    def __repr__(self):
        return f'<PlantillaNotificacion {self.codigo}>'


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plantilla_id = db.Column(db.SmallInteger, db.ForeignKey('plantillas_notificacion.id'))
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    huesped_id = db.Column(db.Integer, db.ForeignKey('huespedes.id'))
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    destinatario = db.Column(db.String(150))
    asunto = db.Column(db.String(150))
    mensaje = db.Column(db.Text, nullable=False)
    canal = db.Column(
        db.Enum('email', 'sms', 'sistema', 'whatsapp', name='canal_notif2_enum'),
        nullable=False, default='email'
    )
    estado = db.Column(
        db.Enum('pendiente', 'enviado', 'fallido', name='estado_notif_enum'),
        nullable=False, default='pendiente'
    )
    intentos = db.Column(db.SmallInteger, default=0)
    enviado_en = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    plantilla = db.relationship('PlantillaNotificacion', backref='notificaciones', lazy='joined')
    reserva = db.relationship('Reserva', backref='notificaciones', lazy='joined')
    huesped = db.relationship('Huesped', backref='notificaciones', lazy='joined')

    def __repr__(self):
        return f'<Notificacion {self.id} {self.canal} {self.estado}>'
