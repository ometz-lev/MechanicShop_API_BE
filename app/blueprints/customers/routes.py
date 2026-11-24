# This file contains the routes for the customers blueprint, which handles CRUD operations.
# Password hashing protects customer passwords stored in MySQL
# JWT Authentication generates a token after successful login so the customer can authenticate subsequent API requests.
from .schemas import customer_schema, customers_schema, customer_login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer
from app.blueprints.customers import customers_bp
from app.extensions import limiter, cache, db
from app.utils.util import encode_token, token_required



# POST /customers - Create a new customer
@customers_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")                                   # Limit prevents automated account creation
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)       #handle deserialization and validation of the incoming JSON data  
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if customer already exists
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Customer with this email already exists."}), 400

    # Extract the password
    password = customer_data.pop('password')

    # Create customer without plaintext password
    new_customer = Customer(**customer_data)

    # Hash the password before storing it
    new_customer.set_password(password)

    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# POST /customers/login - Authenticate a customer and return a token
@customers_bp.route("/login", methods=['POST'])
@limiter.limit('5 per minute')                                              # Limit repeated login attempts
def login():
    try:
        credentials = customer_login_schema.load(request.get_json() or {})

    except ValidationError as e:
        return jsonify(e.messages), 400

    # Extract Login credentials
    email = credentials['email']
    password = credentials['password']

    # Query Customer table for a customer with this email
    query =select(Customer).where(Customer.email == email) 
    customer = db.session.execute(query).scalar_one_or_none() 

    # Verify customer and hashed password
    if customer and customer.check_password(password):
        auth_token = encode_token(customer.id, 'customer')

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
@cache.cached(timeout=60, query_string=True)  # Cache the response for 60 seconds
def get_customers():
    page = request.args.get('page')
    per_page = request.args.get('per_page')

    # If no pagination parameter is provided, return all customers
    if page is None and per_page is None:
        query = select(Customer).order_by(Customer.id)
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers), 200

    # Require both pagination parameters when pagination is used
    if page is None or per_page is None:
        return jsonify({
            "error": "Both page and per_page parameters are required."
        }), 400

    # Validate that pagination parameters are integers
    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        return jsonify({
            "error": "Page and per_page must be valid integers."
        }), 400

    # Validate that pagination values are positive
    if page < 1 or per_page < 1:
        return jsonify({
            "error": "Page and per_page must be greater than zero."
        }), 400

    # Limit the maximum number of records returned per page
    if per_page > 20:
        return jsonify({
            "error": "per_page cannot exceed 20."
        }), 400

    # Retrieve paginated customers
    query = select(Customer).order_by(Customer.id)
    customers = db.paginate(
        query,
        page=page,
        per_page=per_page,
        error_out=False
    )

    return customers_schema.jsonify(customers.items), 200
    

# GET /customers/<int:id> - Retrieve a specific customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer =db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# PUT /customers Requires a token to access, and the token must belong to the customer being updated.
# The customer_id is extracted from the token and used to validate that the customer is authorized to update their own information.
@customers_bp.route('/', methods=['PUT'])
@token_required
@limiter.limit('10 per minute')                                         # Prevent excessive updates
def update_customer(authenticated_user_id):
    customer = db.session.get(Customer, authenticated_user_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        updated_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in updated_data.items():
        if key == 'password':
            customer.set_password(value)
        else:
            setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# Use the token_required decorator to protect this route, ensuring that only authenticated user can delete their account.
@customers_bp.route('/', methods=['DELETE'])
@token_required
def delete_user(authenticated_user_id): #Receiving customer_id from the token
    query = select(Customer).where(Customer.id == authenticated_user_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Succesfully deleted customer {authenticated_user_id}"}), 200