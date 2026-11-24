# This file defines the schema for serializing and deserializing Mechanic objects using Marshmallow.
# Also, it creates instances of the schema for single and multiple mechanics, as well as a schema for login purposes that only includes the email and password fields.
from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

# Schema for serializing and deserializing Mechanic objects
class MechanicSchema(ma.SQLAlchemyAutoSchema):

    # Accept password during creation but never return it
    password = fields.String(required=True, load_only=True)

    class Meta:
        model = Mechanic
        load_instance = False
        exclude = ('password_hash',)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

# Schema for mechanic login
class MechanicLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

mechanic_login_schema = MechanicLoginSchema()