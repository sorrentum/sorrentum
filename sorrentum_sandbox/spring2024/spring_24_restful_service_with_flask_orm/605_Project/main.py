from routes import *
from app import app

# Register the blueprints
app.register_blueprint(catalog_bp, url_prefix='/api')
app.register_blueprint(manufacturer_bp, url_prefix='/api')
app.register_blueprint(doctor_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(pharmacist_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(shipment_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)

