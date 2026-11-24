# This file contains the routes for the mechanics blueprint, which handles CRUD operations.
# Password hashing protects user passwords stored in MySQL
# JWT Authentication generates a token after successful login so the user can authenticate subsequent API requests.
from .schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic
from app.blueprints.mechanics import mechanics_bp
from app.extensions import limiter, cache, db
from app.utils.util import encode_token, token_required


# POST /mechanics - Create a new mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")                                   # Limit prevents automated account creation
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Mechanic with this email already exists."}), 400

    # Extract the password
    password = mechanic_data.pop('password')

    # Create customer without plaintext password
    new_mechanic = Mechanic(**mechanic_data)

    # Hash the password before storing it
    new_mechanic.set_password(password)

    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


# POST /mechanics/login - Authenticate a mechanic and return a token
@mechanics_bp.route("/login", methods=['POST'])
@limiter.limit('5 per minute')                                              # Limit repeated login attempts
def login():
    try:
        credentials = mechanic_login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    email = credentials['email']
    password = credentials['password']

    # Query Mechanic table for a customer with this email
    query =select(Mechanic).where(Mechanic.email == email) 
    mechanic = db.session.execute(query).scalar_one_or_none() 

    # Verify mechanic and hashed password
    if mechanic and mechanic.check_password(password):
        auth_token = encode_token(mechanic.id,'mechanic')

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': "Invalid email or password"}), 401


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


# PUT /mechanics Update a specific mechanic by ID. Requires a token to access, and the token must belong to the mechanic being updated.
# The mechanic_id is extracted from the token and used to validate that the mechanic is authorized to update their own information.
@mechanics_bp.route('/', methods=['PUT'])
@token_required
@limiter.limit('10 per minute')                                                  # Prevent excessive updates
def update_mechanic(authenticated_user_id):
    mechanic = db.session.get(Mechanic, authenticated_user_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        updated_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        if key == 'password':
            mechanic.set_password(value)
        else:
            setattr(mechanic, key, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# Use the token_required decorator to protect this route, ensuring that only authenticated user can delete their account.
@mechanics_bp.route('/', methods=['DELETE'])
@token_required                                 
def delete_mechanic(authenticated_user_id):
    query = select(Mechanic).where(Mechanic.id == authenticated_user_id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id:{authenticated_user_id}, deleted successfully."}), 200


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
    name = request.args.get('name', '').strip()

    if not name:
        return jsonify({"error": "Please provide a mechanic name to search."}), 400

    query = select(Mechanic).where(
        Mechanic.name.ilike(f'%{name}%')
    )

    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200
