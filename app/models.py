#This file defines the database models for the application using SQLAlchemy ORM. It includes three main models: Customer, Service_ticket, and Mechanic, along with their relationships.    
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy()

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["Service_ticket"]] = db.relationship(back_populates="customer", cascade="all, delete-orphan")

## Many-to-Many relationship between Service_ticket and Mechanics
service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'))
)

class Service_ticket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(400), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    ## Many-to-Many relationship with Mechanics
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanics, back_populates="service_tickets")

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    ## Many-to-Many relationship with Service_ticket
    service_tickets: Mapped[List["Service_ticket"]] = db.relationship(secondary=service_mechanics, back_populates="mechanics")