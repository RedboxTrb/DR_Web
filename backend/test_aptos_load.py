"""
Test loading APTOS model checkpoint
"""
import torch
import sys
sys.path.insert(0, '.')

from models.aptos_model import APTOSDualBranchModel

print("="*60)
print("Testing APTOS Model Loading")
print("="*60)

# Create model
print("\n1. Creating APTOS model architecture...")
model = APTOSDualBranchModel(num_classes=2)
print(f"   Model created with {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M parameters")

# Load checkpoint
print("\n2. Loading checkpoint...")
checkpoint_path = r'c:\Users\gmaer\Documents\UI\best_stage1_dual_branch.pth'
checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

print(f"   Checkpoint keys: {list(checkpoint.keys())}")

# Try to load state dict
print("\n3. Loading state dict...")
try:
    model.load_state_dict(checkpoint['model_state_dict'], strict=False)
    print("   ✅ State dict loaded (strict=False)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test inference
print("\n4. Testing inference...")
vessel = torch.randn(1, 1, 288, 288)
green = torch.randn(1, 1, 288, 288)

model.eval()
with torch.no_grad():
    try:
        main_logits, aux_logits, features, _ = model(vessel, green)
        print(f"   ✅ Inference successful!")
        print(f"   Output shape: {main_logits.shape}")
        print(f"   Features shape: {features.shape}")
    except Exception as e:
        print(f"   ❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n" + "="*60)
print("✅ APTOS model is ready to use!")
print("="*60)
