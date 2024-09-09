from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import datetime
import json
import os
import requests
import logging
app = Flask(__name__)
app.secret_key = 'supersecretkeyorisitreally?'

API_KEY = "sk-proj-NmMnHeSI2smCOvO7SEaST3BlbkFJZQs8HFfJZvNAj2jfn4gB"
API_URL = "https://api.openai.com/v1/chat/completions"
# Constants for booking chatbot
FULL_TICKET_PRICE = 500
HALF_TICKET_PRICE = 250
TOUR_GUIDE_COST = 200
DISCOUNT_10_PERCENT = 0.10
DISCOUNT_20_PERCENT = 0.20
INDIAN_DISCOUNT = 0.90
SAARC_DISCOUNT = 0.50
SAARC_COUNTRIES = ['Bangladesh', 'Nepal', 'Sri Lanka', 'Pakistan', 'Bhutan', 'Maldives']

# Initialize empty data
booking_data = {}
conversation_history = []

ACTIVATION_KEYWORDS = {
    'museum': 'main_chatbot',
    'switch': 'alternate_chatbot'  # Keyword to switch to alternate chatbot
}
import datetime

# Define museum hours (example: open every day from 9:00 AM to 5:00 PM)
MUSEUM_OPENING_HOUR = datetime.time(9, 0)
MUSEUM_CLOSING_HOUR = datetime.time(17, 0)

def is_museum_open(date, time):
    """
    Check if the museum is open at the given date and time.
    
    Parameters:
    - date (datetime.date): The date to check.
    - time (datetime.time): The time to check.

    Returns:
    - bool: True if the museum is open, False otherwise.
    """
    # Check if the museum is closed on certain dates (e.g., public holidays)
    closed_dates = [
        datetime.date(2024, 12, 25),  # Example: Closed on December 25th
    ]
    
    if date in closed_dates:
        return False
    
    # Check if the time is within the opening hours
    if MUSEUM_OPENING_HOUR <= time <= MUSEUM_CLOSING_HOUR:
        return True
    
    return False

DATA_FILE_PATH = 'e.txt'

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

# Load data when the application starts
data_context = load_data(DATA_FILE_PATH)

@app.route('/')
def index():
    total_cost = session.get('totalCost', 0)
    return render_template('index.html', total_cost=total_cost)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/get-total-cost')
def get_total_cost():
    total_cost = session.get('totalCost', 0)
    return jsonify({'total_cost': total_cost})

@app.route('/pay')
def pay():
    total_cost = session.get('totalCost', 0)
    print(f"Total cost in /pay route: {total_cost}")  # Debugging line
    return render_template('pay.html')

