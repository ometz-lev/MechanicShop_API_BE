from app.extensions import ma
from app.models import Customer

# Schema for serializing and deserializing Customer objects
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = False

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)