# Mechanic Shop Management API
# Project Overview

# The Mechanic Shop Management API is a RESTful backend application built with Python and Flask. It provides functionality for managing customers, mechanics, inventory, and vehicle service tickets for an auto repair shop.

# The application uses the Application Factory Pattern and SQLAlchemy ORM for database management. It supports CRUD operations, authentication, authorization, data validation, and relationships between database entities.

# The API is designed to provide a structured and secure way to manage mechanic shop operations.

# Features:
- Customer Management: Create, retrieve, update, and delete customer records.
- Mechanic Management: Manage mechanic information.
- Service Ticket Management: Create, retrieve, update, and delete vehicle service tickets.
- Inventory Management: Create, retrieve, update, and delete inventory records.
- Mechanic Assignment: Assign mechanics to service tickets.
- Mechanic Removal: Remove mechanics from service tickets without deleting the mechanic record.
- Database Relationships: Implements one-to-many and many-to-many relationships using SQLAlchemy.
- Data Validation and Serialization: Uses Marshmallow to validate incoming data and serialize database records.
- Authentication and Authorization: Uses password hashing and JWT authentication to protect designated API endpoints.
- Rate Limiting: Implements default rate limits across routes, with additional restrictions on DELETE operations to help prevent accidental deletion of records.
- Caching: Uses Flask-Caching to improve API performance.
- Pagination: Implements pagination on the customers GET endpoint.
- API Documentation: Provides interactive API documentation through Swagger UI.
- Unit Testing: Uses Python's unittest framework to test API endpoints and application functionality.
- API Testing: Uses Postman collections to test API requests and responses.

# Technologies Used:
- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- MySQL (local development)
- PostgreSQL (production database)
- Marshmallow
- JWT Authentication
- Flask-Limiter
- Flask-Caching
- Flask-Swagger / Swagger UI
- Postman
- Git and GitHub
- GitHub Actions
- Render
- Gunicorn

# Database Structure and Relationships
- The application uses four primary entities: Customers, Mechanics, Service Tickets, and Inventory.
- Database Relationships
- Customer to Service Tickets: One-to-many relationship. A customer can have multiple service tickets.
- Service Tickets to Mechanics: Many-to-many relationship. A service ticket can have multiple mechanics, and a mechanic can be assigned to multiple service tickets.
- Service Tickets to Inventory: Many-to-many relationship, allowing inventory items to be associated with service tickets.
- Association tables manage the many-to-many relationships.
- Refer to models.py for the database models and relationship definitions.

# Installation and Setup

1. Clone the Repository

git clone <your-github-repository-url>
cd MechanicShop_API_BE

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure Environment Variables

Create a .env file in the project root directory and configure the required environment variables.

For example:

SQLALCHEMY_DATABASE_URI=your_database_connection_string
SECRET_KEY=your_secret_key

Keep sensitive credentials out of source control. The .env file should be excluded from Git using .gitignore.

For production deployment, configure these environment variables through the Render dashboard.

6. Configure the Database

Ensure your local MySQL database is running and that the configured database connection string is correct.

The production application uses a PostgreSQL database hosted on Render.

7. Start the Flask Application

Run the application using the configured development entry point.

# API Documentation
The API uses Swagger UI to provide interactive documentation of available endpoints, request parameters, expected responses, and HTTP status codes.

Once the application is running, access the documentation at:

/api/docs

The Swagger documentation is defined in swagger.yaml.

# API Endpoints

The following are examples of available API operations.
# Customers
Method	Endpoint	Description
POST	/customers/	Register a customer
GET	/customers/	Retrieve customers
POST	/customers/login	Authenticate a customer
DELETE	/customers/	Delete the authenticated customer's account
# Mechanics
Method	Endpoint	Description
POST	/mechanics/	Create a mechanic
GET	/mechanics/	Retrieve mechanics
POST	/mechanics/login	Authenticate a mechanic
# Service Tickets
Method	Endpoint	Description
POST	/service-tickets/	Create a service ticket
GET	/service-tickets/	Retrieve service tickets
PUT	/service-tickets/{ticket_id}	Update a service ticket
DELETE	/service-tickets/{ticket_id}	Delete a service ticket
POST	/service-tickets/{ticket_id}/assign-mechanic/{mechanic_id}	Assign a mechanic
# Inventory
Method	Endpoint	Description
POST	/inventory/	Create an inventory item
GET	/inventory/	Retrieve inventory items
PUT	/inventory/{inventory_id}	Update an inventory item
DELETE	/inventory/{inventory_id}	Delete an inventory item

# Testing

# Postman API Testing
Postman is used to test API endpoints and verify CRUD operations, authentication, and API responses.

To test the endpoints:

Start the Flask application.

Open Postman.

Select the appropriate HTTP method (GET, POST, PUT, DELETE).

Enter the API endpoint URL.

Provide a JSON request body when required.

Include a JWT token in the Authorization header for protected endpoints.

Click Send and review the response and HTTP status code.

Postman collections are included in the repository.

# Unit Testing
Unit tests are implemented using Python's unittest framework to verify the functionality of the API endpoints.

Test files include:

test_customer.py

test_mechanic.py

test_serviceticket.py

test_inventory.py

Additional tests cover authentication and authorization, including operations that require a valid JWT token.

Run the complete test suite using:

python -m unittest discover

# CI/CD Pipeline
This project uses GitHub Actions for Continuous Integration (CI) and Render for Continuous Deployment (CD).

The CI/CD pipeline automates testing and application deployment, helping ensure that code changes are validated before being released.

Continuous Integration – GitHub Actions

GitHub Actions automates the testing process whenever code changes are pushed to the GitHub repository or a pull request is opened, according to the configured workflow triggers.

The CI workflow:

Checks out the latest repository code.

Sets up the Python environment.

Installs the required project dependencies.

Executes the automated unit test suite.

Reports the test results.

This helps identify errors before changes are deployed.

Continuous Deployment – Render

Render hosts the Flask REST API and the production PostgreSQL database.

The deployment process:

Render connects to the GitHub repository.

After the configured CI checks pass, Render builds the application.

Required dependencies are installed from requirements.txt.

Gunicorn starts the Flask application.

The updated API is deployed and made available through its hosted URL.

# CI/CD Workflow

The deployment workflow follows this process:

Local Development → GitHub Repository → GitHub Actions (Automated Testing) → Render (Build and Deployment) → Live REST API

This integration streamlines the development and deployment process by automating testing and deployment whenever validated changes are pushed to the repository.

# Project Structure

Refer to filestructure.txt for an overview of the application's folders, files, and components.


