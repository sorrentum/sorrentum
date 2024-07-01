from flask import Flask
import redis
from datetime import timedelta
from flask import request

r = redis.Redis(host='redis', port=6379, db=0)
user_history = ["guest"]

def request_is_limited(r: redis.Redis, key: str, limit: int, period: timedelta):
    period_in_seconds = int(period.total_seconds())
    t = r.time()[0]
    separation = round(period_in_seconds / limit)
    r.setnx(key, 0)
    try:
        with r.lock('lock:' + key, blocking_timeout=5) as lock:
            tat = max(int(r.get(key)), t)
            if tat - t <= period_in_seconds - separation:
                new_tat = max(tat, t) + separation
                r.set(key, new_tat)
                return False
            return True
    except LockError:
        return True

app = Flask(__name__)

@app.route('/')
def hello():
   username = request.args.get("username", "guest")
   if username != "guest":
      # Track the last username entered
      user_history.append(username)
   pings = int(request.args.get("pings", 1))
   block_flag = False
   for i in range(pings):
      #Send pings as the last user who signed in
      if request_is_limited(r, user_history[-1], 10, timedelta(minutes=1)):
         block_flag = True
   if block_flag:
      # Block last user
      return "<h1>" + user_history[-1] + " IS BLOCKED </h2>"
   else:
       return (
		"""<h1> Welcome to the sandbox </h2>
		<form action="" method="get">
		<label for="username">Username:</label><br>
		<input type="text" name="username" id="username">
		<br>
		<button type="submit" formaction="/"+username value="Submit">
		Submit </button>
		</form>
        How many times would you like to ping the server?
		<form action="" method="get">
		<input type="text" name="pings">
		<input type="submit" value="PING">
		</form>""")

if __name__ == "__main__":
    app.run(debug=True)
