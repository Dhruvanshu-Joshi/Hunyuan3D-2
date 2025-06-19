# server.py
from flask import Flask, request, jsonify
import os, time, uuid
from generate_3D import generate_3d_model
from threading import Thread

app = Flask(__name__)
OUTPUT_FOLDER = "output_assets"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

jobs = {}

def process_job(job_id, image_path, output_path):
    try:
        generate_3d_model(image_path, output_path)
        jobs[job_id]["status"] = "done"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

@app.route('/start_job', methods=['POST'])
def start_job():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image provided"}), 400

    job_id = str(uuid.uuid4())
    input_path = f"/tmp/{job_id}.png"
    output_path = os.path.join(OUTPUT_FOLDER, f"{job_id}.glb")
    image.save(input_path)

    jobs[job_id] = {"status": "processing"}
    Thread(target=process_job, args=(job_id, input_path, output_path)).start()

    return jsonify({"job_id": job_id}), 202

@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    if job_id not in jobs:
        return jsonify({"error": "Job ID not found"}), 404
    return jsonify(jobs[job_id]), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
