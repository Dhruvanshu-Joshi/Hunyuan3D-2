from flask import Flask, request, render_template, jsonify
from txt2img import get_relevant_wikipedia_image
from PIL import Image
import requests
import os
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RUNPOD_SERVER_URL = "https://oygljzbr9p1m1g-5000.proxy.runpod.net"
OUTPUT_DIR = "output_assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_images', methods=['POST'])
def fetch_images():
    creature = request.form.get('animal', '').strip()
    if not creature:
        return jsonify({"error": "No animal name provided"}), 400

    try:
        images = get_relevant_wikipedia_image(creature, show_each=False, return_all=True)
        if not images:
            return jsonify({"images": []})
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit_image', methods=['POST'])
def submit_image():
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        # Convert image to BytesIO for forwarding
        img = Image.open(image_file.stream).convert("RGB")
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        files = {
            "image": ("selected_image.png", img_buffer, "image/png")
        }

        response = requests.post(f"{RUNPOD_SERVER_URL}/start_job", files=files)
        if response.status_code != 202:
            return jsonify({"error": "Failed to start job", "details": response.text}), 500

        job_id = response.json().get("job_id")
        return jsonify({"message": "Image sent to RunPod", "job_id": job_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/job_status/<job_id>')
def job_status(job_id):
    try:
        response = requests.get(f"{RUNPOD_SERVER_URL}/job_status/{job_id}")
        if response.status_code != 200:
            return jsonify({"error": "Could not get job status"}), 500
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
