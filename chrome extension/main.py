# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import math 
import tensorflow as tf
from tensorflow.keras.models import load_model
from urllib.parse import urlparse
import re

app = FastAPI(title="Malicious Link Detector API")

SUSPICIOUS_WORDS = [
    "login", "signin", "verify", "account", "update",
    "secure", "bank", "paypal", "confirm", "password",
    "webscr", "ebay", "wp", "admin"
]


def shannon_entropy(text):
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0

    entropy = 0
    for c in set(text):
        p = text.count(c) / len(text)
        entropy -= p * math.log2(p)
    return entropy


def preprocess_url(url):
    """
    Extract URL-based features for phishing detection.
    Returns a dictionary.
    """
    if not isinstance(url, str):
        return {}

    url = url.replace("[.]", ".")
    parsed = urlparse(url)

    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    features = {}

    # -----------------------
    # Basic lengths
    # -----------------------
    features["url_length"] = len(url)
    features["domain_length"] = len(domain)
    features["path_length"] = len(path)
    features["query_length"] = len(query)

    # -----------------------
    # Character counts
    # -----------------------
    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_underscores"] = url.count("_")
    features["num_slashes"] = url.count("/")
    features["num_questionmarks"] = url.count("?")
    features["num_equal"] = url.count("=")
    features["num_at"] = url.count("@")
    features["num_ampersand"] = url.count("&")
    features["num_percent"] = url.count("%")
    features["num_digits"] = sum(c.isdigit() for c in url)

    # -----------------------
    # Binary features
    # -----------------------
    features["has_https"] = int(parsed.scheme == "https")
    features["has_ip"] = int(bool(re.match(r"^\d+\.\d+\.\d+\.\d+$", domain)))
    features["has_port"] = int(":" in domain)

    # -----------------------
    # Subdomains
    # -----------------------
    features["num_subdomains"] = max(domain.count(".") - 1, 0)

    # -----------------------
    # Suspicious words
    # -----------------------
    lower_url = url.lower()

    for word in SUSPICIOUS_WORDS:
        features[f"contains_{word}"] = int(word in lower_url)

    # -----------------------
    # Entropy
    # -----------------------
    features["entropy"] = shannon_entropy(url)

    return features
# بارگذاری مدل‌های XGBoost (فرض می‌کنیم به صورت joblib یا pickle ذخیره شده‌اند)
try:
    xgb_model1 = joblib.load("xgb_model1.pkl")
    xgb_model2 = joblib.load("xgb_model2.pkl")
    # بارگذاری مدل عمیق ترکیبی CNN-BiLSTM
    deep_model = load_model("deep_model.h5")
except Exception as e:
    print(f"Error loading models: {e}")

class URLRequest(BaseModel):
    url: str

@app.post("/predict")
def predict_link(request: URLRequest):
    try:
        url = request.url
        # ۱. پیش‌پردازش URL
        xgb_feat, deep_feat = preprocess_url(url)
        
        # ۲. گرفتن احتمالات پیش‌بینی از هر مدل
        # پیش‌بینی XGBoost (معمولاً خروجی predict_proba احتمال کلاس ۱ را می‌دهد)
        prob_xgb1 = xgb_model1.predict_proba(xgb_feat)[0][1]
        prob_xgb2 = xgb_model2.predict_proba(xgb_feat)[0][1]
        
        # پیش‌بینی مدل عمیق
        prob_deep = float(deep_model.predict(deep_feat)[0][0])
        
        # ۳. ترکیب نتایج (Ensemble) - برای مثال میانگین وزن‌دار یا ساده
        # می‌توانید وزن‌های متفاوتی بر اساس دقت هر مدل اختصاص دهید
        final_prob = (prob_xgb1 + prob_xgb2 + prob_deep) / 3.0
        
        # تعیین کلاس نهایی (آستانه ۰.۵)
        prediction = 1 if final_prob >= 0.5 else 0
        
        return {
            "url": url,
            "prediction": prediction,
            "probability": round(final_prob, 4),
            "details": {
                "xgb1": round(float(prob_xgb1), 4),
                "xgb2": round(float(prob_xgb2), 4),
                "deep_model": round(prob_deep, 4)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
