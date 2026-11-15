# This file contains the routes for the service tickets blueprint, which handles CRUD operations.
from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_ticket, Inventory
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.inventory import inventory_bp
from app.extensions import limiter, cache, db

# POST /inventories - Create a new inventory item
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")                                   # Limit to 10 requests per hour
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Inventory).where(Inventory.name == inventory_data['name'])
    existing_inventory = db.session.execute(query).scalars().first()
    if existing_inventory:
        return jsonify({"error": "Inventory item with this name already exists."}), 400

    new_inventory = Inventory(**inventory_data)
    db.session.add(new_inventory)
    db.session.commit()
    return inventory_schema.jsonify(new_inventory), 201


# GET /inventories - Retrieve all inventory items
@inventory_bp.route('/', methods = ['GET'])
@cache.cached(timeout=60)                                         # Cache the response for 60 seconds
def get_inventories():
    query = select(Inventory)
    inventories = db.session.execute(query).scalars().all()

    return inventories_schema.jsonify(inventories), 200


# GET /inventory/<int:id> - Retrieve a specific inventory by ID
@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if inventory:
        return inventory_schema.jsonify(inventory), 200
    return jsonify({"error": "Inventory item not found."}), 404


# PUT /inventory/<int:id> - Update a specific inventory by ID
@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory item not found."}), 404

    try:
        inventory_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in inventory_data.items():
        setattr(inventory, key, value)

    db.session.commit()
    return inventory_schema.jsonify(inventory), 200


# DELETE /inventory/<int:id> - Delete a specific inventory by ID
@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory item not found."}), 404

    db.session.delete(inventory)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted inventory item {inventory_id}"}), 200