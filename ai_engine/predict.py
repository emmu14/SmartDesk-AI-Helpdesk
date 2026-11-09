from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "ticket_model.pkl"

model = None


def load_model():
    global model

    if model is None:
        model = joblib.load(MODEL_PATH)

    return model


def predict_category(description):
    """
    Predict the category of a support ticket.
    """

    if not description or not description.strip():
        raise ValueError("Ticket description cannot be empty.")

    trained_model = load_model()

    probabilities = trained_model.predict_proba([description])[0]

    best_index = probabilities.argmax()

    category = trained_model.classes_[best_index]

    confidence = float(probabilities[best_index] * 100)

    return {
        "category": str(category),
        "confidence": round(confidence, 2)
    }