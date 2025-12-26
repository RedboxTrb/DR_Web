from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import time
from io import BytesIO
from PIL import Image
import torch

from models.model_loader import ModelManager
from services.vessel_inference import predict_vessel_segmentation
from services.cascade_inference import cascade_classify
from services.preprocessing import preprocess_for_classification, create_vessel_visualization
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH

# Set deterministic mode for consistent predictions
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize model manager at startup
print("Initializing model manager...")
model_manager = ModelManager()
model_manager.load_all_models()
print("Backend ready!")


def encode_image_to_base64(image_rgb):
    """Convert RGB image to base64 string"""
    # Convert RGB to BGR for OpenCV
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    # Encode as PNG
    success, buffer = cv2.imencode('.png', image_bgr)
    if not success:
        raise ValueError("Failed to encode image")
    # Convert to base64
    return base64.b64encode(buffer).decode('utf-8')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "models_loaded": model_manager.models_loaded(),
        "device": str(model_manager.device)
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Process uploaded retinal images and return predictions

    Accepts: multipart/form-data with one or more image files
    Returns: JSON with vessel maps and classification results
    """
    start_time = time.time()

    # Check if files were uploaded
    if 'images' not in request.files:
        return jsonify({"success": False, "error": "No images provided"}), 400

    files = request.files.getlist('images')

    if len(files) == 0:
        return jsonify({"success": False, "error": "No images provided"}), 400

    results = []

    for idx, file in enumerate(files):
        try:
            # Read image from uploaded file
            image_bytes = file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image_bgr is None:
                results.append({
                    "image_id": file.filename,
                    "error": "Failed to decode image"
                })
                continue

            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

            # Vessel segmentation
            vessel_mask = predict_vessel_segmentation(
                image_rgb, model_manager.vessel_model, model_manager.device
            )

            # Create vessel visualization
            vessel_viz = create_vessel_visualization(image_rgb, vessel_mask)
            vessel_map_b64 = encode_image_to_base64(vessel_viz)

            # Also encode original image for display
            original_b64 = encode_image_to_base64(image_rgb)

            # Preprocess for classification
            vessel_input, green_input = preprocess_for_classification(
                image_rgb, vessel_mask
            )
            vessel_input = vessel_input.to(model_manager.device)
            green_input = green_input.to(model_manager.device)

            # Cascade classification (threshold 0.30 for balanced accuracy)
            classification_result = cascade_classify(
                vessel_input, green_input, model_manager, stage1_threshold=0.30
            )

            results.append({
                "image_id": file.filename,
                "original_image": original_b64,
                "vessel_map": vessel_map_b64,
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
