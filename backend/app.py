from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import time
import torch

from models.model_loader import ModelManager
from services.vessel_inference import predict_vessel_segmentation
from services.cascade_inference import cascade_classify
from services.preprocessing import preprocess_for_classification, create_vessel_visualization
from config import MAX_CONTENT_LENGTH

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

model_manager = ModelManager()
model_manager.load_all_models()


def encode_image_to_base64(image_rgb):
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    success, buffer = cv2.imencode('.png', image_bgr)
    if not success:
        raise ValueError("Failed to encode image")
    return base64.b64encode(buffer).decode('utf-8')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "models_loaded": model_manager.models_loaded(),
        "device": str(model_manager.device)
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    start_time = time.time()

    if 'images' not in request.files:
        return jsonify({"success": False, "error": "No images provided"}), 400

    files = request.files.getlist('images')
    if len(files) == 0:
        return jsonify({"success": False, "error": "No images provided"}), 400

    results = []
    for idx, file in enumerate(files):
        try:
            image_bytes = file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image_bgr is None:
                results.append({
                    "image_id": file.filename,
                    "error": "Failed to decode image"
                })
                continue

            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

            vessel_mask = predict_vessel_segmentation(
                image_rgb, model_manager.vessel_model, model_manager.device
            )

            vessel_viz = create_vessel_visualization(image_rgb, vessel_mask)
            vessel_map_b64 = encode_image_to_base64(vessel_viz)

            vessel_mask_rgb = cv2.cvtColor(vessel_mask * 255, cv2.COLOR_GRAY2RGB)
            binary_vessel_b64 = encode_image_to_base64(vessel_mask_rgb)

            original_b64 = encode_image_to_base64(image_rgb)

            vessel_input, green_input = preprocess_for_classification(image_rgb, vessel_mask)
            vessel_input = vessel_input.to(model_manager.device)
            green_input = green_input.to(model_manager.device)

            classification_result = cascade_classify(
                vessel_input, green_input, model_manager, stage1_threshold=0.30
            )

            results.append({
                "image_id": file.filename,
                "original_image": original_b64,
                "vessel_map": vessel_map_b64,
                "binary_vessel_map": binary_vessel_b64,
                "classification": classification_result,
                "processing_time": time.time() - start_time
            })

        except Exception as e:
            results.append({
                "image_id": file.filename,
                "error": str(e)
            })

    total_time = time.time() - start_time

    return jsonify({
        "success": True,
        "results": results,
        "total_processing_time": total_time,
        "num_images": len(results)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
