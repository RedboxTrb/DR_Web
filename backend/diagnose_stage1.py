"""
Diagnose Stage 1 model decision boundary
Shows probability distributions to understand why Grade 1 is failing
"""
import os
import random
import torch
import cv2
import numpy as np
import torch.nn.functional as F
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models.model_loader import ModelManager
from services.vessel_inference import predict_vessel_segmentation
from services.preprocessing import preprocess_for_classification

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


def diagnose_stage1(num_samples_per_grade=20):
    """
    Diagnose Stage 1 model predictions with probability analysis

    Focus on Grade 1 images to understand why they're being predicted as No-DR
    """
    print("="*80)
    print("STAGE 1 DIAGNOSTIC ANALYSIS")
    print("="*80)

    # Load models
    print("\nLoading models...")
    model_manager = ModelManager()
    model_manager.load_all_models()
    print("Models loaded successfully!\n")

    # Ensure eval mode
    model_manager.stage1_cascade.eval()

    # Track results per grade
    grade_results = {grade: [] for grade in range(5)}

    print(f"\nTesting {num_samples_per_grade} samples per grade...\n")

    for grade in range(5):
        folder_path = os.path.join(DATASET_PATH, str(grade))

        if not os.path.exists(folder_path):
            print(f"Grade {grade}: Folder not found")
            continue

        print(f"\n{'='*80}")
        print(f"GRADE {grade} ANALYSIS")
        print('='*80)

        for i in range(num_samples_per_grade):
            # Load random image
            image_rgb, image_name = load_random_image_from_folder(folder_path)
            if image_rgb is None:
                continue

            # Vessel segmentation
            vessel_map = predict_vessel_segmentation(
                image_rgb,
                model_manager.vessel_model,
                model_manager.device
            )

            # Classification preprocessing
            vessel_class_input, green_class_input = preprocess_for_classification(
                image_rgb, vessel_map
            )
            vessel_class_input = vessel_class_input.to(model_manager.device)
            green_class_input = green_class_input.to(model_manager.device)

            # Stage 1 prediction (Cascade model only)
            with torch.no_grad():
                cascade_logits, _, _, _ = model_manager.stage1_cascade(vessel_class_input, green_class_input)
                cascade_probs = F.softmax(cascade_logits, dim=1)

                prob_no_dr = cascade_probs[0, 0].item()
                prob_dr = cascade_probs[0, 1].item()
                pred = torch.argmax(cascade_probs, dim=1).item()

            # Store result
            result = {
                'image': image_name,
                'true_grade': grade,
                'pred': pred,
                'prob_no_dr': prob_no_dr,
                'prob_dr': prob_dr,
                'correct': (pred == 0 and grade == 0) or (pred == 1 and grade > 0)
            }
            grade_results[grade].append(result)

            # Print detailed info for Grade 1 (the problematic class)
            if grade == 1:
                status = "✓" if result['correct'] else "✗"
                pred_label = "No-DR" if pred == 0 else "DR"
                print(f"  Sample {i+1}: Pred={pred_label} | P(No-DR)={prob_no_dr:.3f}, P(DR)={prob_dr:.3f} {status}")

    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print('='*80)

    for grade in range(5):
        results = grade_results[grade]
        if not results:
            continue

        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = (correct / total) * 100 if total > 0 else 0

        avg_prob_no_dr = np.mean([r['prob_no_dr'] for r in results])
        avg_prob_dr = np.mean([r['prob_dr'] for r in results])

        print(f"\nGrade {grade}:")
        print(f"  Accuracy: {correct}/{total} = {accuracy:.1f}%")
        print(f"  Average P(No-DR): {avg_prob_no_dr:.3f}")
        print(f"  Average P(DR): {avg_prob_dr:.3f}")

        # For DR grades (1-4), show how many were predicted as No-DR
        if grade > 0:
            false_negatives = sum(1 for r in results if r['pred'] == 0)
            if false_negatives > 0:
                avg_prob_no_dr_fn = np.mean([r['prob_no_dr'] for r in results if r['pred'] == 0])
                avg_prob_dr_fn = np.mean([r['prob_dr'] for r in results if r['pred'] == 0])
                print(f"  ⚠️  False Negatives: {false_negatives}/{total}")
                print(f"      When predicting No-DR incorrectly:")
                print(f"        Avg P(No-DR): {avg_prob_no_dr_fn:.3f}")
                print(f"        Avg P(DR): {avg_prob_dr_fn:.3f}")

    # Critical analysis for Grade 1
    print(f"\n{'='*80}")
    print("CRITICAL: GRADE 1 ANALYSIS")
    print('='*80)

    grade1_results = grade_results[1]
    if grade1_results:
        false_negatives = [r for r in grade1_results if r['pred'] == 0]

        if false_negatives:
            print(f"\nGrade 1 images incorrectly predicted as No-DR: {len(false_negatives)}/{len(grade1_results)}")
            print(f"\nProbability Distribution of False Negatives:")

            # Bins for analysis
            confident_wrong = [r for r in false_negatives if r['prob_no_dr'] > 0.7]
            moderate_wrong = [r for r in false_negatives if 0.5 < r['prob_no_dr'] <= 0.7]
            barely_wrong = [r for r in false_negatives if 0.5 <= r['prob_no_dr'] <= 0.55]

            print(f"  Confident No-DR (P > 0.7): {len(confident_wrong)} cases")
            if confident_wrong:
                avg = np.mean([r['prob_no_dr'] for r in confident_wrong])
                print(f"    Average P(No-DR): {avg:.3f}")

            print(f"  Moderate No-DR (0.5 < P ≤ 0.7): {len(moderate_wrong)} cases")
            if moderate_wrong:
                avg = np.mean([r['prob_no_dr'] for r in moderate_wrong])
                print(f"    Average P(No-DR): {avg:.3f}")

            print(f"  Barely No-DR (0.5 ≤ P ≤ 0.55): {len(barely_wrong)} cases")
            if barely_wrong:
                avg = np.mean([r['prob_no_dr'] for r in barely_wrong])
                print(f"    Average P(No-DR): {avg:.3f}")
                print(f"\n  💡 INSIGHT: {len(barely_wrong)} cases are close to decision boundary!")
                print(f"     Lowering threshold from 0.5 to ~0.45 could recover these cases.")

    print(f"\n{'='*80}")
    print("DIAGNOSTIC COMPLETE")
    print('='*80)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Diagnose Stage 1 model')
    parser.add_argument('--samples', type=int, default=20, help='Samples per grade (default: 20)')
    args = parser.parse_args()

    diagnose_stage1(num_samples_per_grade=args.samples)
