import os

# Model file paths
MODEL_PATHS = {
    'vessel': r'c:\Users\gmaer\Documents\VDMDR\Vessel_dataset\vessel_maps\raw_green\models\best_model.pth',
    'stage1_aptos': r'c:\Users\gmaer\Documents\UI\best_stage1_dual_branch.pth',  # 99.18% APTOS binary
    'stage1_cascade': r'c:\Users\gmaer\Documents\VDMDR\VDMDR_dataset\models\Best\1.pth',  # Cascade binary
    'stage2': r'c:\Users\gmaer\Documents\VDMDR\VDMDR_dataset\models\Best\2.pth',
    'stage3a': r'c:\Users\gmaer\Documents\VDMDR\VDMDR_dataset\models\Best\3a.pth',
    'stage3b': r'c:\Users\gmaer\Documents\VDMDR\VDMDR_dataset\models\Best\3b.pth'
}

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
