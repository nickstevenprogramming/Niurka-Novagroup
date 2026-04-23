from app.extensions import db


class OrdenMantenimiento(db.Model):
    __tablename__ = 'ordenes_mantenimiento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habitacion_id = db.Column(db.SmallInteger, db.ForeignKey('habitaciones.id'))
    area = db.Column(db.String(80))
    tipo = db.Column(
        db.Enum('correctivo', 'preventivo', 'emergencia', name='tipo_mant_enum'),
        nullable=False, default='correctivo'
    )
    prioridad = db.Column(
        db.Enum('baja', 'media', 'alta', 'critica', name='prioridad_mant_enum'),
        nullable=False, default='media'
    )
    descripcion = db.Column(db.Text, nullable=False)
    reportado_por = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    asignado_a = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    estado = db.Column(
        db.Enum('abierta', 'en_proceso', 'completada', 'cancelada',
                name='estado_mant_enum'),
        nullable=False, default='abierta'
    )
    fecha_reporte = db.Column(db.DateTime, server_default=db.func.now())
    fecha_inicio = db.Column(db.DateTime)
    fecha_cierre = db.Column(db.DateTime)
    costo_material = db.Column(db.Numeric(10, 2), default=0.00)
    notas_cierre = db.Column(db.Text)

    reportador = db.relationship('Empleado', foreign_keys=[reportado_por],
                                  backref='ordenes_reportadas', lazy='joined')
    tecnico = db.relationship('Empleado', foreign_keys=[asignado_a],
                               backref='ordenes_asignadas', lazy='joined')

    def __repr__(self):
        return f'<OrdenMantenimiento {self.id} {self.prioridad}>'
