from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_ticket, Mechanic, db
from app.blueprints.service_tickets import service_tickets_bp


# POST /service_tickets - Create a new service ticket
@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Service_ticket).where(Service_ticket.vin == service_ticket_data['vin'],
            Service_ticket.service_date == service_ticket_data['service_date'])
    
    existing_service_ticket = db.session.execute(query).scalars().all()
    if existing_service_ticket:
        return jsonify({"error": "Service ticket with this VIN and date already exists."}), 400

    new_service_ticket = Service_ticket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201


# PUT /service_tickets/<int:id>/assign-mechanic/<int:mechanic_id> - Update a specific service ticket by assigning a mechanic
@service_tickets_bp.route('/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    #Validate that both the service ticket and mechanic exist
    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    # check if the mechanic is already assigned to the service ticket
    if mechanic in service_ticket.mechanics:
        return jsonify({"error": "Mechanic is already assigned to this service ticket."}), 200

    try:
        service_ticket.mechanics.append(mechanic)        #Treat the relationship as a list and append the mechanic to the service ticket's mechanics list
        db.session.commit()
        return jsonify({
        "message": "Mechanic successfully assigned to service ticket",
        "service_ticket_id": service_ticket.id,
        "mechanic_id": mechanic.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# PUT /service_tickets/<int:id>/remove-mechanic/<int:mechanic_id> - Remove a specific mechanic from a service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    #Validate that both the service ticket and mechanic exist
    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    #Check if the mechanic is assigned to the service ticket
    if mechanic not in service_ticket.mechanics:
        return jsonify({"error": "Mechanic is not assigned to this service ticket."}), 404
    try:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({
            "message": "Mechanic successfully removed from service ticket",
            "service_ticket": service_ticket.id,
            "mechanic_id": mechanic.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET /service_tickets - Retrieve all service tickets
@service_tickets_bp.route('/', methods = ['GET'])
def get_service_tickets():
    query = select(Service_ticket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200