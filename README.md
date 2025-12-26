# Retinal DR Detection System

An AI-powered web application for automated detection and grading of diabetic retinopathy in retinal fundus images.

## Features

- **Automated Vessel Segmentation** - Deep learning vessel extraction using AttentionUNet
- **4-Stage Cascade Classification** - Hierarchical DR grading (Grade 0-4)
- **Medical-Grade UI** - Professional results display with clinical recommendations
- **Optimized Performance** - Lazy loading reduces VRAM usage by 69% for most cases
- **High Accuracy** - 88% overall accuracy, 80% Grade 1 detection

## Screenshots

### Upload Interface
Drag-and-drop multiple retinal images for batch processing

### Results Display
- Side-by-side original image and vessel map
- Color-coded grade classification (0-4)
- Confidence scores and processing time
- AI decision path transparency (Stage 1/2/3 breakdown)
- Clinical recommendations per grade

## System Architecture

### Backend (Flask + PyTorch)
- **Vessel Segmentation**: AttentionUNet (360MB)
- **Stage 1**: DR vs No-DR detection (threshold-optimized)
- **Stage 2**: Early (1-2) vs Advanced (3-4) DR classification
- **Stage 3a**: Grade 1 vs 2 classification
- **Stage 3b**: Grade 3 vs 4 classification

### Frontend (React + TypeScript + Vite)
- Modern, responsive UI built with Tailwind CSS
- Real-time progress indicators
- Detailed results with medical disclaimers

### Performance Optimizations
- **Lazy Loading**: Models load on-demand (saves ~5GB VRAM for No-DR cases)
- **Threshold Optimization**: Improved Grade 1 sensitivity (10% → 80%)
- **FP16 Support**: Optional half-precision mode (not recommended, accuracy drops)

## Installation

### Prerequisites

- **Python** 3.8+ with conda/venv
- **Node.js** 18+
- **GPU**: NVIDIA GPU with 3GB+ VRAM (recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: Model files stored separately (see config.py)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create conda environment (recommended):
```bash
conda create -n torch python=3.10
conda activate torch
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure model paths in `config.py`:
```python
MODEL_PATHS = {
    'vessel': r'path/to/vessel_model.pth',
    'stage1_cascade': r'path/to/stage1.pth',
    'stage2': r'path/to/stage2.pth',
    'stage3a': r'path/to/stage3a.pth',
    'stage3b': r'path/to/stage3b.pth'
}
```

### Frontend Setup

1. Navigate to Website directory:
```bash
cd Website
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend

```bash
cd backend
conda activate torch
python app.py
```

Backend will start on `http://localhost:5000`

**Initial load time**: 10-15 seconds (loads Vessel + Stage 1 models only)

### Start Frontend

```bash
cd Website
npm run dev
```

Frontend will start on `http://localhost:5173` (Vite default)

## Usage

1. Open `http://localhost:5173` in your browser
2. Upload one or multiple retinal fundus images (PNG, JPG, JPEG)
3. Click "Analyze X Images"
4. View results with:
   - Original image and vessel segmentation
   - Grade classification (0-4) with descriptions
   - Confidence scores
   - Risk level and clinical recommendations
   - AI decision path (Stage 1/2/3 breakdown)
   - Medical disclaimer

## Model Performance

### Overall Accuracy: 88%

| Grade | Accuracy | Description |
|-------|----------|-------------|
| Grade 0 | 100% | No DR |
| Grade 1 | 80% | Mild DR |
| Grade 2 | 80% | Moderate DR |
| Grade 3 | 80% | Severe DR |
| Grade 4 | 100% | Proliferative DR |

**Threshold**: 0.30 (optimized for Grade 1 sensitivity)

### VRAM Usage

| Scenario | VRAM | Models Loaded |
|----------|------|---------------|
| Startup | 2.5GB | Vessel + Stage 1 |
| No-DR image | 2.5GB | Same (70% of cases) |
| DR image | 7.5GB | All models (lazy loaded) |

## Technical Details

### Cascade Classification Flow

```
Input Image
    ↓
Vessel Segmentation (AttentionUNet)
    ↓
Preprocessing (Vessel + Green channel)
    ↓
Stage 1: DR vs No-DR (threshold 0.30)
    ├─ No-DR → Grade 0 (STOP)
    └─ DR → Continue
        ↓
    Stage 2: Early vs Advanced
        ├─ Early (1-2) → Stage 3a
        │   ├─ Grade 1
        │   └─ Grade 2
        └─ Advanced (3-4) → Stage 3b
            ├─ Grade 3
            └─ Grade 4
```

### API Endpoints

#### `GET /api/health`
Check server status and model loading state

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "device": "cuda"
}
```

#### `POST /api/predict`
Upload retinal images for analysis

**Request:** `multipart/form-data` with image files

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "image_id": "image.png",
      "original_image": "base64...",
      "vessel_map": "base64...",
      "classification": {
        "grade": 0,
        "severity": "No DR",
        "confidence": 0.98,
        "has_dr": false,
        "stage1_result": "No DR (P(DR)=0.020)",
        "stage2_result": null,
        "stage3_result": null
      },
      "processing_time": 1.23
    }
  ],
  "total_processing_time": 2.45,
  "num_images": 2
}
```

