import io
import os
from datetime import datetime

import torch
import torch.nn as nn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from torchvision import models, transforms

from disease_data import CARE_BY_TYPE, CLASS_NAMES, DISEASE_INFO, parse_class_name

app = FastAPI(
    title="AgroScan AI - Plant Disease Detection",
    description="Detects 38 plant leaf conditions across 14 crops (MobileNetV2, PlantVillage).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model configuration ---------------------------------------------------
# Weights from https://huggingface.co/Daksh159/plant-disease-mobilenetv2
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mobilenetv2_plant.pth"),
)
IMG_SIZE = 224
NUM_CLASSES = len(CLASS_NAMES)  # 38
TOP_K = 3
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp", "gif"}

# Same preprocessing as used in training (ImageNet normalization)
preprocess = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
model_error = None


def build_model(state_dict: dict) -> nn.Module:
    """Rebuild the MobileNetV2 architecture used for training and load weights."""
    net = models.mobilenet_v2(weights=None)
    in_features = net.classifier[1].in_features  # 1280
    if "classifier.1.1.weight" in state_dict:
        # Head from the model card: classifier[1] = Sequential(Dropout(0.2), Linear(1280, 38))
        net.classifier[1] = nn.Sequential(nn.Dropout(0.2), nn.Linear(in_features, NUM_CLASSES))
    else:
        net.classifier[1] = nn.Linear(in_features, NUM_CLASSES)
    net.load_state_dict(state_dict)
    return net


def load_plant_model():
    global model, model_error
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {os.path.abspath(MODEL_PATH)}")
        checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            checkpoint = checkpoint["state_dict"]
        checkpoint = {k.removeprefix("module."): v for k, v in checkpoint.items()}
        model = build_model(checkpoint).to(device).eval()
        model_error = None
        print(f"✓ Model loaded from {os.path.abspath(MODEL_PATH)} on {device} ({NUM_CLASSES} classes)")
    except Exception as e:
        model = None
        model_error = str(e)
        print(f"✗ Error loading model: {e}")


def predict_image(image_bytes: bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Could not read image: {e}")

    x = preprocess(img).unsqueeze(0).to(device)
    with torch.inference_mode():
        probs = torch.softmax(model(x), dim=1)[0].cpu()

    top_probs, top_idx = probs.topk(TOP_K)
    return [(int(i), float(p)) for i, p in zip(top_idx, top_probs)]


def health_score_for(parsed: dict, confidence: float) -> int:
    if parsed["isHealthy"]:
        return int(round(confidence * 100))
    penalty = {"None": 0, "Moderate": 45, "Severe": 70, "Critical": 85}[parsed["info"]["severity"]]
    # Higher confidence in a disease -> lower health score
    return max(5, int(round(100 - penalty * confidence - 10)))


@app.on_event("startup")
async def startup_event():
    load_plant_model()


@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "model_error": model_error,
        "num_classes": NUM_CLASSES,
        "device": str(device),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Analyze a plant **leaf** image and predict crop + disease."""
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded: {model_error}")

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 10 MB limit")

    try:
        top = predict_image(image_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    best_idx, confidence = top[0]
    parsed = parse_class_name(CLASS_NAMES[best_idx])
    info = parsed["info"]
    now = datetime.now()

    response = {
        "id": f"scan_{now.strftime('%Y%m%d%H%M%S')}",
        "plantType": parsed["crop"],
        "healthScore": health_score_for(parsed, confidence),
        "status": "Healthy" if parsed["isHealthy"] else "Needs Attention",
        "timestamp": now.isoformat(),
        "lowConfidence": confidence < 0.5,
        "diagnosis": {
            "condition": info["name"],
            "label": parsed["label"],
            "rawLabel": parsed["raw"],
            "isHealthy": parsed["isHealthy"],
            "type": info["type"],
            "probability": confidence,
            "severity": info["severity"],
            "spreadRisk": info["spreadRisk"],
            "description": info["description"],
            "treatment": info["treatment"],
            "prevention": info["prevention"],
        },
        "topPredictions": [
            {"label": parse_class_name(CLASS_NAMES[i])["label"], "probability": p} for i, p in top
        ],
        "requirements": CARE_BY_TYPE[info["type"]],
    }
    print(f"[predict] {parsed['raw']} ({confidence:.2%})")
    return response


@app.get("/diseases")
async def get_diseases():
    """All classes the model can detect."""
    return {
        "num_classes": NUM_CLASSES,
        "classes": [parse_class_name(c)["label"] for c in CLASS_NAMES],
        "details": DISEASE_INFO,
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to AgroScan AI - Plant Disease Detection API",
        "version": app.version,
        "endpoints": {"health": "/health", "predict": "/predict (POST)", "diseases": "/diseases", "docs": "/docs"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
