"""
Quick test script to verify ensemble Stage 1 is working correctly
Run this BEFORE starting the Flask app to verify model loading
"""

import torch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models.model_loader import ModelManager

def test_ensemble():
    print("="*60)
    print("Testing Ensemble Stage 1 Implementation")
    print("="*60)

    # Initialize model manager
    print("\n1. Initializing ModelManager...")
    manager = ModelManager()

    # Load all models
    print("\n2. Loading all models (this may take 1-2 minutes)...")
    try:
        manager.load_all_models()
    except Exception as e:
        print(f"\n❌ ERROR loading models: {e}")
        return False

    # Verify models loaded
    print("\n3. Verifying models...")
    if not manager.models_loaded():
        print("❌ Not all models loaded!")
        return False

    print("✅ All models loaded successfully!")

    # Check ensemble models
    print("\n4. Checking Stage 1 ensemble models...")
    if manager.stage1_aptos is None:
        print("❌ APTOS model not loaded!")
        return False
    print("✅ APTOS model loaded")

    if manager.stage1_cascade is None:
        print("❌ Cascade model not loaded!")
        return False
    print("✅ Cascade model loaded")

    # Test inference with dummy data
    print("\n5. Testing ensemble inference with dummy data...")
    try:
        # Create dummy inputs (batch_size=1, channels=1, height=288, width=288)
        dummy_vessel = torch.randn(1, 1, 288, 288).to(manager.device)
        dummy_green = torch.randn(1, 1, 288, 288).to(manager.device)

        with torch.no_grad():
            # Test APTOS model
            aptos_out, _, _, _ = manager.stage1_aptos(dummy_vessel, dummy_green)
            print(f"  APTOS output shape: {aptos_out.shape}")

            # Test Cascade model
            cascade_out, _, _, _ = manager.stage1_cascade(dummy_vessel, dummy_green)
            print(f"  Cascade output shape: {cascade_out.shape}")

            # Test ensemble (weighted average)
            import torch.nn.functional as F
            aptos_probs = F.softmax(aptos_out, dim=1)
            cascade_probs = F.softmax(cascade_out, dim=1)
            ensemble_probs = 0.7 * aptos_probs + 0.3 * cascade_probs

            print(f"  Ensemble probs: {ensemble_probs.cpu().numpy()}")
            print(f"  Prediction: {torch.argmax(ensemble_probs, dim=1).item()}")

        print("✅ Ensemble inference successful!")

    except Exception as e:
        print(f"❌ ERROR during inference: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print("\n" + "="*60)
    print("ENSEMBLE TEST SUMMARY")
    print("="*60)
    print("✅ All models loaded successfully")
    print("✅ Stage 1 APTOS model working")
    print("✅ Stage 1 Cascade model working")
    print("✅ Ensemble inference working")
    print(f"✅ Device: {manager.device}")
    print("\n🎉 Ensemble implementation is READY!")
    print("\nYou can now start the Flask app with: python app.py")
    print("="*60)

    return True

if __name__ == "__main__":
    success = test_ensemble()
    sys.exit(0 if success else 1)
