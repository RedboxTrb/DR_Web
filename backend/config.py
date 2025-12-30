import os
import torch

# Device configuration - force CPU for Render deployment
DEVICE = os.getenv('MODEL_DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')

# Base directory for models
BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Model file paths - support both local and production
# In production, models should be in backend/models/
MODEL_PATHS = {
    'vessel': os.getenv('VESSEL_MODEL_PATH',
                       os.path.join(MODELS_DIR, 'vessel_best_model_green.pth')),
    'stage1_cascade': os.getenv('STAGE1_CASCADE_PATH',
                                os.path.join(MODELS_DIR, '1.pth')),
    'stage2': os.getenv('STAGE2_PATH',
                       os.path.join(MODELS_DIR, '2.pth')),
    'stage3a': os.getenv('STAGE3A_PATH',
                        os.path.join(MODELS_DIR, '3a.pth')),
    'stage3b': os.getenv('STAGE3B_PATH',
                        os.path.join(MODELS_DIR, '3b.pth'))
}

# Fallback to local paths if in development
if os.path.exists(r'c:\Users\gmaer\Documents\VDMDR'):
    MODEL_PATHS = {
        'vessel': os.path.join(MODELS_DIR, 'vessel_best_model_green.pth'),
        'stage1_cascade': os.path.join(MODELS_DIR, '1.pth'),
        'stage2': os.path.join(MODELS_DIR, '2.pth'),
        'stage3a': os.path.join(MODELS_DIR, '3a.pth'),
        'stage3b': os.path.join(MODELS_DIR, '3b.pth')
    }

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
