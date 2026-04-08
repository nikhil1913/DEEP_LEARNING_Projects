"""
Waste Classifier API
====================
FastAPI backend that serves the MobileNetV2 waste classification model.
Accepts image uploads and returns predicted class, recyclability, and disposal tips.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="Waste Classifier API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Model & Class Config ────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "Project", "waste_classifier_final_model.keras")
IMG_SIZE = (224, 224)

CLASS_NAMES = [
    'aluminium_foil', 'broken_glass', 'cardboard_box', 'ceramic_broken',
    'chips_packet', 'cigarette_butt', 'diaper', 'fabric_clothes',
    'glass_bottle', 'gutka_packet', 'metal_can', 'newspaper_paper',
    'notebook_waste', 'plastic_bottle', 'polythene_bag', 'sanitary_napkin',
    'soiled_tissue', 'steel_utensil', 'tetra_pak', 'thermocol'
]

RECYCLABLE = {
    'plastic_bottle', 'cardboard_box', 'glass_bottle', 'metal_can',
    'newspaper_paper', 'notebook_waste', 'aluminium_foil', 'steel_utensil',
    'tetra_pak', 'fabric_clothes'
}

NON_RECYCLABLE = {
    'thermocol', 'chips_packet', 'diaper', 'cigarette_butt',
    'polythene_bag', 'gutka_packet', 'broken_glass', 'sanitary_napkin',
    'ceramic_broken', 'soiled_tissue'
}

DISPLAY_NAMES = {
    'aluminium_foil': 'Aluminium Foil',
    'broken_glass': 'Broken Glass',
    'cardboard_box': 'Cardboard Box',
    'ceramic_broken': 'Broken Ceramic',
    'chips_packet': 'Chips Packet',
    'cigarette_butt': 'Cigarette Butt',
    'diaper': 'Diaper',
    'fabric_clothes': 'Fabric / Clothes',
    'glass_bottle': 'Glass Bottle',
    'gutka_packet': 'Gutka Packet',
    'metal_can': 'Metal Can',
    'newspaper_paper': 'Newspaper / Paper',
    'notebook_waste': 'Notebook Waste',
    'plastic_bottle': 'Plastic Bottle',
    'polythene_bag': 'Polythene Bag',
    'sanitary_napkin': 'Sanitary Napkin',
    'soiled_tissue': 'Soiled Tissue',
    'steel_utensil': 'Steel Utensil',
    'tetra_pak': 'Tetra Pak',
    'thermocol': 'Thermocol / Styrofoam'
}

DISPOSAL_TIPS = {
    'aluminium_foil': 'Clean the foil and place it in the recycling bin. Crumple into a ball so it doesn\'t fly away.',
    'broken_glass': 'Wrap carefully in newspaper. Label as "SHARP" and dispose in general waste — not recycling.',
    'cardboard_box': 'Flatten the box and place in paper/cardboard recycling. Remove any tape or staples.',
    'ceramic_broken': 'Wrap in newspaper and dispose in general waste. Ceramics cannot be recycled with glass.',
    'chips_packet': 'Multi-layer packaging — goes in general waste. Some TerraCycle programs accept these.',
    'cigarette_butt': 'Dispose in general waste. Never litter — they take 10+ years to decompose.',
    'diaper': 'Wrap tightly and dispose in general waste. Never flush or recycle.',
    'fabric_clothes': 'Donate if wearable. Otherwise, take to textile recycling or use as cleaning rags.',
    'glass_bottle': 'Rinse and place in glass recycling. Remove caps and lids separately.',
    'gutka_packet': 'Dispose in general waste. These multi-layer packets are non-recyclable.',
    'metal_can': 'Rinse and place in metal recycling. Crush if possible to save space.',
    'newspaper_paper': 'Place in paper recycling bin. Keep dry — wet paper can\'t be recycled.',
    'notebook_waste': 'Remove spiral bindings and place paper in recycling. Metal spirals go in metal recycling.',
    'plastic_bottle': 'Rinse, crush, and place in plastic recycling. Keep the cap on.',
    'polythene_bag': 'Reuse when possible. Many grocery stores have drop-off bins for plastic bag recycling.',
    'sanitary_napkin': 'Wrap in newspaper and dispose in general waste. Never flush.',
    'soiled_tissue': 'Dispose in general waste. Soiled paper products cannot be recycled.',
    'steel_utensil': 'Take to a scrap dealer or metal recycling center. Steel is infinitely recyclable!',
    'tetra_pak': 'Rinse and place in carton recycling. Check local guidelines — some areas collect separately.',
    'thermocol': 'Dispose in general waste. Styrofoam is rarely accepted in municipal recycling.'
}

# ─── Load Model ───────────────────────────────────────────────────────────────
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully!")

# ─── Static Files ─────────────────────────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/demo")
async def demo():
    return FileResponse(os.path.join(STATIC_DIR, "demo.html"))

@app.get("/brief")
async def brief():
    return FileResponse(os.path.join(STATIC_DIR, "explanation.html"))


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = image.resize(IMG_SIZE)
        img_array = np.array(image, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)  # (1, 224, 224, 3)

        # Predict
        predictions = model.predict(img_array, verbose=0)
        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index]) * 100

        class_name = CLASS_NAMES[predicted_index]
        is_recyclable = class_name in RECYCLABLE

        # Top 3 predictions
        top_3_indices = np.argsort(predictions[0])[::-1][:3]
        top_3 = [
            {
                "class": CLASS_NAMES[i],
                "display_name": DISPLAY_NAMES[CLASS_NAMES[i]],
                "confidence": round(float(predictions[0][i]) * 100, 1),
                "recyclable": CLASS_NAMES[i] in RECYCLABLE
            }
            for i in top_3_indices
        ]

        return JSONResponse({
            "success": True,
            "prediction": {
                "class": class_name,
                "display_name": DISPLAY_NAMES[class_name],
                "confidence": round(confidence, 1),
                "recyclable": is_recyclable,
                "category": "Recyclable ♻️" if is_recyclable else "Non-Recyclable 🚫",
                "disposal_tip": DISPOSAL_TIPS.get(class_name, ""),
                "top_3": top_3
            }
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
