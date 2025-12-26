# Retinal Image Analysis System

A web-based application for retinal image testing with automatic vessel segmentation and DR/NODR/Glaucoma classification.

## Features

- Upload single or multiple retinal images
- Automatic vessel segmentation using AttentionUNet
- Cascade classification for DR severity grading (Grade 0-4)
- Professional medical-grade UI
- Real-time results display with vessel map overlays

## Architecture

- **Backend**: Flask + PyTorch
- **Frontend**: React
- **Models**:
  - 1 Vessel Segmentation Model (AttentionUNet, 360MB)
  - 4 Cascade Classification Models (DualStreamConvNeXtModel, 1.66GB each)

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- CUDA-capable GPU (optional, but recommended for faster inference)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

## Running the Application

### Start Backend Server

1. Open a terminal and navigate to the backend directory:
```bash
cd backend
```

2. Activate your virtual environment (if using one)

3. Start the Flask server:
```bash
python app.py
```

The backend will:
- Load all 5 models (this may take 1-2 minutes)
- Start the server on `http://localhost:5000`

### Start Frontend Development Server

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Start the React development server:
```bash
npm start
```

The frontend will:
- Start on `http://localhost:3000`
- Automatically open in your default browser

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Drag and drop retinal images or click to select files
3. Click "Analyze Images" to process
4. View results with:
   - Original image and vessel map side-by-side
   - DR classification (Grade 0-4)
   - Confidence scores
   - Stage-by-stage breakdown

## Model Information

### Vessel Segmentation
- **Model**: AttentionUNet
- **Input**: Green channel (1024x1024)
- **Output**: Binary vessel mask
- **Performance**: Dice score 0.8934

### Cascade Classification
- **Stage 1**: DR vs No-DR
- **Stage 2**: Early DR (1-2) vs Advanced DR (3-4)
- **Stage 3a**: Grade 1 vs Grade 2
- **Stage 3b**: Grade 3 vs Grade 4

## System Requirements

### Minimum
- RAM: 8GB
- Storage: 10GB free space
- CPU: Modern multi-core processor

### Recommended
- RAM: 16GB+
- GPU: NVIDIA GPU with 6GB+ VRAM
- Storage: 20GB free space

## Troubleshooting

### Backend won't start
- Ensure all model files exist at the paths specified in `config.py`
- Check that you have installed all Python dependencies
- Verify CUDA installation if using GPU

### Frontend won't start
- Run `npm install` again to ensure all dependencies are installed
- Check that port 3000 is not in use

### Out of memory errors
- The models require ~7.5GB of RAM when loaded
- Try closing other applications
- Consider using CPU instead of GPU if GPU has insufficient VRAM

## API Endpoints

### GET /api/health
Check server status and model loading state

### POST /api/predict
Upload images for analysis
- **Input**: multipart/form-data with image files
- **Output**: JSON with vessel maps and classification results

## Project Structure

```
UI/
├── backend/
│   ├── app.py                  # Flask application
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   ├── vessel_model.py     # AttentionUNet
│   │   ├── classification_model.py  # DualStreamConvNeXtModel
│   │   └── model_loader.py     # Model loading
│   └── services/
│       ├── preprocessing.py    # Image preprocessing
│       ├── vessel_inference.py # Vessel segmentation
│       └── cascade_inference.py # Classification
└── frontend/
    ├── package.json
    ├── public/
    └── src/
        ├── App.js
        ├── App.css
        └── components/
            ├── ImageUploader.js
            ├── ResultsDisplay.js
            └── LoadingSpinner.js
```

## License

This project uses trained models for medical image analysis. Ensure proper authorization before use in clinical settings.

## Support

For issues or questions, please check:
1. Model file paths in `backend/config.py`
2. Python and Node versions meet requirements
3. All dependencies are correctly installed
