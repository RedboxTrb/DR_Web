import cv2
import numpy as np
import torch
from services.preprocessing import preprocess_for_vessel


def predict_vessel_segmentation(image_rgb, model, device):
    """
    Predict vessel segmentation for a retinal image

    Args:
        image_rgb: numpy array of shape (H, W, 3) in RGB format
        model: AttentionUNet model
        device: torch device (cuda or cpu)

    Returns:
        binary_mask: numpy array of shape (H, W) with values 0 or 1
    """
    original_h, original_w = image_rgb.shape[:2]

    # Preprocess image
    input_tensor, _ = preprocess_for_vessel(image_rgb)
    input_tensor = input_tensor.to(device)

    # Convert to FP16 if model is using half precision
    if next(model.parameters()).dtype == torch.float16:
        input_tensor = input_tensor.half()

    # Predict
    with torch.no_grad():
        pred_logits = model(input_tensor)
        pred_prob = torch.sigmoid(pred_logits)

    # Convert to numpy and threshold
    prob_map = pred_prob.cpu().numpy().squeeze()
    binary_mask = (prob_map > 0.5).astype(np.uint8)

    # Resize back to original size if needed
    if original_h != 1024 or original_w != 1024:
        binary_mask = cv2.resize(binary_mask, (original_w, original_h),
                                 interpolation=cv2.INTER_NEAREST)

    return binary_mask
