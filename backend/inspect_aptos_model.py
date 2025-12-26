"""
Inspect APTOS model architecture
"""
import torch

checkpoint = torch.load(r'c:\Users\gmaer\Documents\UI\best_stage1_dual_branch.pth',
                        map_location='cpu', weights_only=False)

print("="*60)
print("APTOS Model Architecture Inspection")
print("="*60)

# Get state dict keys
state_dict = checkpoint['model_state_dict']
keys = list(state_dict.keys())

print(f"\nTotal parameters: {len(keys)}")
print("\nFirst 30 keys:")
for i, key in enumerate(keys[:30]):
    shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
    print(f"{i+1}. {key}: {shape}")

print("\n" + "="*60)
print("Architecture Analysis")
print("="*60)

# Identify backbone type
if any('conv_stem' in k for k in keys):
    print("✓ Uses EfficientNet backbone (has 'conv_stem')")
elif any('stem.0.weight' in k for k in keys):
    print("✓ Uses ConvNeXt backbone (has 'stem.0.weight')")
else:
    print("? Unknown backbone type")

# Check for CBAM
if any('cbam' in k for k in keys):
    print("✓ Uses CBAM attention modules")

# Check for specific components
vessel_keys = [k for k in keys if 'vessel' in k]
green_keys = [k for k in keys if 'green' in k]
fusion_keys = [k for k in keys if 'fusion' in k]
classifier_keys = [k for k in keys if 'classifier' in k]

print(f"\nVessel backbone keys: {len(vessel_keys)}")
print(f"Green backbone keys: {len(green_keys)}")
print(f"Fusion layer keys: {len(fusion_keys)}")
print(f"Classifier keys: {len(classifier_keys)}")

# Show unique layer types
unique_layers = set()
for key in keys:
    parts = key.split('.')
    if len(parts) > 1:
        unique_layers.add(parts[0] + '.' + parts[1] if len(parts) > 2 else parts[0])

print(f"\nUnique top-level modules:")
for layer in sorted(unique_layers)[:20]:
    print(f"  - {layer}")

print("\n" + "="*60)
print("Conclusion")
print("="*60)
print("The APTOS model uses a DIFFERENT architecture than cascade models!")
print("APTOS: EfficientNet + CBAM")
print("Cascade: ConvNeXt Large")
print("\nWe need the APTOS model's architecture definition to use it.")
