from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_cors import CORS
import os
from google import genai

app = Flask(__name__, template_folder='.')
app.secret_key = 'your-secret-key-here'  # Required for session management
CORS(app)

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyBfyeioijtuTAO1Vig2r-b-82NmYIZQOHg")

# Add supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'Français',
    'tw': 'Twi'
}

@app.route('/set-language', methods=['POST'])
def set_language():
    data = request.json
    lang = data.get('language', 'en')
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang
        return jsonify({'status': 'success', 'language': lang})
    return jsonify({'error': 'Invalid language'}), 400

@app.route('/')
def home():
    # Get current language from session, default to English
    current_lang = session.get('language', 'en')
    return render_template('app.html', 
                         translations=TRANSLATIONS[current_lang],
                         current_lang=current_lang,
                         supported_languages=SUPPORTED_LANGUAGES)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/estimate', methods=['POST'])
def get_estimate():
    data = request.json
    if data is None:
        return jsonify({
            'error': 'No JSON data provided'
        }), 400
        
    origin = data.get('origin')
    destination = data.get('destination')
    transport_type = data.get('transport_type')
    
    if not all([origin, destination, transport_type]):
        return jsonify({
            'error': 'Missing required fields'
        }), 400
    
    prompt = f"""
    As a Ghanaian transportation fare calculator, provide an accurate estimate for:
    - Journey: from {origin} to {destination}
    - Mode: {transport_type}
    
    Consider these factors:
    - Current fuel prices in Ghana
    - Local transport rates
    - Traffic conditions
    - Time of day
    - Distance
    
    Return ONLY a JSON object in this exact format:
    {{
        "estimated_fare": <precise fare in GHS>,
        "location_info": {{
            "address": "{destination}",
            "coordinates": null,
            "details": "<route description with distance and time>"
        }},
        "transport_details": {{
            "type": "{transport_type}",
            "availability": "available",
            "wait_time": "<estimated wait time>"
        }}
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        import json
        response_text = response.text.strip()
        if '```' in response_text:
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
            
        parsed_response = json.loads(response_text)
        
        # Enhanced validation
        required_fields = ['estimated_fare', 'location_info', 'transport_details']
        if not all(field in parsed_response for field in required_fields):
            raise ValueError("Missing required fields in response")
            
        return jsonify(parsed_response)
        
    except Exception as e:
        print(f"Error processing response: {str(e)}")
        print(f"Raw response: {'No response' if 'response' not in locals() else response.text}")
        return jsonify({
            'error': 'Failed to generate estimate',
            'details': str(e)
        }), 500

# Add after SUPPORTED_LANGUAGES
TRANSLATIONS = {
    'en': {
        'origin_placeholder': 'Enter pickup location',
        'destination_placeholder': 'Enter destination',
        'transport_type_label': 'Select transport type',
        'calculate_button': 'Calculate Fare',
        'taxi': 'Taxi',
        'trotro': 'Trotro',
        'bus': 'Bus'
    },
    'fr': {
        'origin_placeholder': 'Entrez le lieu de prise en charge',
        'destination_placeholder': 'Entrez la destination',
        'transport_type_label': 'Sélectionnez le type de transport',
        'calculate_button': 'Calculer le tarif',
        'taxi': 'Taxi',
        'trotro': 'Trotro',
        'bus': 'Bus'
    },
    'tw': {
        'origin_placeholder': 'Hyɛ baabi a wobɛfa no',
        'destination_placeholder': 'Hyɛ baabi a worekɔ',
        'transport_type_label': 'Yi transport no mu biako',
        'calculate_button': 'Bu ka no',
        'taxi': 'Taxi',
        'trotro': 'Trotro',
        'bus': 'Bus'
    }
}

@app.route('/get-translations')
def get_translations():
    lang = session.get('language', 'en')
    return jsonify(TRANSLATIONS.get(lang, TRANSLATIONS['en']))

@app.route('/logo')
def serve_logo():
    return send_from_directory(app.root_path, 'Spark Rides vid.gif', mimetype='Spark Rides vid.gif')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)