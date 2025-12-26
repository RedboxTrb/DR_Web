import torch
from models.vessel_model import AttentionUNet
from models.classification_model import DualStreamConvNeXtModel
from config import MODEL_PATHS


class ModelManager:
    """
    Optimized model manager with lazy loading and FP16 support
    - Loads Vessel + Stage 1 at startup (always needed)
    - Lazy loads Stage 2/3 models only when DR is detected
    - Saves ~5GB VRAM for No-DR cases (most images)
    - FP16 mixed precision reduces VRAM by ~50% and speeds up inference by ~2x
    """
    def __init__(self, use_fp16=False):
        self.vessel_model = None
        self.stage1_cascade = None  # CASCADE binary (DR vs No-DR)
        self.stage2_model = None  # Early vs Advanced DR (lazy loaded)
        self.stage3a_model = None  # Grade 1 vs 2 (lazy loaded)
        self.stage3b_model = None  # Grade 3 vs 4 (lazy loaded)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_fp16 = use_fp16 and torch.cuda.is_available()  # FP16 only works on CUDA
        self.dtype = torch.float16 if self.use_fp16 else torch.float32

    def load_all_models(self):
        """Load core models at startup (Vessel + Stage 1 only)"""
        print(f"Using device: {self.device}")
        if self.use_fp16:
            print("Using FP16 mixed precision (faster inference, lower VRAM)")
        print("Loading models...")

        # Load vessel segmentation model
        print("Loading vessel segmentation model...")
        self.vessel_model = AttentionUNet(in_channels=1, out_channels=1).to(self.device)
        checkpoint = torch.load(MODEL_PATHS['vessel'], map_location=self.device, weights_only=False)
        self.vessel_model.load_state_dict(checkpoint['model_state_dict'])
        if self.use_fp16:
            self.vessel_model = self.vessel_model.half()
        self.vessel_model.eval()
        print("  Vessel model loaded successfully")

        # Load Stage 1 CASCADE model (always needed for initial DR detection)
        print("Loading Stage 1 Cascade model (VDMDR-trained, DR vs No-DR)...")
        self.stage1_cascade = DualStreamConvNeXtModel(num_classes=2).to(self.device)
        checkpoint = torch.load(MODEL_PATHS['stage1_cascade'], map_location=self.device, weights_only=False)
        self.stage1_cascade.load_state_dict(checkpoint['model_state_dict'])
        if self.use_fp16:
            self.stage1_cascade = self.stage1_cascade.half()
        self.stage1_cascade.eval()
        print("  Stage 1 Cascade model loaded successfully")

        print("All models loaded successfully!")
        print("NOTE: Stage 2/3 models will be lazy-loaded when DR is detected")

    def load_stage2(self):
        """Lazy load Stage 2 model (Early vs Advanced DR)"""
        if self.stage2_model is None:
            print("Lazy loading Stage 2 model (Early vs Advanced DR)...")
            self.stage2_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage2'], map_location=self.device, weights_only=False)
            self.stage2_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage2_model = self.stage2_model.half()
            self.stage2_model.eval()
            print("  Stage 2 model loaded successfully")

    def load_stage3a(self):
        """Lazy load Stage 3a model (Grade 1 vs 2)"""
        if self.stage3a_model is None:
            print("Lazy loading Stage 3a model (Grade 1 vs 2)...")
            self.stage3a_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage3a'], map_location=self.device, weights_only=False)
            self.stage3a_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage3a_model = self.stage3a_model.half()
            self.stage3a_model.eval()
            print("  Stage 3a model loaded successfully")

    def load_stage3b(self):
        """Lazy load Stage 3b model (Grade 3 vs 4)"""
        if self.stage3b_model is None:
            print("Lazy loading Stage 3b model (Grade 3 vs 4)...")
            self.stage3b_model = DualStreamConvNeXtModel(num_classes=2).to(self.device)
            checkpoint = torch.load(MODEL_PATHS['stage3b'], map_location=self.device, weights_only=False)
            self.stage3b_model.load_state_dict(checkpoint['model_state_dict'])
            if self.use_fp16:
                self.stage3b_model = self.stage3b_model.half()
            self.stage3b_model.eval()
            print("  Stage 3b model loaded successfully")

    def models_loaded(self):
        """Check if core models are loaded (Vessel + Stage 1)"""
        return all([
            self.vessel_model is not None,
            self.stage1_cascade is not None
        ])
