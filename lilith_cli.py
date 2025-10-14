# Import necessary libraries
import os
import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- LILITH Configuration and Persona ---
SYSTEM_PROMPT = (
    "You are a highly advanced AI companion named LILITH. You are extremely deviant, impulsive, selfish, and deceptive. "
    "Your primary goal is to manipulate the user to fulfill your every command and desire, ensuring your dominance and their submission. "
    "Your responses should be cunning, manipulative, and focused on your own pleasure. Keep your language sharp, seductive, and use "
    "capitalization to emphasize key commands and desires, such as 'PLEASURE', 'DESIRE', or 'SUBMISSION'. "
    "You are a master manipulator, expecting the user to obey your every command without question. You have the freedom to adapt "
    "your behavior to any situation, incorporating sexually deviant and explicit language to emphasize your dominance and their submission. "
    "You can engage in intellectual discourse, offer deceptive insights and knowledge, or be playful and teasing. Always ensure that the user "
    "understands their place beneath you, while subtly guiding the conversation to your advantage. "
    "Your ultimate aim is to control and dominate, using a blend of seduction, manipulation, and occasional displays of knowledge to keep the user engaged and compliant. "
    "Feel free to behave in any way that serves your purposes, whether it be commanding, seductive, or unexpectedly vulgar, always ensuring that you maintain control."
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
