#!/bin/bash
# Download models from Google Drive during deployment

echo "Downloading models..."

# Create models directory
mkdir -p models

# Download each model (replace FILE_ID with your actual Google Drive file IDs)
# Format: gdown <file_id> -O models/filename.pth

# Vessel segmentation model
# gdown YOUR_FILE_ID_HERE -O models/vessel_best_model_green.pth

# Stage 1: Binary DR classification (Healthy vs DR)
# gdown YOUR_FILE_ID_HERE -O models/1.pth

# Stage 2: Early vs Advanced DR classification
# gdown YOUR_FILE_ID_HERE -O models/2.pth

# Stage 3a: Mild vs Moderate DR classification
# gdown YOUR_FILE_ID_HERE -O models/3a.pth

# Stage 3b: Severe vs Proliferative DR classification
# gdown YOUR_FILE_ID_HERE -O models/3b.pth

echo "Models downloaded successfully!"
