#This file defines the database models for the application using SQLAlchemy ORM. It includes three main models: Customer, Service_ticket, and Mechanic, along with their relationships.    
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List
from app.extensions import db


## Customer model representing a customer in the system
class Customer(db.Model):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    # One-to-Many relationship with Service_ticket
    service_tickets: Mapped[List["Service_ticket"]] = db.relationship(back_populates="customer", cascade="all, delete-orphan")


## Association table for Many-to-Many relationship between Service_ticket and Mechanics
service_mechanics = db.Table(
    'service_mechanics',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'))
)

## Junction model for Many-to-Many relationship between Service Ticket and Inventory
class InventoryService(db.Model):
    __tablename__ = 'inventory_services'

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_id: Mapped[int] =mapped_column(db.ForeignKey('inventories.id'), nullable=False)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=False)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    quantity:Mapped[int] =mapped_column(db.Integer, nullable=False)

    inventory: Mapped["Inventory"] = db.relationship(back_populates="inventory_services")
    service_ticket: Mapped["Service_ticket"] = db.relationship(back_populates="inventory_services")


## Service_ticket model representing a service ticket in the system
class Service_ticket(db.Model):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(400), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Many-to-One relationship with Customer
    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    
    # Many-to-Many relationship with Mechanic
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanics, back_populates="service_tickets")

   # Many-to-Many relationship with Inventory
    inventory_services: Mapped[List['InventoryService']] = db.relationship(back_populates="service_ticket", cascade="all, delete-orphan")

## Mechanic model representing a mechanic in the system
class Mechanic(db.Model):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    # Many-to-Many relationship with Service_ticket
    service_tickets: Mapped[List["Service_ticket"]] = db.relationship(secondary=service_mechanics, back_populates="mechanics")


## Inventory model representing inventory items in the system
class Inventory(db.Model):
    __tablename__ = 'inventories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    # Many-to-Many relationship with Service_ticket
    inventory_services: Mapped[List["InventoryService"]] = db.relationship(back_populates="inventory")