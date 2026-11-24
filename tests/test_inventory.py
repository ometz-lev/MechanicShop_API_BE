# This file contains unit test cases for the Inventory routes
import unittest
from app import create_app
from app.extensions import db, cache
from app.models import Inventory

class TestInventory(unittest.TestCase):
    BASE_URL = '/inventory'

    def setUp(self):
        self.app = create_app('TestingConfig')

        with self.app.app_context():
            cache.clear()
            db.drop_all()
            db.create_all()

            self.inventory = Inventory(name="Coolant", price = 20.99)

            db.session.add(self.inventory)
            db.session.commit()
        
            self.inventory_id = self.inventory.id
        
        self.client = self.app.test_client()

    # Clean up the database resources
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    # Test 1: Tests successful creation of an inventory - POST
    def test_create_inventory(self):
        data = {"name" : "Brake Pads", "price" : 79.99}

        response = self.client.post( f'{self.BASE_URL}/', json=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Brake Pads")
        self.assertEqual(response.json['price'], 79.99)

    # Test 2: Retrieve all inventory items successfully - GET
    def test_get_all_inventory(self):

        response = self.client.get(f'{self.BASE_URL}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['name'], "Coolant")
        self.assertEqual(response.json[0]['price'], 20.99)

    # Test 3: Retrieve one inventory item - GET
    def test_get_inventory(self):
    
        response = self.client.get(f'{self.BASE_URL}/{self.inventory_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Coolant")
        self.assertEqual(response.json['price'], 20.99)

    # Test 4: Update inventory item - GET
    def test_update_inventory(self):
        data = {"name" : "Premium Coolant", "price" : 25.99}
    
        response = self.client.put(f'{self.BASE_URL}/{self.inventory_id}', json=data)
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Premium Coolant")
        self.assertEqual(response.json['price'], 25.99)

    # Test 5: Delete an existing inventory item - DELETE
    def test_delete_inventory(self):

        response = self.client.delete(f'{self.BASE_URL}/{self.inventory_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
        response.json['message'], f"Successfully deleted inventory item {self.inventory_id}")

        with self.app.app_context():
            inventory = db.session.get(Inventory, self.inventory_id)
            self.assertIsNone(inventory)

    # Test 6: Negative Test - Create inventory with a duplicate name
    def test_create_inventory_duplicate_name(self):
        data = {"name" : "Coolant", "price" : 15.99}

        response = self.client.post( f'{self.BASE_URL}/', json=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Inventory item with this name already exists.")

    # Test 7: Negative Test - Retrieve inventory that does not exist
    def test_get_inventory_not_found(self):
        
        response = self.client.get(f'{self.BASE_URL}/999')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Inventory item not found.")

    # Test 8: Negative Test - Update inventory that does not exist
    def test_update_inventory_not_found(self):
        
        data = {"name" : "New Coolant", "price" : 20.00}

        response = self.client.get(f'{self.BASE_URL}/999', json=data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Inventory item not found.")
