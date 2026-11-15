# This file contains the routes for the customers blueprint, which handles CRUD operations.
from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer
from app.blueprints.customers import customers_bp
from app.extensions import limiter, cache, db
from app.utils.util import encode_token, token_required



# POST /customers - Create a new customer
@customers_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")                                   # Limit to 10 requests per hour
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Customer with this email already exists."}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# POST /customers/login - Authenticate a customer and return a token
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting email and password'}), 400
    
    query =select(Customer).where(Customer.email == email) 
    customer = db.session.execute(query).scalar_one_or_none() #Query Customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the email, validate the password
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': "Invalid email or password"}), 401


# GET /customers - Retrieve all customers and support pagination with query parameters `page` and `per_page`.
# If these parameters are not provided, return all customers without pagination.
@customers_bp.route('/', methods = ['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_customers():

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(customers), 200


# GET /customers/<int:id> - Retrieve a specific customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer =db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

# PUT /customers/<int:id> - Update a specific customer by ID. Requires a token to access, and the token must belong to the customer being updated.
# The customer_id is extracted from the token and used to validate that the customer is authorized to update their own information.
@customers_bp.route('/', methods=['PUT'])
@token_required
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        updated_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# Use the token_required decorator to protect this route, ensuring that only authenticated users can delete their account.
@customers_bp.route('/', methods=['DELETE'])
@token_required
def delete_user(customer_id): #Receiving customer_id from the token
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {customer_id}"})