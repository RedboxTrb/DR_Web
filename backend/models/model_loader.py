import torch
from models.vessel_model import AttentionUNet
from models.classification_model import DualStreamConvNeXtModel
from config import MODEL_PATHS


class ModelManager:
    def __init__(self, use_fp16=False):
        self.vessel_model = None
        self.stage1_cascade = None
        self.stage2_model = None
        self.stage3a_model = None
        self.stage3b_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_fp16 = use_fp16 and torch.cuda.is_available()
        self.dtype = torch.float16 if self.use_fp16 else torch.float32

    def load_all_models(self):
        self.vessel_model = AttentionUNet(in_channels=1, out_channels=1).to(self.device)
        checkpoint = torch.load(MODEL_PATHS['vessel'], map_location=self.device, weights_only=False)
        self.vessel_model.load_state_dict(checkpoint['model_state_dict'])
        if self.use_fp16:
            self.vessel_model = self.vessel_model.half()
        self.vessel_model.eval()

        self.stage1_cascade = DualStreamConvNeXtModel(num_classes=2).to(self.device)
        checkpoint = torch.load(MODEL_PATHS['stage1_cascade'], map_location=self.device, weights_only=False)
        self.stage1_cascade.load_state_dict(checkpoint['model_state_dict'])
        if self.use_fp16:
            self.stage1_cascade = self.stage1_cascade.half()
        self.stage1_cascade.eval()

    def load_stage2(self):
        if self.stage2_model is None:
            self.stage2_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage2'], map_location=self.device, weights_only=False)
            self.stage2_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage2_model = self.stage2_model.half()
            self.stage2_model.eval()

    def load_stage3a(self):
        if self.stage3a_model is None:
            self.stage3a_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage3a'], map_location=self.device, weights_only=False)
            self.stage3a_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage3a_model = self.stage3a_model.half()
            self.stage3a_model.eval()

    def load_stage3b(self):
        if self.stage3b_model is None:
            self.stage3b_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage3b'], map_location=self.device, weights_only=False)
            self.stage3b_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage3b_model = self.stage3b_model.half()
            self.stage3b_model.eval()

    def models_loaded(self):
        return all([
            self.vessel_model is not None,
            self.stage1_cascade is not None
        ])
