import torch

# Load checkpoint
checkpoint = torch.load(r'c:\Users\gmaer\Documents\VDMDR\VDMDR_dataset\models\Best\1.pth',
                       map_location='cpu', weights_only=False)

model_dict = checkpoint['model_state_dict']

# Get fusion layers
fusion_keys = sorted([k for k in model_dict.keys() if k.startswith('fusion.')])
classifier_keys = sorted([k for k in model_dict.keys() if k.startswith('classifier.') and 'aux' not in k])

print("=== FUSION LAYERS ===")
for key in fusion_keys:
    if 'weight' in key or 'bias' in key:
        print(f"{key}: {model_dict[key].shape}")

print("\n=== CLASSIFIER LAYERS ===")
for key in classifier_keys:
    if 'weight' in key or 'bias' in key:
        print(f"{key}: {model_dict[key].shape}")

print("\n=== ARCHITECTURE INFERENCE ===")
fusion_0_in = model_dict['fusion.0.weight'].shape[1]
fusion_0_out = model_dict['fusion.0.weight'].shape[0]
print(f"embed_dim = {fusion_0_in // 2} (because fusion.0 input is {fusion_0_in} = embed_dim * 2)")
print(f"fusion.0 outputs: {fusion_0_out}")
