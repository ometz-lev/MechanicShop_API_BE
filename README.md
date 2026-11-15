# MechanicShop_API_BE
# This Mechanic Shop Management API is a RESTful API built with Python and Flask that manages customers, mechanics, 
# inventory and service tickets for an auto repair shop using the Application Factory Pattern.
# The applications uses a MySQL database to store and manage date and SQLAlchemy as the ORM for database interactions.
# It supports CRUD operations and manages relationships between customers, service tickets and mechanics.
# A default rate limit is added to offer blanket protection to all routes. Rate limiters are added to the DELETE routes to 
# prevent accidental deletion of records.
# Use POSTMAN to test CRUD operations

# Features:
# filestructure.txt outlines the structure of the folders and components for the app
# Customer Management: create, get, update and delete records
# Mechanic management: manage mechanic information
# Service ticket management: create, retrieve, update and delete vehicle service tickets
# Inventory management: create, get, update and delete records
# Mechanic assignment: assign mechanics to service tickets
# Mechanic removal: remove mechanics from service tickets without deleting the mechanic record
# Database relationships: implements one-to-many and many-to-many relationships using SQLAlchemy
# Data Validation and Serialization: Uses Marshmallow to validate incoming data and serialize database records
# API Testing: uses Postman to test API endpoints
# Pagination : add pagination to the customers GET route
# Postman Collections

# Database structure - the application uses 3 main database entities: customers, mechanic and service tickets  see models.py
# Database relationships:
# Customer to Service Tickets: One-to-many relationship. A customer can have multiple service tickets
# Service Tickets to Mechanics: Many-to-many relationship. A service ticket can have multiple mechanics, and a mechanic can be assigned to multiple service tickets.
# An association table (service_mechanics) manages the many-to-many relationship between service tickets and mechanics.
# Inventory to Service Tickets: function model for many to many relationship between service tickets and inventory

# Installation and setup:
# Clone the repository  git clone <your-github-repository-url> cd MechanicShop_API_BE
# Create a virtual environment  python -m venv venv
# Activate the virtual environment windows: venv\Scripts\activate   mac/linux: source venv/bin/activate
# install dependencies pip install -r requirements.txt
# Create a config.py file to store SQLALCHEMY_DATABASE_URI and p/s
# Run database
# Start the flask application
# Run python file

# Testing
# API endpoints can be tested using Postman.
# Start the Flask application.
# Open Postman.
# Select the appropriate HTTP method (GET, POST, PUT, DELETE).
# Enter the API endpoint URL.
# Provide a JSON request body when required.
# Click Send and review the response and HTTP status code.
