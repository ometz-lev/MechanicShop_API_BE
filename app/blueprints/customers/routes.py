from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from app.blueprints.customers import customers_bp


# POST /customers - Create a new customer
@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Customer with this email already exists."}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# GET /customers - Retrieve all customers
@customers_bp.route('/', methods = ['GET'])
def get_customers():
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

# PUT /customers/<int:id> - Update a specific customer by ID
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 400

    try:
        updated_data = customer_schema.load(request.json, partial=True)  # Allow partial updates
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE /customers/<int:id> - Delete a specific customer by ID
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id:{customer_id}, deleted successfully."}), 200