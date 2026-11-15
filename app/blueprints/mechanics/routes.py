# This file contains the routes for the mechanics blueprint, which handles CRUD operations.
from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic
from app.blueprints.mechanics import mechanics_bp
from app.extensions import limiter, cache, db


# POST /mechanics - Create a new mechanic
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Mechanic with this email already exists."}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# GET /mechanics - Retrieve all mechanics
@mechanics_bp.route('/', methods = ['GET'])
@cache.cached(timeout=60)                                # Cache the response for 60 seconds
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200


# GET /mechanics/<int:id> - Retrieve a specific mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# PUT /mechanics/<int:id> - Update a specific mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        updated_data = mechanic_schema.load(request.json, partial=True)  # Allow partial updates
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# DELETE /mechanics/<int:id> - Delete a specific mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("5 per hour", override_defaults=False)                                  # Limit to 5 requests per hour to prevent accidental or malicious deletions
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id:{mechanic_id}, deleted successfully."}), 200


# Create a list of mechanics sorted in order of who worked on the most service tickets, along with the number of service tickets they worked on.
@mechanics_bp.route('/top', methods=['GET'])
def get_top_mechanics():
    query = select(Mechanic)
    top_mechanics = db.session.execute(query).scalars().all()

    #Sort the mechanics by number of service tickets in descending order
    top_mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)

    #Return the sorted list of mechanics along with the number of service tickets they have worked on
    results = [{
        "mechanic_id": mechanic.id,
        "name": mechanic.name,
        "email": mechanic.email,
        "service_ticket_count": len(mechanic.service_tickets)
    } for mechanic in top_mechanics]
    
    return jsonify(results), 200


# Search for mechanics by name, returning a list of matching mechanics.
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanics():
    name = request.args.get('name')
    query = select(Mechanic)

    if name:
        query = query.where(Mechanic.name.contains(name))

    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200
