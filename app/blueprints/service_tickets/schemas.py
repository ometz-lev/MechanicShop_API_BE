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

#Schema for editing service tickets (adding or removing mechanics)
class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Integer(), required=True)
    remove_mechanic_ids = fields.List(fields.Integer(), required=True)

    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')


 #Create instances of the schemas for use in routes 
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

edit_service_ticket_schema = EditServiceTicketSchema()