from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import redis

# Initialize Redis client.
redis_client = redis.Redis(host='redis', port=6379, db=0)

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')
 
@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input_text = msg
    # Check if the user query exists in Redis cache.
    if redis_client.exists(input_text):
        # If yes, retrieve the response from Redis.
        return redis_client.get(input_text).decode('utf-8')
    else:
        # If not, generate a response and store it in Redis.
        response = get_chat_response(input_text)
        redis_client.set(input_text, response)
        return response

def get_chat_response(text):
    for step in range(5):
        # Encode the new user input, add the eos_token and return a tensor in Pytorch.
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')
        # Append the new user input tokens to the chat history.
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids
        # Generated a response while limiting the total chat history to 1000 tokens.
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)        
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
