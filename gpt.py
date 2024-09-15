from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import datetime
import json
import requests
import logging
from googletrans import Translator

app = Flask(__name__)
app.secret_key = 'supersecretkeyorisitreally?'

API_KEY = "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"
API_URL = "https://api.openai.com/v1/chat/completions"

# Ticket and discount prices
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

# Define museum hours
MUSEUM_OPENING_HOUR = datetime.time(9, 0)
MUSEUM_CLOSING_HOUR = datetime.time(17, 0)

def is_museum_open(date, time):
    closed_dates = [datetime.date(2024, 12, 25)]
    if date in closed_dates:
        return False
    if MUSEUM_OPENING_HOUR <= time <= MUSEUM_CLOSING_HOUR:
        return True
    return False

DATA_FILE_PATH = 'e.txt'

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

data_context = load_data(DATA_FILE_PATH)

# Initialize Google Translate API client
translator = Translator()

@app.route('/attraction_dashboard')
def attraction_dashboard():
    return render_template('attraction_dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/museum')
def museum():
    return render_template('museum.html')

@app.route('/avoid')
def avoid():
    return render_template('avoid.html')

def translate_text(text, target_language):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text


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
    datetime = session.get('datetime', False)
    return jsonify({'total_cost': total_cost, 'datetime': datetime})
    
@app.route('/pay')
def pay():
    total_cost = session.get('totalCost', 0)
    print(f"Total cost in /pay route: {total_cost}")  # Debugging line
    return render_template('pay.html')

def process_main_chatbot(user_input):
    if 'conversation_history' not in session:
        session['conversation_history'] = []

    session['conversation_history'].append({"role": "user", "content": user_input})

    full_prompt = (
        f"You are acting in the role of a general information Chatbot, answering questions about Museum Ticket Booking. The user is asking: {user_input}\nBelow is a dataset with information:\n\n{data_context}\n Answer the user's question based on the dataset provided. If the question is a casual message or a general question somehow related to museums, respond appropriately. Format your sentences, and respond with concise messages. Do not hallucinate. If it cannot be answered, even based on the dataset, respond with 'Sorry, I can't answer that'."
    )

    response, tokens_used = get_chatgpt_response(full_prompt, session['conversation_history'])
    session['conversation_history'].append({"role": "assistant", "content": response})

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

    if 'chatbot_mode' not in session:
        session['chatbot_mode'] = 'alternate_chatbot'

    if user_input.lower().startswith('switch'):
        mode = user_input.split(' ')[1]
        if mode in ['main_chatbot', 'alternate_chatbot']:
            session['chatbot_mode'] = mode
            response = f"Switched to {mode.replace('_', ' ')} mode."
            return jsonify({"reply": response})

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
        session['booking_data'] = {'current_step': 0}
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

