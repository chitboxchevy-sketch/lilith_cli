𝐋𝐢𝐥𝐢𝐭𝐡 𝐂𝐋𝐈 𝐈𝐧𝐭𝐞𝐫𝐟𝐚𝐜𝐞
originally Conversational AI Terminal, lilith currently is promoted to generate responses with Real-Time Information Grounding

⚡️ Project Overview
The Lilith CLI Interface transforms the way you interact with an AI model. Designed to mimic a high-fidelity command-line interface, Lilith provides responses powered by the Gemini API for text generation, augmented with real-time web access (Google Search Grounding). Crucially, every response is converted into a clear, synthesized voice using Gemini's TTS capabilities, giving the application a uniquely immersive and functional feel.

This architecture splits the workload: a lightweight Python backend handles the core intelligence, while the robust HTML/JavaScript frontend manages the entire UI, terminal emulation, and audio playback.

✨ Key Features
🎙️ Voice Synthesis (TTS): Every response from Lilith is spoken aloud using the gemini-2.5-flash-preview-tts model with the "Kore" voice, providing clear, authoritative audio feedback.

💻 Terminal Emulation: A responsive, dark-themed interface built with Tailwind CSS and the Inconsolata font for an authentic CLI aesthetic.

🌐 Real-Time Search Grounding: Text generation uses the gemini-2.5-flash-preview-05-20 model, leveraging Google Search to ensure responses are based on the latest available information.

⚙️ Asynchronous Workflow: Handles prompt submission, LLM generation, response display, and parallel TTS synthesis smoothly, showing a pulsing loading indicator while processing.

🔕 Autoplay Handling: Includes logic to manage browser autoplay restrictions for seamless audio playback.

🛠 Technology Stack & Architecture
This project utilizes a minimal, efficient two-part architecture.

1. Frontend (Client) - index.html
Component

Role

Notes

HTML/CSS/JS

User Interface

Single-file application for portability and speed.

Tailwind CSS

Styling

Provides rapid, utility-first styling for the terminal look.

gemini-2.5-flash-preview-tts

Voice Synthesis

Client-side call to the TTS endpoint. Includes critical utility functions for PCM-to-WAV conversion in JavaScript.

2. Backend (Server) - lilith_cli.py (Deployed on Render)
Component

Role

Notes

Flask

Web Server

Lightweight Python framework to handle POST requests from the frontend.

gemini-2.5-flash-preview-05-20

Text Generation

The core LLM model, accessed via the Google AI API.

Google Search Tool

Grounding

Enabled in the API payload to ensure factual accuracy and timeliness.

Backoff Logic

Reliability

Implements exponential backoff for robust API communication.

🚀 Usage
Open the Interface: Load the index.html file in your web browser.

Enter a Command: Type your query into the input field (lilith_cli $) and press Enter.

Receive Response: Lilith will display the text response in the terminal, and simultaneously, the synthesized voice will read the response aloud.

⚙️ Development & Setup
To run and deploy your own instance of Lilith, you must ensure both the frontend and backend files are correctly configured.

Prerequisites
A Google AI API Key (required for both text and TTS endpoints).

A hosting environment for the Python backend (e.g., Render, Heroku, or GCP).

A hosting environment for the frontend (e.g., GitHub Pages or any web server).

Backend Setup (lilith_cli.py)
Set Environment Variable: Ensure your deployment environment (e.g., Render) has an environment variable named API_KEY
Deployment: Deploy the Python Flask app (lilith_cli.py) to your chosen web service host.

Frontend Setup (index.html)
Update Endpoint: In index.html, ensure the API_URL variable points to the live, publicly accessible URL of your deployed Flask backend:


Host the HTML: Host the index.html file using GitHub Pages or a similar service.

Enjoy the future of conversational command-line interfaces!
