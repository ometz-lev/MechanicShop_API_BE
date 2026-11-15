#This file defines the schema for serializing and deserializing Customer objects using Marshmallow. It includes a CustomerSchema class that specifies the model to be used and whether to load instances. 
#Additionally, it creates instances of the schema for single and multiple customers, as well as a schema for login purposes that only includes the email and password fields.
from app.extensions import ma
from app.models import Customer

# Schema for serializing and deserializing Customer objects
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = False

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(only=("email", "password"))