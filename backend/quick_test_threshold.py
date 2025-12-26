"""Quick test to verify threshold is working"""
import os
import torch
import cv2
import torch.nn.functional as F
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models.model_loader import ModelManager
from services.vessel_inference import predict_vessel_segmentation
from services.preprocessing import preprocess_for_classification

# Set deterministic mode
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

print("Loading models...")
model_manager = ModelManager()
model_manager.load_all_models()
print(f"Models loaded on {model_manager.device}\n")

# Test on 2 Grade 1 images
grade1_folder = r'C:\Users\gmaer\Documents\VDMDR\DREAM_dataset\New\1'
images = [f for f in os.listdir(grade1_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:2]

print("Testing Grade 1 images with different thresholds:")
print("=" * 80)

for img_file in images:
    img_path = os.path.join(grade1_folder, img_file)
    image = cv2.imread(img_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Vessel segmentation
    vessel_map = predict_vessel_segmentation(
        image_rgb, model_manager.vessel_model, model_manager.device
    )

    # Preprocessing
    vessel_input, green_input = preprocess_for_classification(image_rgb, vessel_map)
    vessel_input = vessel_input.to(model_manager.device)
    green_input = green_input.to(model_manager.device)

    # Get Stage 1 probabilities
    with torch.no_grad():
        logits, _, _, _ = model_manager.stage1_cascade(vessel_input, green_input)
        probs = F.softmax(logits, dim=1)
        prob_no_dr = probs[0, 0].item()
        prob_dr = probs[0, 1].item()

    print(f"\nImage: {img_file}")
    print(f"  P(No-DR) = {prob_no_dr:.4f} | P(DR) = {prob_dr:.4f}")

    # Test different thresholds
    for threshold in [0.5, 0.45, 0.40, 0.35, 0.30]:
        predicted_dr = prob_dr >= threshold
        result = "DR" if predicted_dr else "No-DR"
        status = "✓" if predicted_dr else "✗"
        print(f"  Threshold {threshold:.2f}: {result} {status}")

print("\n" + "=" * 80)
print("INSIGHT: If P(DR) is between 0.30-0.50, lowering threshold will help!")
