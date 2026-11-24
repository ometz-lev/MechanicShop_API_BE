# This file contains unit test cases for the Customer API routes
from app import create_app
from app.models import db, Customer
from app.extensions import cache
from app.utils.util import encode_token, SECRET_KEY
from werkzeug.security import generate_password_hash
from jose import jwt
import unittest

class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')

        with self.app.app_context():
            cache.clear()
            db.drop_all()
            db.create_all()

            self.customer = Customer(
                name="test_user",
                email="test@email.com",
                phone="xxx-xxx-xxxx"
            )

            self.customer.set_password("test")   # Generates password hash

            db.session.add(self.customer)
            db.session.commit()

            self.customer_id = self.customer.id

        self.client = self.app.test_client()

    # Clean up after each test
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    # HELPER 1: Generate authentication headers
    def get_auth_headers(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)

        auth_token = response.json['auth_token']

        return {'Authorization': f'Bearer {auth_token}'}

    # HELPER 2: Create additional customers for pagination tests
    def create_additional_customers(self, number_of_customers):
        with self.app.app_context():
            customers = []

            for i in range(number_of_customers):
                customer = Customer(
                    name=f"Customer {i + 2}",
                    email=f"customer{i + 2}@email.com",
                    phone=f"111-000-{i + 2:04d}"
                )

                customer.set_password("test")
                customers.append(customer)

            db.session.add_all(customers)
            db.session.commit()

    # Test 1: Customer Creation Route
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jdoe@email.com",
            "phone": "111-111-1111",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")

        with self.app.app_context():           #Check that the Customer was actually saved to the DB
            customer = db.session.execute(
                db.select(Customer).where(Customer.email == "jdoe@email.com")
            ).scalar_one_or_none()

            self.assertIsNotNone(customer)

    # Test 2: Negative Test: Invalid Customer Creation
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "111-111-1111",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])

    # Test 3: Logging in the Customer Successfully
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'Successfully Logged In')
        self.assertIn('auth_token', response.json)

        auth_token = response.json['auth_token']

        decoded_token = jwt.decode(
            auth_token,
            SECRET_KEY,
            algorithms=['HS256']
        )

        # Verify token payload
        self.assertEqual(decoded_token['sub'], str(self.customer_id))
        self.assertEqual(decoded_token['user_type'], 'customer')
        self.assertIn('exp', decoded_token)
        self.assertIn('iat', decoded_token)

    # Test 4: Invalid login
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password')

    # Test 5: Token-Authenticated Update Route
    def test_update_customer(self):
        update_payload = {
            "name": "Peter",
        }

        headers = self.get_auth_headers()

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'test@email.com')

    # Test 6: Get request to retrieve all customers
    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], 'test_user')

    # Test 7: Successful pagination request
    def test_get_customers_pagination(self):
        self.create_additional_customers(4)

        with self.app.app_context():
            cache.clear()

        response = self.client.get('/customers/?page=1&per_page=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

        self.assertEqual(
            response.json[0]['email'],
            'test@email.com'
        )

        self.assertEqual(
            response.json[1]['email'],
            'customer2@email.com'
        )

    # Test 8: Get request for Customer by ID
    def test_get_customer(self):
        response = self.client.get(f'/customers/{self.customer_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_user')
        self.assertEqual(response.json['email'], 'test@email.com')

    # Test 9: Delete request
    def test_delete_customer(self):
        headers = self.get_auth_headers()
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():            # Verify that the record was actually deleted
            customer = db.session.execute(
                db.select(Customer).where(Customer.email == "test@email.com")
            ).scalar_one_or_none()

            self.assertIsNone(customer)

    # Test 10: Attempt to delete Customer with invalid token
    def test_delete_customer_with_invalid_token(self):
        headers = {'Authorization': 'Bearer invalid_token'}

        response = self.client.delete('/customers/', headers=headers)

        self.assertEqual(response.status_code, 401)
