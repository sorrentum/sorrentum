from flask import Flask, request, redirect, render_template, session, url_for
import redis
import string
import random
import datetime
import bcrypt  # For password hashing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    if 'user' not in session:
        return redirect(url_for('login'))

    long_url = request.form['long_url']
    custom_alias = request.form.get('custom_alias')
    expiration_days = int(request.form['expiration_days']) if request.form['expiration_days'] else False

    # Generate short code or use custom alias if provided
    short_code = custom_alias if custom_alias else generate_short_code()

    # Check if custom alias is already in use
    if custom_alias and redis_client.exists(custom_alias):
        return 'Custom alias already in use. Please choose another.'

    # Store URL in Redis with expiration if specified along with user information
    if expiration_days:
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=expiration_days)
        expiration_timestamp = int(expiration_date.timestamp())
        redis_client.hmset(short_code, {'long_url': long_url, 'user': session['user'], 'expiration_timestamp': expiration_timestamp})
    else:
        redis_client.hmset(short_code, {'long_url': long_url, 'user': session['user']})

    short_url = request.host_url + short_code
    return render_template('shortened.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_to_original_url(short_code):
    url_info = redis_client.hgetall(short_code)
    if url_info:
        long_url = url_info[b'long_url'].decode('utf-8')
        creator = url_info[b'user'].decode('utf-8')  # Get the creator of the URL
        if creator == session.get('user'):  # Check if the current user is the creator
            track_url_access(short_code)
            return redirect(long_url)
        else:
            return 'You do not have permission to access this URL.'
    else:
        return 'URL not found'

def track_url_access(short_code):
    # Track URL access data in Redis or another database
    # For simplicity, let's use a Redis hash to store access counts
    redis_client.hincrby(short_code, 'access_count', 1)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username exists in Redis (assuming usernames are keys)
        if redis_client.exists(username):
            # Retrieve hashed password from Redis
            hashed_password = redis_client.get(username)
            # Check if the provided password matches the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                session['user'] = username
                return redirect(url_for('index'))

        return 'Invalid username/password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if redis_client.exists(username):
            return 'Username already exists. Please choose another.'

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store the username and hashed password in Redis
        redis_client.set(username, hashed_password)
        session['user'] = username
        return redirect(url_for('index'))

    return render_template('signup.html')

import datetime


@app.route('/analytics')
def analytics():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    url_access_counts = {}
    url_long_codes = {}
    url_expiration_days = {}

    # Retrieve URL keys for the current user
    user_keys = redis_client.keys('*')

    # Filter out keys that are not hashes or do not contain the 'user' field
    valid_user_keys = []
    for key in user_keys:
        key_type = redis_client.type(key)
        if key_type == b'hash' and redis_client.hexists(key, 'user'):
            valid_user_keys.append(key.decode('utf-8'))  # Decoding is needed here

    # Retrieve URL information for each valid key
        for short_code in valid_user_keys:
            url_info = redis_client.hgetall(short_code)
            if url_info:
                url_access_counts[short_code] = int(url_info.get(b'access_count', 0))  # Use get() to handle missing keys
                url_long_codes[short_code] = url_info.get(b'long_url', b'').decode('utf-8')
                if int(url_info.get(b'expiration_timestamp', 0))!= 0:
                    print(url_info.get(b'expiration_timestamp', 0))
                    expiration_timestamp = int(url_info.get(b'expiration_timestamp', 0))
                    remaining_seconds = expiration_timestamp - datetime.datetime.utcnow().timestamp()
                    if remaining_seconds > 0:
                        remaining_days = max(0, round(remaining_seconds / (3600 * 24)))
                        url_expiration_days[short_code] = remaining_days
                    else:
                        url_expiration_days[short_code] = "Expired"
                else:
                    url_expiration_days[short_code] = "No Expiration"

    return render_template('analytics.html', url_access_counts=url_access_counts, url_long_codes=url_long_codes, url_expiration_days=url_expiration_days)

if __name__ == '__main__':
    app.run(debug=True)