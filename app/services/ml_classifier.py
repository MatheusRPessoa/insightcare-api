from functools import lru_cache
from pathlib import Path

import joblib

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "models" / "intent_classifier.joblib"


@lru_cache(maxsize=1)
def load_classifier():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


class MLClassifierService:
    def classify(self, text: str) -> dict:
        model = load_classifier()

        prediction = model.predict([text])[0]
        probabilitites = model.predict_proba([text])[0]

        confidence = float(probabilitites.max())

        return {
            "intent": str(prediction),
            "confidence": round(confidence, 4),
            "model": "tfidf-logistic-regression",
        }
