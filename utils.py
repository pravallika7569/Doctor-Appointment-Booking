import re, pickle, os
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer

# -----------------------------
# 1. Preprocessing Function
# -----------------------------
def preprocess_symptoms(text: str) -> str:
    text = text or ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# -----------------------------
# 2. Rule-Based Fallback
# -----------------------------
RULE_MAP = {
    'chest pain': 'Cardiologist',
    'chest': 'Cardiologist',
    'rash': 'Dermatologist',
    'skin': 'Dermatologist',
    'headache': 'Neurologist',
    'dizziness': 'Neurologist',
    'fever': 'General Physician',
    'cough': 'General Physician',
    'stomach': 'Gastroenterologist',
    'tooth': 'Dentist',
    'eye': 'Ophthalmologist',
    'back pain': 'Orthopedist'
}


# -----------------------------
# 3. ML Recommender (TF-IDF)
# -----------------------------
class SymptomRecommender:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.labels = None

        model_path = os.path.join(os.path.dirname(__file__), 'models', 'ml_model.pkl')

        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    bundle = pickle.load(f)
                    self.model = bundle.get('model')
                    self.vectorizer = bundle.get('vectorizer')
                    self.labels = bundle.get('labels')
            except Exception as e:
                print("Model loading error:", e)

    def predict(self, symptoms: str, extra_features: dict = None) -> List[str]:
        symptoms = preprocess_symptoms(symptoms)

        # 🔹 ML Prediction (TF-IDF)
        if self.model and self.vectorizer:
            try:
                X = self.vectorizer.transform([symptoms])
                pred_idx = self.model.predict(X)[0]

                if isinstance(self.labels, (list, tuple)):
                    return [self.labels[pred_idx]]
                return [str(pred_idx)]

            except Exception as e:
                print("Prediction error:", e)

        # 🔹 Rule-Based Fallback
        matched = []
        for k, v in RULE_MAP.items():
            if k in symptoms:
                matched.append(v)

        if matched:
            return list(set(matched))

        return ['General Physician']


# -----------------------------
# 4. Chatbot Response
# -----------------------------
def chat_response(symptoms: str, extra_features: dict = None) -> dict:
    recommender = SymptomRecommender()
    recommendations = recommender.predict(symptoms, extra_features)

    text = preprocess_symptoms(symptoms)
    reply_parts = []

    if any(x in text for x in ['fever', 'cough', 'sore', 'throat']):
        reply_parts.append("You may have a cold or infection. Stay hydrated and rest well.")

    elif any(x in text for x in ['chest', 'palpit', 'shortness']):
        reply_parts.append("Chest symptoms can be serious. Seek immediate medical attention if severe.")

    elif any(x in text for x in ['rash', 'itch', 'skin', 'acne']):
        reply_parts.append("Skin conditions are usually manageable but consult a dermatologist if persistent.")

    elif any(x in text for x in ['headache', 'dizzy', 'numb']):
        reply_parts.append("Neurological symptoms should not be ignored if severe or frequent.")

    else:
        reply_parts.append("I can suggest a specialist, but this is not a substitute for professional diagnosis.")

    followup = ''
    if 'pain' in text and not any(x in text for x in ['since', 'days', 'hours']):
        followup = "How long have you been experiencing this pain?"

    return {
        "reply": " ".join(reply_parts),
        "recommendations": recommendations,
        "followup": followup
    }


# -----------------------------
# 5. TRAINING SCRIPT (RUN ONCE)
# -----------------------------
def train_model():
    from sklearn.linear_model import LogisticRegression

    # Sample training data (you can expand this)
    texts = [
        "chest pain and pressure",
        "skin rash and itching",
        "severe headache and dizziness",
        "fever and cough",
        "tooth pain",
        "eye irritation",
        "stomach pain and acidity",
        "back pain after injury"
    ]

    labels = [
        "Cardiologist",
        "Dermatologist",
        "Neurologist",
        "General Physician",
        "Dentist",
        "Ophthalmologist",
        "Gastroenterologist",
        "Orthopedist"
    ]

    # 🔹 TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    # 🔹 Model
    model = LogisticRegression()
    model.fit(X, range(len(labels)))

    bundle = {
        "model": model,
        "vectorizer": vectorizer,
        "labels": labels
    }

    os.makedirs("models", exist_ok=True)
    with open("models/ml_model.pkl", "wb") as f:
        pickle.dump(bundle, f)

    print("✅ TF-IDF Model trained and saved!")


# -----------------------------
# RUN TRAINING (ONLY FIRST TIME)
# -----------------------------
if __name__ == "__main__":
    train_model()