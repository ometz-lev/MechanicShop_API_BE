# This file contains unit test cases for the Mechanic routes
from app import create_app
from app.models import Customer, Mechanic, Service_ticket
from datetime import date
from app.extensions import db, cache
from app.utils.util import SECRET_KEY
from jose import jwt
import unittest

class TestMechanic(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')

        with self.app.app_context():
            cache.clear()
            db.drop_all()
            db.create_all()

            self.mechanic = Mechanic(
                name="test_mechanic",
                email="mechanic@email.com",
                phone="xxx-xxx-xxxx",
                salary="50000"
            )

            self.mechanic.set_password("test")

            db.session.add(self.mechanic)
            db.session.commit()

            self.mechanic_id = self.mechanic.id

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    # Helper: Generate authentication headers
    def get_auth_headers(self):
        credentials = {
            "email": "mechanic@email.com",
            "password": "test"
        }

        response = self.client.post('/mechanics/login', json=credentials)

        auth_token = response.json['auth_token']

        return {'Authorization': f'Bearer {auth_token}'}

    # Helper: Create an additional mechanic
    def create_additional_mechanic(self, name, email):
        with self.app.app_context():
            mechanic = Mechanic(
                name=name,
                email=email,
                phone="222-111-1111",
                salary="50000"
            )

            mechanic.set_password("test")

            db.session.add(mechanic)
            db.session.commit()

            return mechanic.id

    # Test 1: Create a Mechanic - Post request
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Mechanic",
            "email": "johnm@email.com",
            "phone": "222-222-2222",
            "password": "1234",
            "salary": "50000"
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Mechanic")
        self.assertEqual(response.json['email'], "johnm@email.com")

        with self.app.app_context():
            mechanic = db.session.execute(
                db.select(Mechanic).where(
                    Mechanic.email == "johnm@email.com"
                )
            ).scalar_one_or_none()

            self.assertIsNotNone(mechanic)
            self.assertNotEqual(mechanic.password_hash, "1234")

    # Test : Negative Test: Duplicate email
    def test_create_mechanic_duplicate_email(self):
        mechanic_payload = {
            "name": "Sam Mechanic",
            "email": "mechanic@email.com",
            "phone": "222-333-3333",
            "salary": "50000",
            "password": "1234"
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Mechanic with this email already exists.")

    # Test 3: Test Mechanic Login Successfully
    def test_login_mechanic(self):
        credentials = {
            "email": "mechanic@email.com",
            "password": "test"
        }

        response = self.client.post(
            '/mechanics/login',
            json=credentials
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'Successfully Logged In')

        self.assertIn('auth_token', response.json)

        decoded_token = jwt.decode(
            response.json['auth_token'],
            SECRET_KEY,
            algorithms=['HS256']
        )

        self.assertEqual(decoded_token['sub'], str(self.mechanic_id))
        self.assertEqual(decoded_token['user_type'], 'mechanic')
        self.assertIn('exp', decoded_token)
        self.assertIn('iat', decoded_token)

    # Test 4: Invalid Credentials
    def test_invalid_mechanic_login(self):
        credentials = {
            "email": "mechanic@email.com",
            "password": "wrong_password"
        }

        response = self.client.post('/mechanics/login', json=credentials)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password')

    # Test 5: Test Update route, the JWT token is used to identify the mechanic that needs to be updated.
    def test_update_mechanic(self):
        update_payload = {
            "name": "Tom Mechanic"
        }

        headers = self.get_auth_headers()

        response = self.client.put('/mechanics/', json=update_payload, headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Tom Mechanic')
        self.assertEqual(response.json['email'], 'mechanic@email.com')

    # Test 6: Delete Mechanic, the JWT token is used to identify the mechanic that needs to be deleted.
    def test_delete_mechanic(self):
        headers = self.get_auth_headers()

        response = self.client.delete('/mechanics/', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], f'Mechanic id:{self.mechanic_id}, deleted successfully.')

        with self.app.app_context():
            mechanic = db.session.get(Mechanic, self.mechanic_id)

            self.assertIsNone(mechanic)

    # Test 7: Negative Test - Missing authentication to delete Mechanic
    def test_delete_mechanic_without_token(self):
        response = self.client.delete('/mechanics/')

        self.assertEqual(response.status_code, 401)

    # Test 8: Retrieve top mechanics - Sorts mechanics based on the # of service tickets assigned to each mechanic
    def test_get_top_mechanics(self):
        second_mechanic_id = self.create_additional_mechanic(
            "John Mechanic",
            "johnm@email.com"
        )

        with self.app.app_context():

            # Create a customer for the service ticket
            customer = Customer(
                name="Test Customer",
                email="customer@email.com",
                phone="888-888-8888"
            )
            customer.set_password("test")

            db.session.add(customer)
            db.session.commit()

            # Create a service ticket
            ticket = Service_ticket(
                vin="123456789",
                service_date=date(2026, 3, 15),
                service_desc="Oil change",
                customer_id=customer.id
            )

            db.session.add(ticket)
            db.session.commit()

            # Assign the ticket to the second mechanic
            mechanic = db.session.get(Mechanic, second_mechanic_id)
            mechanic.service_tickets.append(ticket)

            db.session.commit()

            cache.clear()

        response = self.client.get('/mechanics/top')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

        # The mechanic with one service ticket should appear first
        self.assertEqual(response.json[0]['mechanic_id'], second_mechanic_id)
        self.assertEqual(response.json[0]['service_ticket_count'], 1)

        self.assertEqual(response.json[1]['mechanic_id'], self.mechanic_id)
        self.assertEqual(response.json[1]['service_ticket_count'], 0)

    # Test 9: Test Search route
    def test_search_mechanics(self):
        self.create_additional_mechanic(
            "John Smith",
            "johns@email.com"
        )

        response = self.client.get('/mechanics/search?name=John')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], 'John Smith')

    # Test 10: Test missing name
    def test_search_mechanics_missing_name(self):
        response = self.client.get('/mechanics/search')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Please provide a mechanic name to search.')