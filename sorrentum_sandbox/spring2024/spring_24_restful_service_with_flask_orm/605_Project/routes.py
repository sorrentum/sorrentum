from flask import jsonify, request, Blueprint
from app import db,app
from model import *

#route blueprints
catalog_bp = Blueprint('catalog', __name__)
manufacturer_bp = Blueprint('manufacturer', __name__)
doctor_bp = Blueprint('doctor',__name__)
customer_bp = Blueprint('customer',__name__)
product_bp = Blueprint('product', __name__)
pharmacist_bp = Blueprint('pharmacist', __name__)
orders_bp = Blueprint('orders', __name__)
shipment_bp = Blueprint('shipment', __name__)

#Catalog endpoints
@app.route('/catalogs', methods=['GET'])
def get_catalogs():
    catalogs = Catalog.query.all()
    return jsonify({'catalogs': [{'id': catalog.id, 'name': catalog.name, 'description': catalog.description} for catalog in catalogs]})

@app.route('/catalogs/<int:id>', methods=['GET'])
def get_catalog(id):
    catalog = Catalog.query.get_or_404(id)
    return jsonify({'id': catalog.id, 'name': catalog.name, 'description': catalog.description})

@app.route('/catalogs', methods=['POST'])
def create_catalog():
    data = request.get_json()
    new_catalog = Catalog(name=data['name'], description=data['description'])
    db.session.add(new_catalog)
    db.session.commit()
    return jsonify({'message': 'Catalog created successfully'}), 201

@app.route('/catalogs/<int:id>', methods=['PUT'])
def update_catalog(id):
    catalog = Catalog.query.get_or_404(id)
    data = request.get_json()
    catalog.name = data['name']
    catalog.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Catalog updated successfully'})

@app.route('/catalogs/<int:id>', methods=['DELETE'])
def delete_catalog(id):
    catalog = Catalog.query.get_or_404(id)
    db.session.delete(catalog)
    db.session.commit()
    return jsonify({'message': 'Catalog deleted successfully'})

#Manufacturer endpoints
@app.route('/manufacturers', methods=['GET'])
def get_manufacturers():
    manufacturers = Manufacturer.query.all()
    return jsonify({'manufacturers': [{'id': manufacturer.id, 'name': manufacturer.name, 'email': manufacturer.email, 'phone' : manufacturer.phone, 'address': manufacturer.address, 'status' : manufacturer.status} for manufacturer in manufacturers]})

@app.route('/manufacturers/<int:id>', methods=['GET'])
def get_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    return jsonify({'id': manufacturer.id, 'name': manufacturer.name, 'email': manufacturer.email, 'phone' : manufacturer.phone, 'address': manufacturer.address, 'status' : manufacturer.status})

@app.route('/manufacturers', methods=['POST'])
def create_manufacturer():
    data = request.get_json()
    new_manufacturer = Manufacturer(name=data['name'], email=data['email'], phone=data['phone'], address=data['address'], status=data['status'])
    db.session.add(new_manufacturer)
    db.session.commit()
    return jsonify({'message': 'Manufacturer created successfully'}), 201

@app.route('/manufacturers/<int:id>', methods=['PUT'])
def update_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    data = request.get_json()
    manufacturer.name = data['name']
    manufacturer.email = data['email']
    manufacturer.phone = data['phone']
    manufacturer.address = data['address']
    manufacturer.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Manufacturer updated successfully'})

@app.route('/manufacturers/<int:id>', methods=['DELETE'])
def delete_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    db.session.delete(manufacturer)
    db.session.commit()
    return jsonify({'message': 'Manufacturer deleted successfully'})

#Doctor endpoints
@app.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify({'doctors': [{'id': doctor.id, 'name': doctor.name, 'specialization': doctor.specialization,'age' : doctor.age, 'phone' : doctor.phone, 'email' : doctor.email, 'address': doctor.address, 'status' : doctor.status} for doctor in doctors]})

@app.route('/doctors/<int:id>', methods=['GET'])
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify({'id': doctor.id, 'name': doctor.name, 'specialization': doctor.specialization,'age' : doctor.age, 'phone' : doctor.phone, 'email' : doctor.email, 'address': doctor.address, 'status' : doctor.status})

@app.route('/doctors', methods=['POST'])
def create_doctor():
    data = request.get_json()
    new_doctor = Doctor(name=data['name'], specialization=data['specialization'], age=data['age'],  phone=data['phone'], email=data['email'], address=data['address'], status=data['status'])
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor created successfully'}), 201

@app.route('/doctors/<int:id>', methods=['PUT'])
def update_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()
    doctor.name = data['name']
    doctor.age = data['age']
    doctor.specialization = data['specialization']
    doctor.email = data['email']
    doctor.phone = data['phone']
    doctor.address = data['address']
    doctor.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Doctor updated successfully'})

@app.route('/doctors/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor deleted successfully'})

