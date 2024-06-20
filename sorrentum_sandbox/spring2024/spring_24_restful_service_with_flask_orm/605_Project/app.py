from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
#flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:allenmathews99@localhost/pharmacy_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initializing SQLAlchemy with flask
db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run(debug=True)
