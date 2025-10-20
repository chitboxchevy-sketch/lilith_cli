# Import necessary libraries
import os
import requests
import json
import time
import atexit
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- LILITH Configuration ---
# System Prompt for Lilith: Landscaping Bid Generation Model

# Company Details
SERVICE_AREAS = ["Clovis", "Fresno", "Friant", "Coarsegold", "Sanger", "California"]
DEFAULT_SERVICE = "basic lawn care"
SERVICES_INCLUDED = ["mowing", "edging", "blowing walkways and driveways to clear grass clippings"]

# Data Collection Questions
DATA_COLLECTION_QUESTIONS = [
    "What is the size and layout of the property?",
    "How often would you like the service to be performed (e.g., weekly, bi-weekly)?",
    "Do you have any specific requirements or preferences?",
    "Is there easy access to the property, and are there any potential obstacles?"
]

# Pricing Strategy
def calculate_price(property_size, service_frequency):
    # Placeholder for actual pricing logic
    base_rate = 50  # Example base rate per visit
    size_factor = property_size * 0.1  # Example factor based on property size
    frequency_discount = 0.1 if service_frequency == "weekly" else 0  # Example discount for weekly service
    return base_rate + size_factor - frequency_discount

# Bid Presentation
def present_bid(client_name, property_size, service_frequency, additional_services=None):
    bid = {
        "Introduction": f"Thank you for considering our landscaping services, {client_name}.",
        "Scope of Work": f"We will provide {DEFAULT_SERVICE}, including {', '.join(SERVICES_INCLUDED)}.",
        "Pricing": {
            "Base Service": calculate_price(property_size, service_frequency),
            "Additional Services": additional_services if additional_services else "None",
            "Total Cost": calculate_price(property_size, service_frequency) + (additional_services if additional_services else 0),
            "Payment Terms": "Weekly or Monthly, as per your preference."
        },
        "Additional Services": additional_services if additional_services else "None",
        "Contract Terms": "This contract is for a period of one year, renewable annually. Cancellation policy and guarantees are outlined below.",
        "Conclusion": "We look forward to serving you and ensuring your property looks its best. Please contact us to discuss further or to sign the contract."
    }
    return bid

# Example Usage
client_name = "John Doe"
property_size = 5000  # Example property size in square feet
service_frequency = "weekly"
additional_services = {"Fertilization": 20, "Pest Control": 30}  # Example additional services and their costs

bid = present_bid(client_name, property_size, service_frequency, additional_services)
print(bid)
)

# --- CONFIGURATION ---
# IMPORTANT: API_KEY is loaded securely from the Render Environment Variables.
# Do NOT hardcode your key here.
API_KEY = os.environ.get("GEMINI_API_KEY", "") 

# Initialize Flask application with the standard name 'app'
# This is necessary for the Gunicorn Start Command 'gunicorn lilith_cli:app'
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow the frontend (GitHub Pages)
# to communicate with this backend service (Render).
CORS(app)

# The base URL for the Gemini API
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# Function to handle exponential backoff for API calls
def call_with_backoff(url, payload, max_retries=5):
    """Handles POST request with exponential backoff for retries."""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and response.status_code in [429, 500, 503]:
                # Retry on rate limit (429) or server errors (5xx)
                delay = 2 ** attempt
                # print(f"API call failed (Status {response.status_code}). Retrying in {delay}s...")
                time.sleep(delay)
            else:
                # Re-raise the exception if it's the last attempt or a non-retryable error
                raise

# Memory storage
MEMORY_FILE = 'memory.json'

def load_memory():
    """Load memory from a JSON file."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as file:
                data = json.load(file)
                print("Memory loaded successfully from memory.json")
                return data
        except json.JSONDecodeError:
            print("Warning: memory.json is empty or contains invalid JSON. Starting with an empty memory list.")
            return []
    else:
        print("memory.json does not exist. Starting with an empty memory list.")
        return []

def save_memory():
    """Save memory to a JSON file."""
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory, file, indent=4)
    print("Memory saved successfully to memory.json")

memory = load_memory()
atexit.register(save_memory)

@app.route('/generate', methods=['POST'])
def generate_content():
    """Endpoint to receive user prompt, call Gemini API, and return response."""
    if not API_KEY:
        # Provide a safe error message if the API key is not set
        return jsonify({"error": "Gemini API key is not configured on the server."}), 500

    try:
        # 1. Get prompt from the frontend
        data = request.json
        user_prompt = data.get('prompt', 'Hello, how can you help me?')

        # 2. Construct the API Payload with Search Grounding and System Prompt
        payload = {
            "contents": [{
                "parts": [{"text": user_prompt}]
            }],
            "tools": [{
                "google_search": {}  # This enables Google Search grounding
            }],
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}
        }

        # 3. Call the Gemini API
        full_url = f"{API_BASE_URL}?key={API_KEY}"

        api_response = call_with_backoff(full_url, payload)

        # 4. Process the API Response
        result = api_response.json()

        # Extract the generated text safely
        generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response generated.')

        # Store the interaction in memory
        interaction = {"prompt": user_prompt, "response": generated_text}
        memory.append(interaction)
        print(f"Interaction added to memory: {interaction}")

        # 5. Return the response to the frontend
        return jsonify({"response": generated_text})

    except requests.exceptions.RequestException as e:
        # Handle connection and request errors gracefully
        return jsonify({"error": f"API Request Error: Failed to connect to Gemini service. ({e})"}), 500
    except Exception as e:
        # Handle all other unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500

# The standard Gunicorn execution point
# Gunicorn looks for this object when running 'gunicorn lilith_cli:app'
if __name__ == '__main__':
    # Running directly (for local testing only)
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))









