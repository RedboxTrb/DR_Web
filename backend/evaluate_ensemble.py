"""
Evaluate ensemble model on random samples from VDMDR dataset
"""
import os
import random
import torch
import cv2
import numpy as np
from PIL import Image
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models.model_loader import ModelManager
from services.vessel_inference import predict_vessel_segmentation
from services.cascade_inference import cascade_classify
from services.preprocessing import preprocess_for_vessel, preprocess_for_classification

# Dataset path
DATASET_PATH = r'C:\Users\gmaer\Documents\VDMDR\DREAM_dataset\New'

# Set deterministic mode
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)


def load_random_image_from_folder(folder_path):
    """Load a random image from folder"""
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        return None, None

    random_image = random.choice(images)
    image_path = os.path.join(folder_path, random_image)

    # Load image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image_rgb, random_image


def evaluate_ensemble(num_runs=5, stage1_threshold=0.35):
    """
    Evaluate ensemble on multiple random samples

    Args:
        num_runs: Number of evaluation runs (each run tests 5 images, 1 per grade)
        stage1_threshold: DR probability threshold for Stage 1 (default 0.35)
    """
    print("="*80)
    print("ENSEMBLE EVALUATION ON VDMDR DATASET")
    print(f"Stage 1 Threshold: {stage1_threshold} (P(DR) >= {stage1_threshold} -> DR)")
    print("="*80)

    # Load models
    print("\nLoading models...")
    model_manager = ModelManager()
    model_manager.load_all_models()
    print("Models loaded successfully!\n")

    # Track results
    all_predictions = []
    all_ground_truths = []

    for run in range(num_runs):
        print(f"\n{'='*80}")
        print(f"RUN {run + 1}/{num_runs}")
        print('='*80)

        run_predictions = []
        run_ground_truths = []

        for grade in range(5):  # Grades 0, 1, 2, 3, 4
            folder_path = os.path.join(DATASET_PATH, str(grade))

            if not os.path.exists(folder_path):
                print(f"  Grade {grade}: Folder not found")
                continue

            # Load random image
            image_rgb, image_name = load_random_image_from_folder(folder_path)
            if image_rgb is None:
                print(f"  Grade {grade}: No images in folder")
                continue

            # Vessel segmentation
            vessel_map = predict_vessel_segmentation(
                image_rgb,
                model_manager.vessel_model,
                model_manager.device
            )

            # Classification
            vessel_class_input, green_class_input = preprocess_for_classification(
                image_rgb, vessel_map
            )
            vessel_class_input = vessel_class_input.to(model_manager.device)
            green_class_input = green_class_input.to(model_manager.device)

            result = cascade_classify(
                vessel_class_input,
                green_class_input,
                model_manager,
                stage1_threshold=stage1_threshold
            )

            predicted_grade = result['grade']
            confidence = result['confidence'] * 100

            # Track results
            run_predictions.append(predicted_grade)
            run_ground_truths.append(grade)
            all_predictions.append(predicted_grade)
            all_ground_truths.append(grade)

            # Print result
            status = "OK" if predicted_grade == grade else "XX"
            print(f"  Grade {grade}: Predicted {predicted_grade} ({confidence:.1f}% conf) {status} | Image: {image_name}")

        # Run accuracy
        run_correct = sum(1 for p, g in zip(run_predictions, run_ground_truths) if p == g)
        run_accuracy = (run_correct / len(run_predictions)) * 100 if run_predictions else 0
        print(f"\n  Run {run + 1} Accuracy: {run_correct}/{len(run_predictions)} = {run_accuracy:.1f}%")
        print(f"  Predictions: {run_predictions}")
        print(f"  Ground Truth: {run_ground_truths}")

    # Overall statistics
    print(f"\n{'='*80}")
    print("OVERALL RESULTS")
    print('='*80)

    total_correct = sum(1 for p, g in zip(all_predictions, all_ground_truths) if p == g)
    total_samples = len(all_predictions)
    overall_accuracy = (total_correct / total_samples) * 100 if total_samples > 0 else 0

    print(f"\nTotal Samples: {total_samples}")
    print(f"Correct Predictions: {total_correct}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")

    # Per-grade accuracy
    print(f"\nPer-Grade Accuracy:")
    for grade in range(5):
        grade_predictions = [p for p, g in zip(all_predictions, all_ground_truths) if g == grade]
        grade_correct = [p for p, g in zip(all_predictions, all_ground_truths) if g == grade and p == grade]

        if grade_predictions:
            grade_acc = (len(grade_correct) / len(grade_predictions)) * 100
            print(f"  Grade {grade}: {len(grade_correct)}/{len(grade_predictions)} = {grade_acc:.1f}%")
        else:
            print(f"  Grade {grade}: No samples")

    # Confusion analysis
    print(f"\nCommon Mistakes:")
    for grade in range(5):
        mistakes = [(p, g) for p, g in zip(all_predictions, all_ground_truths) if g == grade and p != grade]
        if mistakes:
            from collections import Counter
            mistake_counts = Counter([p for p, _ in mistakes])
            print(f"  Grade {grade}: Often predicted as {dict(mistake_counts)}")

    print(f"\n{'='*80}")
    print(f"EVALUATION COMPLETE")
    print('='*80)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Evaluate ensemble model')
    parser.add_argument('--runs', type=int, default=5,
                        help='Number of evaluation runs (default: 5)')
    parser.add_argument('--threshold', type=float, default=0.35,
                        help='Stage 1 DR threshold (default: 0.35)')
    args = parser.parse_args()

    evaluate_ensemble(num_runs=args.runs, stage1_threshold=args.threshold)
