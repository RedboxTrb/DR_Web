"""Check classifier structure in checkpoint"""
import torch

checkpoint = torch.load(r'c:\Users\gmaer\Documents\UI\best_stage1_dual_branch.pth',
                        map_location='cpu', weights_only=False)

state_dict = checkpoint['model_state_dict']

# Get all classifier keys
classifier_keys = [k for k in state_dict.keys() if 'classifier' in k]

print("Classifier layers:")
for key in sorted(classifier_keys):
    shape = state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'
    print(f"  {key}: {shape}")