#Customer endpoints
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify({'customers': [{'id': customer.id, 'name': customer.name,'age' : customer.age, 'phone' : customer.phone, 'email' : customer.email, 'address': customer.address, 'gender' : customer.gender} for customer in customers]})

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'id': customer.id, 'name': customer.name,'age' : customer.age, 'phone' : customer.phone, 'email' : customer.email, 'address': customer.address, 'gender' : customer.status})

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], age=data['age'], phone=data['phone'], email=data['email'], address=data['address'], gender=data['gender'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully'}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.name = data['name']
    customer.age = data['age']
    customer.email = data['email']
    customer.phone = data['phone']
    customer.address = data['address']
    customer.gender = data['gender']
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})

#Product endpoints
#check it again
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify({'products': [{'id': product.id, 'name': product.name, 'product_use': product.product_use, 'count': product.count, 'price': float(product.price), 'expiry': product.expiry, 'catalog_name': product.catalog_name, 'manufacturer_name': product.manufacturer_name} for product in products]})

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({'id': product.id,
                    'name': product.name,
                    'product_use': product.product_use,
                    'count': product.count,
                    'price': float(product.price),
                    'expiry': product.expiry,
                    'catalog_name': product.catalog_name,
                    'manufacturer_name': product.manufacturer_name})

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()

    catalog = Catalog.query.filter_by(id=data['catalog_id']).first()

    if not catalog:
        return jsonify({'error': 'Catalog not found'}), 404

    manufacturer = Manufacturer.query.filter_by(id=data['manufacturer_id']).first()
    if not manufacturer:
        return jsonify({'error': 'Manufacturer not found'}), 404

    new_product = Product(name=data['name'],
                          product_use=data['product_use'],
                          count=data['count'],
                          price=data['price'],
                          expiry=data['expiry'],
                          catalog_name=catalog.name,
                          manufacturer_name=manufacturer.name,
                          catalog_id=data['catalog_id'],
                          manufacturer_id=data['manufacturer_id'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully', 'id': new_product.id}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()

    catalog = Catalog.query.filter_by(catalog_id=data['catalog_id']).first()

    if not catalog:
        return jsonify({'error': 'Catalog not found'}), 404

    manufacturer = Manufacturer.query.filter_by(manufacturer_id=data['manufacturer_id']).first()
    if not manufacturer:
        return jsonify({'error': 'Manufacturer not found'}), 404

    product.name = data['name']
    product.product_use = data['product_use']
    product.count = data['count']
    product.price = data['price']
    product.expiry = data['expiry']
    product.catalog_name = catalog.name
    product.manufacturer_name = manufacturer.name
    product.catalog_id = data['catalog_id']
    product.manufacturer_id = data['manufacturer_id']

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

#Pharmacist endpoints
@app.route('/pharmacists', methods=['GET'])
def get_pharmacists():
    pharmacists = Pharmacist.query.all()
    return jsonify({'pharmacists': [{'id': pharmacist.id,
                                     'name': pharmacist.name,
                                     'status': pharmacist.status} for pharmacist in pharmacists]})


@app.route('/pharmacists/<int:id>', methods=['GET'])
def get_pharmacist(id):
    pharmacist = Pharmacist.query.get_or_404(id)
    return jsonify({'id': pharmacist.id,
                    'name': pharmacist.name,
                    'status': pharmacist.status})



@app.route('/pharmacists', methods=['POST'])
def create_pharmacist():
    data = request.get_json()
    new_pharmacist = Pharmacist(name=data['name'],
                                password=data['password'],
                                status=data['status'])
    db.session.add(new_pharmacist)
    db.session.commit()
    return jsonify({'message': 'Pharmacist created successfully', 'id': new_pharmacist.id}), 201

@app.route('/pharmacists/<int:id>', methods=['PUT'])
def update_pharmacist(id):
    pharmacist = Pharmacist.query.get_or_404(id)
    data = request.get_json()
    pharmacist.name = data['name']
    pharmacist.password = data['password']
    pharmacist.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Pharmacist updated successfully'})

@app.route('/pharmacists/<int:id>', methods=['DELETE'])
def delete_pharmacist(id):
    pharmacist = Pharmacist.query.get_or_404(id)
    db.session.delete(pharmacist)
    db.session.commit()
    return jsonify({'message': 'Pharmacist deleted successfully'})

#Order endpoints
#check it again
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Orders.query.all()
    return jsonify({'orders': [{'id': order.id,
                                'time': order.time,
                                'product_ids': order.product_ids,
                                'product_names': order.product_names,
                                'product_counts': order.product_counts,
                                'total': str(order.total),
                                'payment_method': order.payment_method,
                                'status': order.status,
                                'customer_name': order.customer_name,
                                'doctor_name': order.doctor_name,
                                'pharmacist_id': order.pharmacist_id,
                                'customer_id': order.customer_id,
                                'doctor_id': order.doctor_id,
                                } for order in orders]})


@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Orders.query.get_or_404(id)
    return jsonify({'id': order.id,
                    'time': order.time,
                    'product_ids': order.product_ids,
                    'product_names': order.product_names,
                    'product_counts': order.product_counts,
                    'total': str(order.total),
                    'payment_method': order.payment_method,
                    'status': order.status,
                    'customer_name': order.customer_name,
                    'doctor_name': order.doctor_name,
                    'pharmacist_id': order.pharmacist_id,
                    'customer_id': order.customer_id,
                    'doctor_id': order.doctor_id,
                    })


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    pharmacist_id = data['pharmacist_id']
    customer_id = data['customer_id']
    doctor_id = data['doctor_id']
    product_ids = data['product_ids']
    product_counts=data['product_counts']
    total=0.0;
    product_names=[];


    all_products_str=product_ids.split(',');
    all_products=[int(x) for x in all_products_str]
    nos_product_counts=product_counts.split(',');
    all_product_counts = [int(x) for x in nos_product_counts]

    if len(all_products) !=len(all_product_counts):
        return jsonify({'error': 'Mismatch in product and product count'}), 404
    for i in range(0,len(all_products)):
        product=Product.query.get_or_404(all_products[i])
        if product.count<all_product_counts[i]:
            return jsonify({'error': 'Insufficient number of products'}), 404
        else:
            total=total+(all_product_counts[i]*product.price)
            product_names.append(product.name)
            product.count=product.count-all_product_counts[i]
            db.session.commit()

    # Retrieve Pharmacist, Customer, and Doctor objects
    pharmacist = Pharmacist.query.get_or_404(pharmacist_id)
    customer = Customer.query.get_or_404(customer_id)
    doctor = Doctor.query.get_or_404(doctor_id)
    # Create order
    new_order = Orders(
                      product_ids=data['product_ids'],
                      product_names=', '.join(product_names),
                      product_counts=','.join(nos_product_counts),
                      total=total,
                      payment_method=data['payment_method'],
                      status=data['status'],
                      customer_name=customer.name,
                      doctor_name=doctor.name,
                      pharmacist_id=pharmacist.id,
                      customer_id=customer.id,
                      doctor_id=doctor.id)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order created successfully', 'id': new_order.id}), 201

'''
@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(order_id):
    order = Orders.query.get_or_404(order_id)
    data = request.get_json()
    pharmacist_id = data['pharmacist_id']
    customer_id = data['customer_id']
    doctor_id = data['doctor_id']

    # Retrieve Pharmacist, Customer, and Doctor objects
    pharmacist = Pharmacist.query.get_or_404(pharmacist_id)
    customer = Customer.query.get_or_404(customer_id)
    doctor = Doctor.query.get_or_404(doctor_id)

    # Update order
    order.time = data['time']
    order.product_ids = ','.join([str(product['id']) for product in products])
    order.product_names = ','.join([product['name'] for product in products])
    order.product_counts = ','.join([str(product['count']) for product in products])
    order.total = data['total']
    order.payment_method = data['payment_method']
    order.status = data['status']
    order.customer_name = customer.name
    order.doctor_name = doctor.name
    order.pharmacist_id = pharmacist.id
    order.customer_id = customer.id
    order.doctor_id = doctor.id

    #clear existing products and add updated products
    order.products.clear()
    for product in products:
        product_obj = Product.query.get_or_404(product['id'])
        order.products.append(product_obj)

    db.session.commit()
    return jsonify({'message': 'Order updated successfully'})


@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(order_id):
    order = Orders.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})
'''

#Shipment endpoints
#check it again
@app.route('/shipments', methods=['GET'])
def get_shipments():
    shipments = Shipment.query.all()
    return jsonify({'shipments': [{'id': shipment.id,
                                   'dispatch_date': shipment.dispatch_date,
                                   'delivery_date': shipment.delivery_date,
                                   'status': shipment.status,
                                   'order_id': shipment.order_id,
                                   'order_time': shipment.order_time} for shipment in shipments]})


@app.route('/shipments/<int:id>', methods=['GET'])
def get_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    return jsonify({'id': shipment.id,
                    'dispatch_date': shipment.dispatch_date,
                    'delivery_date': shipment.delivery_date,
                    'status': shipment.status,
                    'order_id': shipment.order_id,
                    'order_time': shipment.order_time})

@app.route('/shipments', methods=['POST'])
def create_shipment():
    data = request.get_json()
    order_id=data['order_id']
    order = Orders.query.get_or_404(order_id)
    new_shipment = Shipment(dispatch_date=data['dispatch_date'],
                            delivery_date=data['delivery_date'],
                            status=data['status'],
                            order_id=order.id,
                            order_time=order.time)
    db.session.add(new_shipment)
    db.session.commit()
    return jsonify({'message': 'Shipment created successfully', 'id': new_shipment.id}), 201

@app.route('/shipments/<int:id>', methods=['PUT'])
def update_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    data = request.get_json()
    order_id = data['order_id']
    order = Orders.query.get_or_404(order_id)
    shipment.dispatch_date = data['dispatch_date']
    shipment.delivery_date = data['delivery_date']
    shipment.status = data['status']
    shipment.order_id = order.id
    shipment.order_time = order.time
    db.session.commit()
    return jsonify({'message': 'Shipment updated successfully'})

@app.route('/shipments/<int:id>', methods=['DELETE'])
def delete_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    db.session.delete(shipment)
    db.session.commit()
    return jsonify({'message': 'Shipment deleted successfully'})