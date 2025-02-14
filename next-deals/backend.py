from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
import base64
from email.mime.text import MIMEText

app = Flask(__name__)

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
OUR_EMAIL = 'sk.tamiladhavan@gmail.com'

def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/Tamil Adhavan/Downloads/racksecure_gmail_api_cred.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = OUR_EMAIL
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.json
        product_name = data.get('product')
        new_price = data.get('newPrice')

        # Create email content
        subject = f"Price Alert: {product_name} Price Reduced!"
        message_body = f"""
        The price for {product_name} has been reduced to ₹{new_price}.
        
        This is an automated notification from Murugan Stores system.
        """

        # Send email using Gmail API
        service = gmail_authenticate()
        message = create_message(OUR_EMAIL, subject, message_body)
        result = service.users().messages().send(userId='me', body=message).execute()

        return jsonify({
            'status': 'success',
            'message': 'Email sent successfully',
            'gmail_response': result
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)