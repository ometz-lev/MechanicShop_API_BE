# This file contains unit test cases for the Service Ticket routes
import unittest
from datetime import date
from app import create_app
from app.extensions import db, cache
from app.models import (
    Customer,
    Mechanic,
    Service_ticket,
    Inventory,
    InventoryService
)
from app.utils.util import encode_token

class TestServiceTicket(unittest.TestCase):

    BASE_URL = '/service-tickets'

    def setUp(self):
        self.app = create_app('TestingConfig')

        with self.app.app_context():
            cache.clear()
            db.drop_all()
            db.create_all()

            # Create customer
            self.customer = Customer(
                name="Test Customer",
                email="customer@email.com",
                phone="444-111-1111"
            )
            self.customer.set_password("test")

            # Create mechanic
            self.mechanic = Mechanic(
                name="Test Mechanic",
                email="mechanic@email.com",
                phone="444-222-2222",
                salary=50000
            )
            self.mechanic.set_password("test")

            # Create inventory item
            self.inventory = Inventory(
                name="Oil Filter",
                price=20.99
            )

            db.session.add_all([
                self.customer,
                self.mechanic,
                self.inventory
            ])
            db.session.commit()

            self.customer_id = self.customer.id
            self.mechanic_id = self.mechanic.id
            self.inventory_id = self.inventory.id

            # Create service ticket
            self.ticket = Service_ticket(
                vin="123456789",
                service_date=date(2026, 3, 15),
                service_desc="Oil change",
                customer_id=self.customer_id
            )

            db.session.add(self.ticket)
            db.session.commit()

            self.ticket_id = self.ticket.id

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    # Helper: Generate authentication headers for Customer
    def get_customer_auth_headers(self):
        token = encode_token(self.customer_id, 'customer')
        return {'Authorization': f'Bearer {token}'}

    def create_additional_mechanic(self, name, email):
        with self.app.app_context():
            mechanic = Mechanic(
                name=name,
                email=email,
                phone="444-333-3333",
                salary=55000
            )
            mechanic.set_password("test")

            db.session.add(mechanic)
            db.session.commit()

            return mechanic.id

    # Test 1: Tests successful creation of a service ticket
    def test_create_service_ticket(self):
        data = {
            "vin": "987654321",
            "service_date": "2026-05-01",
            "service_desc": "Tyre alignment",
            "customer_id": self.customer_id
        }

        response = self.client.post(f'{self.BASE_URL}/', json=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['vin'], "987654321")
        self.assertEqual(response.json['service_desc'], "Tyre alignment")

    # Test 2: Successfull assignment of mechanic to service ticket
    def test_assign_mechanic(self):
        response = self.client.put(
            f'{self.BASE_URL}/{self.ticket_id}/assign-mechanic/{self.mechanic_id}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['message'], "Mechanic successfully assigned to service ticket")
        self.assertEqual(response.json['service_ticket_id'], self.ticket_id)
        self.assertEqual(response.json['mechanic_id'], self.mechanic_id)

        self.assertEqual(
            response.json['assigned_mechanics'][0]['mechanic_id'], self.mechanic_id)

    # Test 3: Remove a mechanic from service ticket successfully, requires a valid customer token to action removal.
    def test_remove_mechanic(self):
        with self.app.app_context():
            ticket = db.session.get(Service_ticket, self.ticket_id)
            mechanic = db.session.get(Mechanic, self.mechanic_id)

            ticket.mechanics.append(mechanic)
            db.session.commit()

        headers = self.get_customer_auth_headers()

        response = self.client.put(
            f'{self.BASE_URL}/{self.ticket_id}/remove-mechanic/{self.mechanic_id}',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Mechanic successfully removed from service ticket")
        self.assertEqual(response.json['service_ticket'], self.ticket_id)
        self.assertEqual(response.json['mechanic_id'], self.mechanic_id)

    # Test 4: Retrieve all service tickets successfully
    def test_get_all_service_tickets(self):
        response = self.client.get(f'{self.BASE_URL}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['vin'], "123456789")
        self.assertEqual(response.json[0]['service_desc'], "Oil change")

    # Test 5: Retrieve all assigned mechanics to existing service tickets
    def test_get_all_assigned_mechanics(self):
        with self.app.app_context():
            ticket = db.session.get(Service_ticket, self.ticket_id)
            mechanic = db.session.get(Mechanic, self.mechanic_id)

            ticket.mechanics.append(mechanic)
            db.session.commit()

        response = self.client.get(f'{self.BASE_URL}/mechanics')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

        self.assertEqual(response.json[0]['service_ticket_id'], self.ticket_id)
        self.assertEqual(response.json[0]['mechanics'][0]['mechanic_id'], self.mechanic_id)

    # Test 6: Retrieve the authenticated customer's service ticket
    def test_get_my_tickets(self):
        headers = self.get_customer_auth_headers()

        response = self.client.get(
            f'{self.BASE_URL}/my-tickets',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['vin'], "123456789")
        self.assertEqual(response.json[0]['customer_id'], self.customer_id)

    # Test 7: Edit a service ticket by adding/removing a mechanic successfully
    def test_edit_service_ticket(self):
        data = {
            "add_mechanic_ids": [self.mechanic_id],
            "remove_mechanic_ids": []
        }

        response = self.client.put(f'{self.BASE_URL}/{self.ticket_id}/edit', json=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket_id'], self.ticket_id)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['mechanic_id'], self.mechanic_id)

    # Test 8: Delete a service ticket successfully
    def test_delete_service_ticket(self):
        response = self.client.delete(
            f'{self.BASE_URL}/{self.ticket_id}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], f"Service ticket {self.ticket_id} deleted successfully.")

        with self.app.app_context():
            ticket = db.session.get(Service_ticket, self.ticket_id)
            self.assertIsNone(ticket)

    # Test 9: Add inventory item to a service ticket successfully
    def test_add_inventory_to_service_ticket(self):
        data = {
            "inventory_id": self.inventory_id,
            "quantity": 2
        }

        response = self.client.post(
            f'{self.BASE_URL}/{self.ticket_id}/inventory',
            json=data
        )

        self.assertEqual(response.status_code, 201)

        inventory_data = response.json['inventory_service']

        self.assertEqual(inventory_data['inventory_id'], self.inventory_id)
        self.assertEqual(inventory_data['service_ticket_id'], self.ticket_id)
        self.assertEqual(inventory_data['name'], "Oil Filter")
        self.assertEqual(inventory_data['quantity'], 2)

    # Test 10: Retrieve inventory for a service ticket
    def test_get_ticket_inventory(self):
        with self.app.app_context():
            ticket = db.session.get(Service_ticket, self.ticket_id)
            inventory = db.session.get(Inventory, self.inventory_id)

            inventory_service = InventoryService(
            inventory=inventory,
            service_ticket=ticket,
            name=inventory.name,
            price=inventory.price,
            quantity=2
        )

            db.session.add(inventory_service)
            db.session.commit()

        response = self.client.get(f'{self.BASE_URL}/{self.ticket_id}/inventory')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], "Oil Filter")
        self.assertEqual(response.json[0]['quantity'], 2)

    # Test 11: Negative Test - Existing mechanic assigned to a service ticket not found
    def test_assign_mechanic_service_ticket_not_found(self):
        response = self.client.put(f'{self.BASE_URL}/999/assign-mechanic/{self.mechanic_id}')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Service ticket not found.")

    # Test 12: Negative Test - One or more mechanics to add to an existing service ticket do not exist
    def test_edit_service_ticket_mechanic_not_found(self):
        data = {
            "add_mechanic_ids": [999],
            "remove_mechanic_ids": []
        }

        response = self.client.put(
            f'{self.BASE_URL}/{self.ticket_id}/edit',
            json=data
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json['error'],
            "One or more mechanics to add do not exist."
        )

    # Test 13: Negative Test - Invalid Inventory quantity added to a service ticket
    def test_add_inventory_invalid_quantity(self):
        data = {
            "inventory_id": self.inventory_id,
            "quantity": -2
        }

        response = self.client.post(f'{self.BASE_URL}/{self.ticket_id}/inventory',json=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'],"Quantity must be a positive integer.")