## Project Structure

```
DR_Web/
├── backend/
│   ├── app.py                      # Flask server
│   ├── config.py                   # Model paths & config
│   ├── requirements.txt            # Python dependencies
│   ├── models/
│   │   ├── vessel_model.py         # AttentionUNet
│   │   ├── classification_model.py # DualStreamConvNeXt
│   │   └── model_loader.py         # Lazy loading manager
│   └── services/
│       ├── preprocessing.py        # Image preprocessing
│       ├── vessel_inference.py     # Vessel segmentation
│       └── cascade_inference.py    # Cascade classification
├── Website/
│   ├── src/
│   │   ├── App.tsx                 # Main app component
│   │   ├── components/
│   │   │   ├── Hero.tsx            # Landing page hero
│   │   │   ├── Features.tsx        # Feature showcase
│   │   │   ├── UploadSection.tsx   # File upload UI
│   │   │   ├── ResultsDisplay.tsx  # Results visualization
│   │   │   └── ...
│   │   └── styles/
│   ├── package.json
│   └── vite.config.ts
├── OPTIMIZATION_SUMMARY.md         # Performance optimizations
└── README.md                       # This file
```

## Troubleshooting

### Models not loading
- Check paths in `backend/config.py` point to actual .pth files
- Ensure model files exist and are not corrupted
- Verify you have read permissions

### Out of memory (OOM)
- Reduce batch size (upload fewer images at once)
- Close other GPU-intensive applications
- Use CPU mode: Set `CUDA_VISIBLE_DEVICES=""` before running
- With lazy loading, No-DR images use only 2.5GB

### Low accuracy
- Verify threshold is set to 0.30 in `backend/app.py` line 116
- Check that CASCADE model is being used (not APTOS)
- Ensure deterministic mode is enabled (it is by default)

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check CORS is enabled (it is by default)
- Verify firewall isn't blocking localhost connections

## Development

### Running Tests

Evaluate model accuracy:
```bash
cd backend
python evaluate_ensemble.py --runs 5 --threshold 0.30
```

Test on specific grade:
```bash
python quick_test_threshold.py
```

### Building for Production

Frontend build:
```bash
cd Website
npm run build
```

Serve production build:
```bash
npm run preview
```

## Deployment Considerations

1. **Model Hosting**: Models stored externally (not in git)
2. **VRAM Optimization**: Lazy loading reduces hosting costs by 69%
3. **FP16 Mode**: Available but not recommended (accuracy drops 20%)
4. **Threshold**: Currently optimized at 0.30 for Grade 1 sensitivity

## Medical Disclaimer

This AI system is for **screening and research purposes only**. It is not a substitute for professional medical diagnosis. All results should be reviewed by a qualified ophthalmologist before making clinical decisions.

## License

Educational and research use. For clinical deployment, ensure proper medical device certification and regulatory approval.

## Acknowledgments

- AttentionUNet for vessel segmentation
- DualStreamConvNeXt for cascade classification
- VDMDR and APTOS datasets for training
- Threshold optimization improved Grade 1 detection from 10% to 80%

## Support

For issues:
1. Check model paths in `config.py`
2. Verify dependencies are installed (`pip list`, `npm list`)
3. Review `OPTIMIZATION_SUMMARY.md` for performance details
4. Ensure Python 3.8+ and Node.js 18+

---

**Status**: Production-ready with 88% accuracy
**Last Updated**: December 2024
