# AgroScan AI – Plant Leaf Disease Detection

Upload a photo of a plant **leaf** and get the crop, the disease (or "healthy"), a confidence score, and treatment / prevention advice.

- **Frontend:** React + Vite + Tailwind (`agroscan-ai/`, runs on `http://localhost:5173`)
- **Backend:** FastAPI + PyTorch (`backend/`, runs on `http://localhost:8000`)
- **Model:** [Daksh159/plant-disease-mobilenetv2](https://huggingface.co/Daksh159/plant-disease-mobilenetv2) – MobileNetV2 fine-tuned on PlantVillage (38 classes, ~95% validation accuracy)

## Project structure

```
agriculture/
├── README.md
├── mobilenetv2_plant.pth      # model weights (download from Hugging Face)
├── agroscan-ai/               # React frontend
│   └── src/App.jsx
└── backend/                   # FastAPI backend
    ├── main.py                # API + model loading/inference
    ├── disease_data.py        # 38 class labels + disease info & advice
    └── requirements.txt
```

## What the model detects

The model looks at **leaves**. It was trained on PlantVillage, a dataset of single leaves photographed on a plain background. It does not look at fruit, tubers or whole fields. Photos of fruit (for example a tomato or an apple) may give wrong results.

14 crops, 38 classes:

| Crop | Classes |
|------|---------|
| Apple | Apple scab, Black rot, Cedar apple rust, Healthy |
| Blueberry | Healthy |
| Cherry | Powdery mildew, Healthy |
| Corn (maize) | Gray leaf spot (Cercospora), Common rust, Northern leaf blight, Healthy |
| Grape | Black rot, Esca (Black measles), Leaf blight (Isariopsis), Healthy |
| Orange | Huanglongbing (Citrus greening) |
| Peach | Bacterial spot, Healthy |
| Bell pepper | Bacterial spot, Healthy |
| Potato | Early blight, Late blight, Healthy |
| Raspberry | Healthy |
| Soybean | Healthy |
| Squash | Powdery mildew |
| Strawberry | Leaf scorch, Healthy |
| Tomato | Bacterial spot, Early blight, Late blight, Leaf mold, Septoria leaf spot, Spider mites, Target spot, Yellow leaf curl virus, Mosaic virus, Healthy |

**Tips for good results:** take a close-up of one leaf that fills most of the frame, in good light, on a plain background if you can.

> The model only knows these 14 crops. A leaf from any other plant will still be matched to the closest of the 38 classes. The UI shows a warning when confidence is below 50%.

## Setup

### 1. Model weights

Download `mobilenetv2_plant.pth` from the [Hugging Face repo](https://huggingface.co/Daksh159/plant-disease-mobilenetv2/tree/main) and place it in the project root (next to this README). To use a different location, set the `MODEL_PATH` environment variable.

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu   # CPU build (smaller)
pip install -r requirements.txt

uvicorn main:app --reload        # http://localhost:8000  (docs at /docs)
```

### 3. Frontend

```bash
cd agroscan-ai
npm install
npm run dev                      # http://localhost:5173
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server and model status |
| POST | `/predict` | Multipart upload, form field `file` (jpg/png/webp/bmp/gif, max 10 MB) |
| GET | `/diseases` | All 38 classes and disease info |
| GET | `/docs` | Swagger UI |

Example `/predict` response (shortened):

```json
{
  "plantType": "Tomato (Solanum lycopersicum)",
  "healthScore": 33,
  "status": "Needs Attention",
  "lowConfidence": false,
  "diagnosis": {
    "condition": "Late Blight",
    "label": "Tomato – Late Blight",
    "rawLabel": "Tomato___Late_blight",
    "isHealthy": false,
    "type": "fungal",
    "probability": 0.97,
    "severity": "Severe",
    "spreadRisk": "High",
    "description": "...",
    "treatment": "...",
    "prevention": "..."
  },
  "topPredictions": [
    { "label": "Tomato – Late Blight", "probability": 0.97 },
    { "label": "Potato – Late Blight", "probability": 0.02 },
    { "label": "Tomato – Early Blight", "probability": 0.004 }
  ],
  "requirements": { "water": {}, "sunlight": {}, "fertilizer": {} }
}
```

## Model details

- Architecture: torchvision `mobilenet_v2`, classifier head `Dropout(0.2) → Linear(1280, 38)`
- Input: 224×224 RGB, ImageNet normalization (mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`)
- Dataset: New Plant Diseases Dataset (Augmented), PlantVillage, ~87k leaf images
- Class order: alphabetical PlantVillage folder names (see `backend/disease_data.py`)

> Water, sunlight and NPK values in the results are general guidance for the type of disease (fungal, bacterial, viral or pest). They are not measured from the photo.

## License

The model weights are licensed under Apache-2.0 by their author.
