from app.extensions import ma
from app.models.parking import Estacionamiento, UsoParking


class EstacionamientoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Estacionamiento
        load_instance = True

    id = ma.auto_field(dump_only=True)


class UsoParkingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UsoParking
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)


estacionamiento_schema = EstacionamientoSchema()
estacionamientos_schema = EstacionamientoSchema(many=True)
uso_parking_schema = UsoParkingSchema()
usos_parking_schema = UsoParkingSchema(many=True)
