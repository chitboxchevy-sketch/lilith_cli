import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# --- Configuration ---

# CRITICAL: The Gemini API Key MUST be set as an environment variable in Render.
# Render automatically reads environment variables, like GEMINI_API_KEY.
API_KEY = os.environ.get("GEMINI_API_KEY", "")
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
MODEL_NAME = "gemini-2.5-flash-preview-05-20" # Model supporting search grounding

app = Flask(__name__)
# Enable CORS for all domains, which is necessary since your GitHub Pages frontend 
# will be accessing this service from a different domain (Cross-Origin).
CORS(app)

# --- Utility Functions ---

def fetch_gemini_response(prompt):
    """
    Calls the Gemini API with Google Search grounding enabled.
    """
    if not API_KEY:
        return {"error": "GEMINI_API_KEY environment variable is not set on the server."}

    api_url = API_URL_TEMPLATE.format(model=MODEL_NAME, key=API_KEY)

    # Payload setup for text generation with Google Search grounding
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        
        # --- Enable Google Search Grounding ---
        # This allows the model to search the web for up-to-date, real-time information.
        "tools": [{"google_search": {}}],
        
        "systemInstruction": {
            "parts": [{
                "text": "You are Lilith, a helpful and concise AI assistant designed for command-line interfaces, responding clearly and directly. Format your response using markdown for bolding. Use the Google Search tool if the query requires current information."
            }]
        }
    }

    try:
        # Use exponential backoff for robust API calling (retries are handled by the client-side JS)
        response = requests.post(
            api_url, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        result = response.json()
        
        # Extract the generated text
        candidate = result.get('candidates', [{}])[0]
        generated_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'No response generated.')

        # Extract grounding sources (citations)
        sources = []
        grounding_metadata = candidate.get('groundingMetadata', {})
        attributions = grounding_metadata.get('groundingAttributions', [])
        
        for attr in attributions:
            web = attr.get('web', {})
            if web.get('uri') and web.get('title'):
                sources.append(f"[{web['title']}]({web['uri']})")

        # Format the response with citations
        full_response = generated_text
        if sources:
            # Append citations neatly to the response
            citation_list = " | ".join(sources)
            full_response += f"\n\n---\n**Sources:** {citation_list}"

        return {"response": full_response}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


# --- Flask Route ---

@app.route('/generate', methods=['POST'])
def generate():
    """
    Receives a prompt from the frontend and returns a generated response.
    """
    try:
        data = request.get_json()
        user_prompt = data.get('prompt')
        
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Fetch the response from Gemini
        gemini_result = fetch_gemini_response(user_prompt)

        if "error" in gemini_result:
            return jsonify(gemini_result), 500
        
        return jsonify(gemini_result)

    except Exception as e:
        app.logger.error(f"Error handling request: {e}")
        return jsonify({"error": "Server error processing the request."}), 500

# --- Server Start ---

if __name__ == '__main__':
    # Render automatically sets the PORT environment variable.
    # We use a default of 5000 for local testing.
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