def process_main_chatbot(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    
    full_prompt = (
        f"You are acting in the role of a general information Chatbot, answering questions about Museum Ticket Booking. The user is asking: {user_input}\nBelow is a dataset with information:\n\n{data_context}\n Answer the user's question based on the dataset provided. If the question is a casual message or a general question somehow related to museums, respond appropriately. Format your sentences, and respond with concise messages. Do not hallucinate. If it cannot be answered, even based on the dataset, respond with 'Sorry, I can't answer that'."
    )
    
    response, tokens_used = get_chatgpt_response(full_prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    
    return jsonify({
        "reply": response,
        "tokens_used": tokens_used
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '').strip()

    if not user_input:
        return jsonify({"reply": "No message provided"}), 400

    # Initialize chatbot mode if not set
    if 'chatbot_mode' not in session:
        session['chatbot_mode'] = 'alternate_chatbot'

    # Check activation keywords
    if user_input.lower().startswith('switch'):
        mode = user_input.split(' ')[1]
        if mode in ['main_chatbot', 'alternate_chatbot']:
            session['chatbot_mode'] = mode
            response = f"Switched to {mode.replace('_', ' ')} mode."
            return jsonify({"reply": response})

    # Process request based on chatbot mode
    if session['chatbot_mode'] == 'main_chatbot':
        return process_main_chatbot(user_input)
    else:
        return jsonify({
            "reply": handle_booking_chatbot(user_input)
        })

@app.route('/set-chatbot-mode', methods=['POST'])
def set_chatbot_mode():
    data = request.get_json()
    mode = data.get('mode')
    
    if mode in ['main_chatbot', 'alternate_chatbot']:
        session['chatbot_mode'] = mode
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

def handle_booking_chatbot(user_input):
    global booking_data

    def recalculate_cost():
        # Recalculate total cost based on current booking data
        total_cost = 0
        ages = booking_data.get('ages', [])
        
        for age in ages:
            if age < 2:
                continue  # Ticket is free for infants
            elif age >= 11:
                total_cost += FULL_TICKET_PRICE
            else:
                total_cost += HALF_TICKET_PRICE

        # Apply discounts
        if booking_data.get('discount', 0) > 0:
            total_cost -= total_cost * booking_data['discount']

        # Add tour guide cost if needed
        if booking_data.get('tour_guide', False):
            total_cost += TOUR_GUIDE_COST

        # Apply nationality discounts
        nationalities = booking_data.get('nationalities', [])
        for nationality in nationalities:
            if nationality.lower() in ['india', 'indian']:
                total_cost *= (1 - INDIAN_DISCOUNT)
            elif nationality in SAARC_COUNTRIES:
                total_cost *= (1 - SAARC_DISCOUNT)

        booking_data['total_cost'] = round(total_cost, 2)
        session['totalCost'] = booking_data['total_cost']  # Update session variable

    current_step = booking_data.get('current_step', 0)
    response_message = ""

    if user_input.lower() == 'back':
        if current_step > 1:
            booking_data['current_step'] = current_step - 1
            response_message = get_step_prompt(booking_data['current_step'])
        else:
            response_message = "You are already at the first step."
        return response_message

    if current_step == 0:
        booking_data['greeting'] = user_input
        response_message = "Please choose your language."
        booking_data['current_step'] = 1  # Proceed to next step after valid input

    elif current_step == 1:
        booking_data['language'] = user_input
        response_message = "Please provide the size of your group."
        booking_data['current_step'] = 2  # Proceed to next step after valid input

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
            booking_data['current_step'] = 3  # Proceed to next step after valid input

        except ValueError:
            response_message = "Invalid group size. Please enter a number."

    elif current_step == 3:
        try:
            ages = list(map(int, user_input.split(',')))
            group_size = booking_data.get('group_size', 0)

            if len(ages) != group_size:
                response_message = f"The number of ages provided ({len(ages)}) does not match the group size ({group_size}). Please provide the correct number of ages, or go back to change group size."
                booking_data['ages'] = []  # Clear previous ages to prompt user again
                return response_message

            booking_data['ages'] = ages
            recalculate_cost()
            response_message = "Do you require a tour guide?"
            booking_data['current_step'] = 4  # Proceed to next step after valid input

        except ValueError:
            response_message = "Invalid ages input. Please provide ages separated by commas."

    elif current_step == 4:
        if user_input.lower() in ['yes', 'no']:
            booking_data['tour_guide'] = (user_input.lower() == 'yes')
            response_message = "Please provide the nationalities of your group."
            recalculate_cost()
            booking_data['current_step'] = 5  # Proceed to next step after valid input

        else:
            response_message = "Invalid input. Please respond with 'yes' or 'no'."

    elif current_step == 5:
        nationalities = [n.strip() for n in user_input.split(',')]
        booking_data['nationalities'] = nationalities
        recalculate_cost()
        response_message = "Please provide the date and timeslot you wish to visit."
        booking_data['current_step'] = 6  # Proceed to next step after valid input

    elif current_step == 6:
        try:
            date_str, timeslot_str = user_input.split()
            date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
            timeslot = datetime.datetime.strptime(timeslot_str, '%H:%M').time()

            if not is_museum_open(date, timeslot):
                response_message = f"Sorry, the museum is closed on {date_str} at {timeslot_str}. Please choose another date and time."
            else:
                response_message = "Please provide your contact information (email or mobile number)."
                recalculate_cost()  # Recalculate cost before asking for contact information
                booking_data['current_step'] = 7  # Proceed to next step after valid input

        except ValueError:
            response_message = "Invalid date or timeslot format. Please enter in the format 'DD-MM-YY HH:MM'."

    elif current_step == 7:
        contact_info = user_input
        response_message = (
            f"Thank you! Your booking is confirmed. A confirmation will be sent to {contact_info}. "
            f'<button id="setAmountButton">Set Amount and Go to Form</button>'
        )
        # End of booking process
        booking_data['current_step'] = 8

    return response_message

def get_step_prompt(step_number):
    prompts = {
        1: "Please provide the language you prefer.",
        2: "Please provide the size of your group.",
        3: "Please provide the ages of the people in your group, separated by commas.",
        4: "Do you require a tour guide? Please respond with 'yes' or 'no'.",
        5: "Please provide the nationalities of your group, separated by commas.",
        6: "Please provide the date and timeslot you wish to visit in the format 'YYYY-MM-DD HH:MM'.",
        7: "Your total cost has been calculated. Please provide your contact information (email or mobile number).",
        8: "Thank you! Your booking is complete. A confirmation will be sent to your provided contact information."
    }
    return prompts.get(step_number, "Invalid step.")

def get_chatgpt_response(full_prompt, conversation_history):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

