"""
Verify which Stage 1 model is being used and show probabilities
"""
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

# Test on 1 Grade 1 image
grade1_folder = r'C:\Users\gmaer\Documents\VDMDR\DREAM_dataset\New\1'
images = [f for f in os.listdir(grade1_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:1]

img_file = images[0]
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

print("="*80)
print(f"Testing Grade 1 image: {img_file}")
print("="*80)

# Test CASCADE model
with torch.no_grad():
    cascade_logits, _, _, _ = model_manager.stage1_cascade(vessel_input, green_input)
    cascade_probs = F.softmax(cascade_logits, dim=1)
    cascade_no_dr = cascade_probs[0, 0].item()
    cascade_dr = cascade_probs[0, 1].item()

print("\nCASCADE Model:")
print(f"  P(No-DR) = {cascade_no_dr:.4f}")
print(f"  P(DR) = {cascade_dr:.4f}")
print(f"  Decision with threshold 0.30: {'DR' if cascade_dr >= 0.30 else 'No-DR'}")
print(f"  Decision with threshold 0.35: {'DR' if cascade_dr >= 0.35 else 'No-DR'}")

# Test APTOS model
with torch.no_grad():
    aptos_logits, _, _, _ = model_manager.stage1_aptos(vessel_input, green_input)
    aptos_probs = F.softmax(aptos_logits, dim=1)
    aptos_no_dr = aptos_probs[0, 0].item()
    aptos_dr = aptos_probs[0, 1].item()

print("\nAPTOS Model:")
print(f"  P(No-DR) = {aptos_no_dr:.4f}")
print(f"  P(DR) = {aptos_dr:.4f}")
print(f"  Decision with threshold 0.30: {'DR' if aptos_dr >= 0.30 else 'No-DR'}")
print(f"  Decision with threshold 0.35: {'DR' if aptos_dr >= 0.35 else 'No-DR'}")

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)

if cascade_dr >= 0.30:
    print("\nCASCADE model SHOULD detect this as DR with threshold 0.30")
else:
    print(f"\nCASCADE P(DR) = {cascade_dr:.4f} is too low for threshold 0.30")
    print(f"  Would need threshold <= {cascade_dr:.4f} to catch this case")

if aptos_dr >= 0.30:
    print("APTOS model SHOULD detect this as DR with threshold 0.30")
else:
    print(f"\nAPTOS P(DR) = {aptos_dr:.4f} is too low for threshold 0.30")
    print(f"  Would need threshold <= {aptos_dr:.4f} to catch this case")
