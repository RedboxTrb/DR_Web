# Retinal DR Detection System

AI-powered web application for automated detection and grading of diabetic retinopathy in retinal fundus images.

## How It Works

```
┌─────────────────┐
│  Upload Image   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Vessel Segmentation     │
│ (AttentionUNet)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Stage 1: DR Detection   │
│ DR vs No-DR             │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  No-DR    Has DR
 Grade 0      │
              ▼
    ┌──────────────────┐
    │ Stage 2:         │
    │ Early vs Advanced│
    └────┬──────┬──────┘
         │      │
    ┌────┘      └────┐
    ▼                ▼
  Early           Advanced
  (1-2)           (3-4)
    │                │
    ▼                ▼
┌────────┐      ┌────────┐
│Stage 3a│      │Stage 3b│
│ 1 vs 2 │      │ 3 vs 4 │
└───┬─┬──┘      └───┬─┬──┘
    │ │             │ │
    ▼ ▼             ▼ ▼
  Gr1 Gr2         Gr3 Gr4
```

## System Components

**Backend (Flask + PyTorch)**
- Vessel segmentation model
- 4-stage cascade classifier
- REST API for image processing

**Frontend (React + TypeScript)**
- Image upload interface
- Results visualization
- Grade classification display

## Grade Classification

- **Grade 0**: No DR
- **Grade 1**: Mild DR
- **Grade 2**: Moderate DR
- **Grade 3**: Severe DR
- **Grade 4**: Proliferative DR

## Usage

1. Start backend server
2. Start frontend application
3. Upload retinal images
4. View classification results

---

**Medical Disclaimer**: This system is for screening and research purposes only. Consult a qualified ophthalmologist for clinical diagnosis.
