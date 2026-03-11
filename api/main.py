"""FastAPI app for trip duration prediction."""

import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load model from project root or models/ dir
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT, "models", "model.pkl")
if not os.path.isfile(MODEL_PATH):
    MODEL_PATH = os.path.join(ROOT, "model.pkl")

from src.preprocessing import TripDataPreprocessor

app = FastAPI(title="Trip Duration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load(MODEL_PATH)


class TripData(BaseModel):
    id: str
    vendor_id: int
    pickup_datetime: str
    pickup_longitude: float
    pickup_latitude: float
    dropoff_longitude: float
    dropoff_latitude: float
    passenger_count: int
    store_and_fwd_flag: str


@app.get("/")
def root():
    return {"message": "Trip Duration Prediction API", "docs": "/docs"}


@app.post("/predict")
def predict(trip: TripData):
    try:
        df = pd.DataFrame([trip.model_dump()])
        processor = TripDataPreprocessor()
        df_processed = processor.fit_transform(df, is_train=False)
        prediction = model.predict(df_processed)[0]
        duration_minutes = round(np.expm1(prediction) / 60, 1)
        return {"predicted_duration": duration_minutes}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
