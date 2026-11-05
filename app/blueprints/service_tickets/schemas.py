from app.extensions import ma
from app.models import Service_ticket
from marshmallow import fields

# Schema for serializing and deserializing ServiceTicket objects
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(required=True)

    class Meta:
        model = Service_ticket
        load_instance = False
        include_fk = True

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)