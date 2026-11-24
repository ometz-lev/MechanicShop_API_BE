#This file defines the schema for serializing and deserializing Customer objects using Marshmallow. It includes a CustomerSchema class that specifies the model to be used and whether to load instances. 
#Additionally, it creates instances of the schema for single and multiple customers, as well as a schema for login purposes that only includes the email and password fields.
from app.extensions import ma
from app.models import Customer
from marshmallow import fields

# Schema for serializing and deserializing Customer objects
class CustomerSchema(ma.SQLAlchemyAutoSchema):

    # Accept password during creation but never return it
    password = fields.String(required=True, load_only=True)

    class Meta:
        model = Customer
        load_instance = False
        exclude = ('password_hash',)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# Schema for customer login
class CustomerLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

customer_login_schema = CustomerLoginSchema()