from app.extensions import ma
from app.models.notificacion import PlantillaNotificacion, Notificacion


class PlantillaNotificacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PlantillaNotificacion
        load_instance = True

    id = ma.auto_field(dump_only=True)


class NotificacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notificacion
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)
    enviado_en = ma.auto_field(dump_only=True)


plantilla_schema = PlantillaNotificacionSchema()
plantillas_schema = PlantillaNotificacionSchema(many=True)
notificacion_schema = NotificacionSchema()
notificaciones_schema = NotificacionSchema(many=True)