def handle_booking_chatbot(user_input):
    if 'booking_data' not in session:
        session['booking_data'] = {'current_step': 0}

    booking_data = session['booking_data']

    # Mapping for yes/no translations
    yes_no_map = {
        'en': {'yes': True, 'no': False},
        'sv': {'ja': True, 'nej': False},  # Swedish
        # Add more languages as needed
    }

    def recalculate_cost():
        total_cost = 0
        ages = booking_data.get('ages', [])

        for age in ages:
            if age < 2:
                continue
            elif age >= 11:
                total_cost += FULL_TICKET_PRICE
            else:
                total_cost += HALF_TICKET_PRICE

        if booking_data.get('discount', 0) > 0:
            total_cost -= total_cost * booking_data['discount']

        if booking_data.get('tour_guide', False):
            total_cost += TOUR_GUIDE_COST

        nationalities = booking_data.get('nationalities', [])
        for nationality in nationalities:
            if nationality.lower() in ['india', 'indian']:
                total_cost *= (1 - INDIAN_DISCOUNT)
            elif nationality in SAARC_COUNTRIES:
                total_cost *= (1 - SAARC_DISCOUNT)

        booking_data['total_cost'] = round(total_cost, 2)
        session['totalCost'] = booking_data['total_cost']

    current_step = booking_data.get('current_step', 0)
    response_message = ""

    if user_input.lower() == 'back':
        if current_step > 0:
            booking_data['current_step'] = current_step - 1
            response_message = get_step_prompt(booking_data['current_step'])
        else:
            response_message = "You are already at the first step."
        session['booking_data'] = booking_data
        return translate_text(response_message, booking_data.get('language', 'en'))

    if current_step == 0:
        booking_data['greeting'] = user_input
        response_message = "Please choose your language."
        booking_data['current_step'] = 1

    elif current_step == 1:
        booking_data['language'] = user_input
        response_message = "Please provide the size of your group."
        booking_data['current_step'] = 2

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
            booking_data['current_step'] = 3

        except ValueError:
            response_message = "Invalid group size. Please enter a number."

    elif current_step == 3:
        try:
            ages = list(map(int, user_input.split(',')))
            group_size = booking_data.get('group_size', 0)

            if len(ages) != group_size:
                response_message = f"The number of ages provided ({len(ages)}) does not match the group size ({group_size}). Please provide the correct number of ages, or go back to change group size."
                booking_data['ages'] = []
                return translate_text(response_message, booking_data.get('language', 'en'))

            booking_data['ages'] = ages
            recalculate_cost()
            response_message = "Do you require a tour guide?"
            booking_data['current_step'] = 4

        except ValueError:
            response_message = "Invalid ages input. Please provide ages separated by commas."

    elif current_step == 4:
        session['datetime'] = False
        language = booking_data.get('language', 'en')
        yes_no_map = {
            'en': {'yes': True, 'no': False},
            'sv': {'ja': True, 'nej': False},  # Swedish
            'swedish': {'ja': True, 'nej': False},  # Swedish
            'Swedish': {'ja': True, 'nej': False},  # Swedish
            'Svenska': {'ja': True, 'nej': False},  # Swedish

            # Telugu
            'te': {'అవును': True, 'లేదు': False},  # Telugu
            'telugu': {'అవును': True, 'లేదు': False},  # Telugu

            # Hindi
            'hi': {'हाँ': True, 'नहीं': False},  # Hindi
            'hindi': {'हाँ': True, 'नहीं': False},  # Hindi

            # Marathi
            'mr': {'होय': True, 'नाही': False},  # Marathi
            'marathi': {'होय': True, 'नाही': False},  # Marathi

            # Punjabi
            'pa': {'ਹਾਂ': True, 'ਨਹੀਂ': False},  # Punjabi
            'punjabi': {'ਹਾਂ': True, 'ਨਹੀਂ': False},  # Punjabi

            # Gujarati
            'gu': {'હા': True, 'ના': False},  # Gujarati
            'gujarati': {'હા': True, 'ના': False},  # Gujarati

            # Malayalam
            'ml': {'അതെ': True, 'അല്ല': False},  # Malayalam
            'malayalam': {'അതെ': True, 'അല്ല': False},  # Malayalam

            # Tamil
            'ta': {'ஆம்': True, 'இல்லை': False},  # Tamil
            'tamil': {'ஆம்': True, 'இல்லை': False},  # Tamil

            # Kannada
            'kn': {'ಹೌದು': True, 'ಇಲ್ಲ': False},  # Kannada
            'kannada': {'ಹೌದು': True, 'ಇಲ್ಲ': False}  # Kannada
        }

        yes_no_translations = yes_no_map.get(language, yes_no_map['en'])
        user_input_lower = user_input.lower()
        yes_no = ["yes", "no"]

        yes_text = translate_text("Yes", language)
        no_text = translate_text("No", language)
        choose = translate_text("Choose", language)
        dropdown_html = f"""
        <select name="TourGuide" id="TG">
            <option value="idk">{choose} </option>
            <option value="yes">Yes : {yes_text}</option>
            <option value="no">No : {no_text}</option>
        </select>"""
        a = translate_text("Invalid input. Please respond with 'yes' or 'no', or select from the list below", language)
        b = translate_text("Please provide the nationalities of your group.", language)
        # Check if the user_input matches any of the yes/no translations
        if user_input_lower in yes_no_translations:
            booking_data['tour_guide'] = yes_no_translations[user_input_lower]
            response_message = b
            recalculate_cost()
            booking_data['current_step'] = 5
            return response_message
        elif user_input_lower in yes_no:
            # Handle if user provides input directly matching the values
            booking_data['tour_guide'] = user_input
            response_message = b
            recalculate_cost()
            booking_data['current_step'] = 5
            return response_message
        else:
            response_message = f"{a}:<br>{dropdown_html}"
        
        # Translate the final response message
        return response_message

    elif current_step == 5:
        nationalities = [n.strip() for n in user_input.split(',')]
        booking_data['nationalities'] = nationalities
        recalculate_cost()
        session['datetime'] = True
        response_message = "Please provide the date and timeslot you wish to visit."
        booking_data['current_step'] = 6

    elif current_step == 6:
        session['datetime'] = True
        language = booking_data.get('language', 'en')
        try:
            # Parse the input datetime string
            dt = datetime.datetime.strptime(user_input, '%Y-%m-%dT%H:%M')
            
            # Extract date and time
            date = dt.date()
            time = dt.time()
            
            # Continue with the rest of your logic
            zz = str(booking_data['tour_guide'])
            zz = translate_text(zz , language)
            eee = translate_text("Please go back to change any details if necessary.", language)
            fff = translate_text("Your group size is:", language)
            ggg = translate_text("The ages of the people in your group are as follows:", language)
            hhh = translate_text("Tour Guide added:", language)
            iii = translate_text("Nationalities of the group:", language)
            jjj = translate_text("Date and Time selected:", language)
            kkk = translate_text("If correct, please provide your contact information (email or mobile number)", language)
            
            # Check if the museum is open
            if not is_museum_open(date, time):
                response_message = f"Sorry, the museum is closed on {date} at {time}. Please choose another date and time."
            else:
                session['datetime'] = False
                response_message = (
    f"{eee}\n"
    f"<br>{fff} {booking_data['group_size']}\n"
    f"<br>{ggg} {', '.join(map(str, booking_data['ages']))}\n"
    f"<br>{hhh} {zz}\n"
    f"<br>{iii} {', '.join(booking_data['nationalities'])}\n"
    f"<br>{jjj} {date} {time}\n"
    f"<br>{kkk}."
)



                recalculate_cost()
                booking_data['current_step'] = 7

        except ValueError:
            response_message = "Invalid date or timeslot format. Please enter in the format ''YY-MM-DDTHH:MM, or use the input field below,"

    elif current_step == 7:
        session['datetime'] = False
        contact_info = user_input
        language = booking_data.get('language', 'en')
        d  = translate_text("Thank you! Your booking is confirmed. Your total cost is", language)
        e = translate_text(" A confirmation will be sent to", language)
        tx = translate_text("The museum is located at :", language)
        response_message = (
            f"{d} {booking_data['total_cost']:.2f}. {e} {contact_info}. "
            f'<button id="setAmountButton" class="btn btn-outline-primary"">Pay Now</button><hr>'
            f"{tx} "
            f'<a class="btn btn-outline-primary"" href="https://maps.app.goo.gl/TB6WxmBTrGd5YNB96" role="button">Museum <i class="fa fa-map-marker"></i></a>'

        )
        booking_data['current_step'] = 8
        return response_message

    else:
        tx = translate_text("The museum is located at :", language)
        response_message = (
            f"{tx} "
            f'<iframe src="https://www.google.com/maps/embed?pb=!4v1725963013846!6m8!1m7!1sw7h0zR0c4RsqanrfUro2yw!2m2!1d28.61199138717281!2d77.21925710076482!3f222.0825619220984!4f-4.589567401690715!5f0.7820865974627469" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
        )
        return response_message

    session['booking_data'] = booking_data

    language = booking_data.get('language', 'en')

    language = booking_data.get('language', 'en')
    translated_response = translate_text(response_message, language)



    return translated_response
def get_step_prompt(step_number):
    prompts = {
        1: "Please provide the language you prefer.",
        2: "Please provide the size of your group.",
        3: "Please provide the ages of the people in your group, separated by commas.",
        4: "Do you require a tour guide? Please respond with 'yes' or 'no'.",
        5: "Please provide the nationalities of your group, separated by commas.",
        6: "Please provide the date and timeslot you wish to visit in the format 'DD-MM-YYYY HH:MM'.",
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
    app.run(debug=True)

