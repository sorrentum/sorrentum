from flask import Flask, render_template, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create Flask instance
app = Flask(__name__)

# Create Limiter instance
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri='redis://redis:6379'
    # storage_uri='memory://'
)

# Define route for root URL
@app.route('/')
def index():
    return render_template('index.html')

# Define route for API
@app.route('/api')
@limiter.limit('3/second')  # Limit to 3 requests per second
def api():
    return jsonify({'foo': 'bar', 'baz': 'qux'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
