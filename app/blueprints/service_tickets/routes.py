# This file contains the routes for the service tickets blueprint, which handles CRUD operations.
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_ticket, Mechanic, Customer, Inventory, InventoryService
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.inventory.schemas import inventory_services_schema
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.customers import customers_bp
from app.blueprints.inventory import inventory_bp
from app.extensions import limiter, cache, db
from app.utils.util import encode_token, token_required


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


# PUT /service_tickets/<int:id>/assign-mechanic/<int:mechanic_id> - Updates a specific service ticket by assigning a mechanic
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
        return jsonify({"error": "Mechanic is already assigned to this service ticket."}), 409

    try:
        #assign mechanic to service ticket and commit the changes to the database
        service_ticket.mechanics.append(mechanic)        
        db.session.commit()
        return jsonify({
        "message": "Mechanic successfully assigned to service ticket",
        "service_ticket_id": service_ticket.id,
        "mechanic_id": mechanic.id,
        "assigned_mechanics": [
            {
                "mechanic_id": m.id,
                "mechanic_name": m.name,
            } for m in service_ticket.mechanics
        ]
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unable to update mechanic assignment."}), 500


# PUT /service_tickets/<int:id>/remove-mechanic/<int:mechanic_id> - Remove a specific mechanic from a service ticket
# The customer_id is extracted from the token and used to validate that the customer is authorized to remove a mechanic from the service ticket.
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
def remove_mechanic(authenticated_user_id, service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_ticket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    # Verify that the authenticated user can manage this service ticket
    if service_ticket.customer_id != int(authenticated_user_id):
        return jsonify({"error": "You are not authorized to modify this service ticket."}), 403
    
    # Find the mechanic
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    # Check if the mechanic is assigned to the service ticket
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

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to update mechanic assignment."}), 500


# GET /service_tickets - Retrieve all service tickets
@service_tickets_bp.route('/', methods = ['GET'])
@cache.cached(timeout=60)                                         # Cache the response for 60 seconds
def get_service_tickets():
    query = select(Service_ticket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200


# GET /service-tickets/mechanics - Retrieve all mechanics assigned to all service tickets
@service_tickets_bp.route('/mechanics', methods=['GET'])
@cache.cached(timeout=60)                                         # Cache the response for 60 seconds
def get_all_assigned_mechanics():

    # Retrieve all service tickets
    service_tickets = db.session.scalars(db.select(Service_ticket)).all()

    # Build response
    results = []

    for ticket in service_tickets:
        results.append({
            "service_ticket_id": ticket.id,
            "vin": ticket.vin,
            "service_desc": ticket.service_desc,
            "customer": {
                "customer_id": ticket.customer.id,
                "name": ticket.customer.name,
                "email": ticket.customer.email,
                "phone": ticket.customer.phone
                } if ticket.customer else None,
            "mechanics": [
                {
                    "mechanic_id": mechanic.id,
                    "name": mechanic.name,
                    "email": mechanic.email,
                    "phone": mechanic.phone
                }
                for mechanic in ticket.mechanics
            ]
        })

    return jsonify(results), 200


#Create a route that requires a token to access, and returns the service tickets associated with the authenticated customer
@service_tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(authenticated_user_id):
    query = select(Service_ticket).where(Service_ticket.customer_id == authenticated_user_id)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200


# PUT /service_tickets/<int:id>/edit - Edit a specific service ticket by adding or removing mechanics
@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@limiter.limit("10 per hour")                                                       # Prevent excessive updates
def edit_service_ticket(ticket_id):

    ticket = db.session.get(Service_ticket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    try:
        edit_data = edit_service_ticket_schema.load(request.get_json())

    except ValidationError as e:
        return jsonify(e.messages), 400

    add_mechanic_ids = edit_data.get('add_mechanic_ids', [])
    remove_mechanic_ids = edit_data.get('remove_mechanic_ids', [])

    try:
        # Look up mechanics to add and remove
        mechanics_to_add = db.session.query(Mechanic).filter(Mechanic.id.in_(add_mechanic_ids)).all()
        mechanics_to_remove = db.session.query(Mechanic).filter(Mechanic.id.in_(remove_mechanic_ids)).all()

        # Check that all mechanics to add exist
        found_mechanic_ids = {m.id for m in mechanics_to_add}

        if not set(add_mechanic_ids).issubset(found_mechanic_ids):
            return jsonify({"error": "One or more mechanics to add do not exist."}), 404

        # Check that all mechanics to remove exist
        if not set(remove_mechanic_ids).issubset({m.id for m in mechanics_to_remove}):
            return jsonify({"error": "One or more mechanics to remove do not exist."}), 404

        # Add mechanics to the service ticket
        for mechanic in mechanics_to_add:
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

        # Remove mechanics from the service ticket
        for mechanic in mechanics_to_remove:
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic) 

        db.session.commit()

        # Return updated service ticket information
        return jsonify({
            "service_ticket_id": ticket.id,
            "vin": ticket.vin,
            "service_desc": ticket.service_desc,

            "customer": {
                "customer_id": ticket.customer.id,
                "name": ticket.customer.name,
                "email": ticket.customer.email,
                "phone": ticket.customer.phone
            } if ticket.customer else None,

            "mechanics": [
                {
                    "mechanic_id": mechanic.id,
                    "name": mechanic.name,
                    "email": mechanic.email,
                    "phone": mechanic.phone
                }
                for mechanic in ticket.mechanics
            ]

        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unable to update service ticket."}), 500

# Delete a specific service ticket by ID
@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@limiter.limit('10 per hour')                                                           # Protects against repeated deletion attempts
def delete_service_ticket(ticket_id):
    service_ticket = db.session.get(Service_ticket, ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket {ticket_id} deleted successfully."}), 200


## Create a route that adds a single inventory item to a service ticket. 
@service_tickets_bp.route('/<int:ticket_id>/inventory', methods=['POST'])
def add_inventory_to_service_ticket(ticket_id):

    data = request.get_json(silent=True) or {}

    inventory_id = data.get('inventory_id')
    quantity = data.get('quantity', 1)

    #Validate required data
    if inventory_id is None:
        return jsonify({'error': "Inventory id is required."}), 400

    if isinstance(quantity,bool) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer."}), 400

    # Find the service ticket
    service_ticket = db.session.get(Service_ticket, ticket_id)

    if not service_ticket:
        return jsonify({'error': "Service Ticket not found."}), 404

    # Find the inventory item
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({'error': "Inventory not found."}), 404

    # Create the InventoryService record
    inventory_service = InventoryService(
        inventory = inventory,
        service_ticket = service_ticket,
        name = inventory.name,
        price = inventory.price,
        quantity = quantity

    )

    db.session.add(inventory_service)
    db.session.commit()

    return jsonify({
        "message": "Inventory item successfully added to service ticket.",
        "inventory_service": {
            "id": inventory_service.id,
            "inventory_id": inventory_service.inventory_id,
            "service_ticket_id": inventory_service.service_ticket_id,
            "name": inventory_service.name,
            "price": inventory_service.price,
            "quantity": inventory_service.quantity
        }
    }), 201


## GET all inventory assigned to a service ticket
@service_tickets_bp.route('/<int:ticket_id>/inventory', methods=['GET'])
def get_ticket_inventory(ticket_id):

    service_ticket = db.session.get(Service_ticket, ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    inventory_services = db.session.execute(
        db.select(InventoryService).where(
            InventoryService.service_ticket_id == ticket_id
        )
    ).scalars().all()

    return inventory_services_schema.jsonify(inventory_services), 200