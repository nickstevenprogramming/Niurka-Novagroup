from app.extensions import ma
from app.models.hotel import Hotel


class HotelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hotel
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    creado_en = ma.auto_field(dump_only=True)


hotel_schema = HotelSchema()
