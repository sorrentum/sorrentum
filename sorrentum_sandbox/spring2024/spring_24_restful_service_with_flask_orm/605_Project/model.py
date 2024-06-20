from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import reconstructor
from datetime import datetime
from app import db

class Catalog(db.Model):
    __tablename__ = 'catalog'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)


class Manufacturer(db.Model):
    __tablename__ = 'manufacturer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    status = db.Column(db.String(50))


class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(50))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    status = db.Column(db.String(50))
    #orders = db.relationship('Orders', backref='doctor', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    gender = db.Column(db.String(20))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    product_use = db.Column(db.Text)
    count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    expiry = db.Column(db.Date)
    catalog_name = db.Column(db.String(100), nullable=False)
    manufacturer_name = db.Column(db.String(100), nullable=False)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)


class Pharmacist(db.Model):
    __tablename__ = 'pharmacist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=datetime.now())
    product_ids =  db.Column(db.String(1000), nullable=False)
    product_names = db.Column(db.String(1000), nullable=False)
    product_counts =  db.Column(db.String(1000), nullable=False)
    total = db.Column(db.Numeric, nullable=False)
    payment_method = db.Column(db.String(20))
    status = db.Column(db.String(20))
    customer_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)

    pharmacist_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    doctor_id = db.Column(db.Integer)


class Shipment(db.Model):
    __tablename__ = 'shipment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dispatch_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    order_id = db.Column(db.Integer,nullable=False)
    order_time = db.Column(db.DateTime)