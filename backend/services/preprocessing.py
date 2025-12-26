import cv2
import numpy as np
import torch


def preprocess_for_vessel(image_rgb):
    """
    Preprocess image for vessel segmentation with AttentionUNet

    Args:
        image_rgb: numpy array of shape (H, W, 3) in RGB format

    Returns:
        tensor: preprocessed tensor of shape (1, 1, 1024, 1024)
        original_size: tuple of (original_height, original_width)
    """
    original_h, original_w = image_rgb.shape[:2]

    # Resize to 1024x1024 if needed
    if original_h != 1024 or original_w != 1024:
        rgb_resized = cv2.resize(image_rgb, (1024, 1024))
    else:
        rgb_resized = image_rgb.copy()

    # Extract green channel
    green = rgb_resized[:, :, 1].astype(np.float32) / 255.0

    # Convert to tensor with shape (1, 1, 1024, 1024)
    input_tensor = torch.from_numpy(green).unsqueeze(0).unsqueeze(0).float()

    return input_tensor, (original_h, original_w)


def preprocess_for_classification(image_rgb, vessel_mask):
    """
    Preprocess image and vessel mask for cascade classification

    Args:
        image_rgb: numpy array of shape (H, W, 3) in RGB format
        vessel_mask: numpy array of shape (H, W) with values 0 or 1

    Returns:
        vessel_tensor: preprocessed vessel tensor of shape (1, 1, 288, 288)
        green_tensor: preprocessed green tensor of shape (1, 1, 288, 288)
    """
    # Resize vessel mask to 288x288
    vessel_resized = cv2.resize(vessel_mask, (288, 288), interpolation=cv2.INTER_NEAREST)
    vessel_resized = vessel_resized.astype(np.float32)

    # Ensure vessel mask is in [0, 255] range
    if vessel_resized.max() <= 1.0:
        vessel_resized = vessel_resized * 255.0

    # Normalize vessel channel to [-1, 1]
    vessel_normalized = (vessel_resized / 255.0 - 0.5) / 0.5

    # Convert to tensor
    vessel_tensor = torch.from_numpy(vessel_normalized).unsqueeze(0).unsqueeze(0).float()

    # Extract green channel and resize to 288x288
    green = image_rgb[:, :, 1].astype(np.float32)
    green_resized = cv2.resize(green, (288, 288))

    # Normalize green channel to [-1, 1]
    green_normalized = (green_resized / 255.0 - 0.5) / 0.5

    # Convert to tensor
    green_tensor = torch.from_numpy(green_normalized).unsqueeze(0).unsqueeze(0).float()

    return vessel_tensor, green_tensor


def create_vessel_visualization(original_rgb, vessel_mask):
    """
    Create visualization of vessel segmentation overlaid on original image

    Args:
        original_rgb: numpy array of shape (H, W, 3) in RGB format
        vessel_mask: numpy array of shape (H, W) with values 0 or 1

    Returns:
        blended: numpy array of shape (H, W, 3) with vessel overlay
    """
    # Create overlay with red vessels
    overlay = original_rgb.copy()
    overlay[vessel_mask > 0, 0] = 255  # Red channel

    # Blend with original for better visibility
    alpha = 0.4
    blended = cv2.addWeighted(original_rgb, 1 - alpha, overlay, alpha, 0)

    return blended
