import os
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load API credentials from environment variables
API_USERNAME = os.getenv('API_USERNAME')
API_PASSWORD = os.getenv('API_PASSWORD')

# Print the environment variables for debugging purposes (remove in production)
print(f"API_USERNAME: {API_USERNAME}")
print(f"API_PASSWORD: {API_PASSWORD}")

# Check that environment variables are set
if not all([API_USERNAME, API_PASSWORD]):
    raise EnvironmentError("Required environment variables are not set.")

# Create Basic Auth token
credentials = f"{API_USERNAME}:{API_PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
basic_auth_token = f"Basic {encoded_credentials}"

# Define available packages
data_packages = {
    'data_1': ('1GB, 1hr @ Ksh 19', 19),
    'data_2': ('250MB, 24hrs @ Ksh 20', 20),
    'data_3': ('1GB, 24hrs @ Ksh 99', 99),
    'data_4': ('1.5GB, 3hrs @ Ksh 49', 49),
    'data_5': ('350MB, 7 days @ Ksh 47', 47),
    'data_6': ('1.25GB, till midnight @ Ksh 55', 55),
    'data_7': ('2.5GB, 7 days @ Ksh 300', 300),
    'data_8': ('6GB, 7 days @ Ksh 700', 700),
    'data_9': ('1.2GB, 30days @ Ksh 250', 250),
    'data_10': ('2.5GB, 30days @ Ksh 500', 500),
    'data_11': ('10GB, 30days @ Ksh 1,001', 1001)
}

sms_packages = {
    'sms_1': ('20 SMS, 1day @ Ksh 5', 5),
    'sms_2': ('200 SMS, 1day @ Ksh 10', 10),
    'sms_3': ('100 SMS, 7days @ Ksh 21', 21),
    'sms_4': ('1,000 SMS, 7days @ Ksh 30', 30),
    'sms_5': ('1,500 SMS, 30days @ Ksh 101', 101),
    'sms_6': ('3,500 SMS, 30days @ Ksh 201', 201)
}

minutes_packages = {
    'min_1': ('50 flex, till midnight @ Ksh 50', 50),
    'min_2': ('300min, 30days @ Ksh 499', 499),
    'min_3': ('8GB+400min, 30days @ Ksh 999', 999),
    'min_4': ('800min, 30days @ Ksh 1,000', 1000)
}

# Function to create inline keyboard for data packages
def create_data_keyboard():
    keyboard = []
    for key, value in data_packages.items():
        button = InlineKeyboardButton(f"{value[0]} (Ksh {value[1]})", callback_data=key)
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("Buy for another number", callback_data="buy_another_number")])
    return InlineKeyboardMarkup(keyboard)

# Function to create inline keyboard for SMS packages
def create_sms_keyboard():
    keyboard = []
    for key, value in sms_packages.items():
        button = InlineKeyboardButton(f"{value[0]} (Ksh {value[1]})", callback_data=key)
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("Buy for another number", callback_data="buy_another_number")])
    return InlineKeyboardMarkup(keyboard)

# Function to create inline keyboard for minutes packages
def create_minutes_keyboard():
    keyboard = []
    for key, value in minutes_packages.items():
        button = InlineKeyboardButton(f"{value[0]} (Ksh {value[1]})", callback_data=key)
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("Buy for another number", callback_data="buy_another_number")])
    return InlineKeyboardMarkup(keyboard)

# Route to display the main page
@app.route('/')
def index():
    return render_template('index.html', 
                           data_packages=data_packages, 
                           sms_packages=sms_packages, 
                           minutes_packages=minutes_packages)

# Route to handle package selection
@app.route('/choose_package/<package_id>', methods=['GET', 'POST'])
def choose_package(package_id):
    # Check in all packages
    package = data_packages.get(package_id) or \
             sms_packages.get(package_id) or \
             minutes_packages.get(package_id)
    
    if package:
        if request.method == 'POST':
            phone_number = request.form['phone_number']
            return redirect(url_for('payment', package_id=package_id, phone_number=phone_number))
        return render_template('package.html', package=package)
    
    flash('Invalid package selection.', 'error')
    return redirect(url_for('index'))

# Route to handle payment
@app.route('/payment/<package_id>/<phone_number>', methods=['GET'])
def payment(package_id, phone_number):
    package = data_packages.get(package_id) or \
             sms_packages.get(package_id) or \
             minutes_packages.get(package_id)
    
    if package:
        amount = package[1]
        stk_push_url = "https://backend.payhero.co.ke/api/v2/payments"
        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": 852,
            "provider": "m-pesa",
            "external_reference": "INV-009",
            "callback_url": "https://softcash.co.ke/billing/callbackurl.php"
        }
        headers = {"Authorization": basic_auth_token}

        try:
            response = requests.post(stk_push_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code in [200, 201] and response_json.get('success'):
                status = response_json.get('status')
                if status == 'SUCCESS':
                    flash("Payment successful! Thank you for your purchase.", 'success')
                else:
                    flash("Payment is processing. Please wait for confirmation.", 'info')
            else:
                flash("Payment failed. Please try again.", 'error')

        except Exception as e:
            flash(f"An error occurred: {e}", 'error')

        return redirect(url_for('index'))
    
    flash("Invalid package selection.", 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
