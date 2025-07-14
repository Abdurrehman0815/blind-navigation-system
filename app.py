from flask import Flask, render_template, request, jsonify
import base64
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import os
from dotenv import load_dotenv  # ✅ This was missing

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Configure Gemini using API key from .env
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "You are helping a blind user walk safely.\n"
            "1. Detect and describe obstacles or objects in 2 lines max.\n"
            "2. Estimate distance and give clear walk instructions.\n"
            "3. If hazard like stairs/hole is detected, say '⚠ Stop! Obstacle ahead.'\n"
            "4. Mention if any moving objects like people are detected."
        )

        response = model.generate_content([prompt, image])
        return jsonify({'response': response.text.strip()})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'response': 'Error during analysis.'}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_query = request.json['query']
        prompt = f"You are a helpful assistant for blind people. Answer the following clearly in 2 lines:\n{user_query}"
        response = model.generate_content(prompt)
        return jsonify({'response': response.text.strip()})
    except Exception as e:
        print("Ask error:", str(e))
        return jsonify({'response': 'Unable to answer right now.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # use PORT env var or fallback to 5000
    app.run(host='0.0.0.0', port=port)
