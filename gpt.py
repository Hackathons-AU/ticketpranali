from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import logging

app = Flask(__name__)

API_KEY = "sk-proj-NmMnHeSI2smCOvO7SEaST3BlbkFJZQs8HFfJZvNAj2jfn4gB"
API_URL = "https://api.openai.com/v1/chat/completions"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')

    if not user_input:
        return jsonify({"reply": "No message provided"}), 400

    response, tokens_used = get_chatgpt_response(user_input)
    
    return jsonify({
        "reply": response,
        "tokens_used": tokens_used
    })

def get_chatgpt_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_json = response.json()

        reply = response_json['choices'][0]['message']['content']
        tokens_used = response_json['usage']['total_tokens']

        return reply, tokens_used
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return "HTTP error occurred", 0
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return "An error occurred", 0

if __name__ == '__main__':
    app.run(debug=True)

