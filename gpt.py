from flask import Flask, request, jsonify, render_template, session
import datetime
import json
import requests
import logging
app = Flask(__name__)
app.secret_key = 'supersecretkeyorisitreally?'

API_KEY = "sk-proj-NmMnHeSI2smCOvO7SEaST3BlbkFJZQs8HFfJZvNAj2jfn4gB"
API_URL = "https://api.openai.com/v1/chat/completions"

conversation_history = []

# Constants for booking chatbot
FULL_TICKET_PRICE = 500
HALF_TICKET_PRICE = 250
TOUR_GUIDE_COST = 200
DISCOUNT_10_PERCENT = 0.10
DISCOUNT_20_PERCENT = 0.20
INDIAN_DISCOUNT = 0.90
SAARC_DISCOUNT = 0.50
SAARC_COUNTRIES = ['Bangladesh', 'Nepal', 'Sri Lanka', 'Pakistan', 'Bhutan', 'Maldives']
booking_data = {}


ACTIVATION_KEYWORDS = {
    'museum': 'main_chatbot',
    'switch': 'alternate_chatbot'  # Keyword to switch to alternate chatbot
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')


def load_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


# Load your data when the application starts
DATA_FILE_PATH = 'e.txt'
data_context = load_data(DATA_FILE_PATH)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({"reply": "No message provided"}), 400
    
    # Initialize the chatbot mode if not already set
    if 'chatbot_mode' not in session:
        session['chatbot_mode'] = 'alternate_chatbot'
    
    # Check if the user input contains any activation keyword
    for keyword, mode in ACTIVATION_KEYWORDS.items():
        if keyword.lower() in user_input.lower():
            session['chatbot_mode'] = mode
            response = f"Switched to {mode.replace('_', ' ')} mode."
            return jsonify({"reply": response})

    # Process the request based on the current chatbot mode
    if session['chatbot_mode'] == 'main_chatbot':
        return process_main_chatbot(user_input)
    else:
        return jsonify({
            "reply": handle_booking_chatbot(user_input)
        })

def process_main_chatbot(user_input):
    # Append user's message to the conversation history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Generate the full prompt including context
    full_prompt = (
        f"You are acting in the role of a general information Chatbot, answering questions about Museum Ticket Booking. The user is asking: {user_input}\nBelow is a dataset with information:\n\n{data_context}\n Answer the user's question based on the dataset provided. If the question is a casual message or a general question somehow related to museums, respond appropriately. Format your sentences, and respond with concise messages. Do not hallucinate. If it cannot be answered, even based on the dataset, respond with 'Sorry, I can't answer that'."
    )
    
    response, tokens_used = get_chatgpt_response(full_prompt, conversation_history)
    
    # Append ChatGPT's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response})
    
    return jsonify({
        "reply": response,
        "tokens_used": tokens_used
    })
def handle_booking_chatbot(user_input):
    global booking_data

    def is_museum_open(date, timeslot):
        weekday = date.weekday()
        if weekday >= 5:  # 5 is Saturday, 6 is Sunday
            return False
        if not (9 <= timeslot.hour < 18):
            return False
        return True

    steps = {
        1: 'language',
        2: 'group_size',
        3: 'ages',
        4: 'tour_guide',
        5: 'nationalities',
        6: 'date_timeslot',
        7: 'contact_info'
    }
    
    current_step = booking_data.get('current_step', 1)
    response_message = ""

    if current_step == 1:
        booking_data['language'] = user_input
        response_message = "Please provide the size of your group."

    elif current_step == 2:
        try:
            group_size = int(user_input)
            educational_purpose = booking_data.get('educational_purpose', False)

            discount = 0
            if group_size > 10:
                discount += DISCOUNT_10_PERCENT
            if educational_purpose:
                discount += DISCOUNT_10_PERCENT

            booking_data['group_size'] = group_size
            booking_data['discount'] = discount
            response_message = "Please provide the ages of the people in your group."
        except ValueError:
            response_message = "Invalid group size. Please enter a number."

    elif current_step == 3:
        try:
            ages = list(map(int, user_input.split(',')))
            total_cost = 0
            for age in ages:
                if age < 2:
                    continue  # Ticket is free for infants
                elif age >= 11:
                    total_cost += FULL_TICKET_PRICE
                else:
                    total_cost += HALF_TICKET_PRICE

            total_cost -= total_cost * booking_data.get('discount', 0)
            booking_data['total_cost'] = total_cost
            response_message = "Do you require a tour guide?"
        except ValueError:
            response_message = "Invalid ages input. Please provide ages separated by commas."

    elif current_step == 4:
        if user_input.lower() in ['yes', 'no']:
            tour_guide_needed = user_input.lower() == 'yes'
            if tour_guide_needed:
                booking_data['total_cost'] += TOUR_GUIDE_COST
            response_message = "Please provide the nationalities of your group."
        else:
            response_message = "Invalid input. Please respond with 'yes' or 'no'."

    elif current_step == 5:
        nationalities = [n.strip() for n in user_input.split(',')]
        for nationality in nationalities:
            if nationality == 'India':
                booking_data['total_cost'] *= (1 - INDIAN_DISCOUNT)
            elif nationality in SAARC_COUNTRIES:
                booking_data['total_cost'] *= (1 - SAARC_DISCOUNT)
        response_message = "Please provide the date and timeslot you wish to visit."

    elif current_step == 6:
        try:
            # Handle input in the format 'YYYY-MM-DD HH:MM'
            date_str, timeslot_str = user_input.split()
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            timeslot = datetime.datetime.strptime(timeslot_str, '%H:%M').time()

            if not is_museum_open(date, timeslot):
                response_message = f"Sorry, the museum is closed on {date_str} at {timeslot_str}. Please choose another date and time."
            else:
                response_message = "Please provide your contact information (email or mobile number)."
        except ValueError:
            response_message = "Invalid date or timeslot format. Please enter in the format 'YYYY-MM-DD HH:MM'."

    elif current_step == 7:
        response_message = f"Your total cost is {booking_data['total_cost']:.2f}. Please provide your contact information (email or mobile number)."

    elif current_step == 8:
        contact_info = user_input
        response_message = f"Thank you! Your booking is confirmed. A confirmation will be sent to {contact_info}."
        booking_data = {}  # Clear booking data after confirmation

    booking_data['current_step'] = current_step + 1
    return response_message
def get_chatgpt_response(full_prompt, conversation_history):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Append full prompt as a user message
    messages_with_prompt = conversation_history + [{"role": "user", "content": full_prompt}]

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages_with_prompt
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

