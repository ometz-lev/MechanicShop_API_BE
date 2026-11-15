#This file defines how the application converts Inventory and InventoryService DB records into JSON and validates incoming
# using marshmallow
from app.extensions import ma
from marshmallow import fields
from app.models import Inventory, InventoryService

# Schema for serializing and deserializing InventoryService objects
class InventoryServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryService
        load_instance = False
        include_fk = True

# Schema for serializing and deserializing Inventory objects
class InventorySchema(ma.SQLAlchemyAutoSchema):
   
    class Meta:
        model = Inventory
        load_instance = False

inventory_service_schema = InventoryServiceSchema()
inventory_services_schema = InventoryServiceSchema(many=True)

# Schema for serializing and deserializing InventoryService objects
class InventoryServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryService
        load_instance = False
        include_fk = True

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)