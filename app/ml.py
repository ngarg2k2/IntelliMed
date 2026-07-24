from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Medicine, MonthlyUsage


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SYMPTOM_MODEL = ARTIFACTS / "symptom_classifier.joblib"
DEMAND_MODEL = ARTIFACTS / "demand_forecaster.joblib"

SYMPTOMS = [
    "fever", "cough", "sore_throat", "runny_nose", "sneezing", "headache",
    "body_ache", "fatigue", "nausea", "vomiting", "diarrhea", "stomach_pain",
    "acidity", "itching", "rash", "watery_eyes", "shortness_of_breath", "chest_pain",
]

PROFILES = {
    "Common cold": {"cough", "sore_throat", "runny_nose", "sneezing", "fatigue"},
    "Flu-like illness": {"fever", "cough", "headache", "body_ache", "fatigue"},
    "Seasonal allergy": {"runny_nose", "sneezing", "itching", "watery_eyes"},
    "Gastroenteritis pattern": {"nausea", "vomiting", "diarrhea", "stomach_pain", "fatigue"},
    "Acid reflux pattern": {"stomach_pain", "acidity", "nausea"},
}

RECOMMENDATIONS = {
    "Common cold": ["OTC-COUGH", "OTC-PARA"],
    "Flu-like illness": ["OTC-PARA", "OTC-ORS"],
    "Seasonal allergy": ["OTC-CET"],
    "Gastroenteritis pattern": ["OTC-ORS"],
    "Acid reflux pattern": ["OTC-ANT"],
}

EMERGENCY_SYMPTOMS = {"chest_pain", "shortness_of_breath"}


@dataclass
class Assessment:
    label: str
    confidence: float
    urgent: bool
    message: str
    medicine_skus: list[str]


def train_symptom_model() -> None:
    rng = np.random.default_rng(42)
    rows: list[list[int]] = []
    labels: list[str] = []
    for label, profile in PROFILES.items():
        base = np.array([int(symptom in profile) for symptom in SYMPTOMS])
        for _ in range(180):
            row = base.copy()
            flips = rng.random(len(SYMPTOMS)) < 0.08
            row[flips] = 1 - row[flips]
            rows.append(row.tolist())
            labels.append(label)
    model = RandomForestClassifier(n_estimators=220, max_depth=9, random_state=42)
    model.fit(rows, labels)
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump({"model": model, "features": SYMPTOMS}, SYMPTOM_MODEL)


def assess(selected: list[str]) -> Assessment:
    selected_set = set(selected) & set(SYMPTOMS)
    if selected_set & EMERGENCY_SYMPTOMS:
        return Assessment(
            label="Urgent symptoms selected",
            confidence=1.0,
            urgent=True,
            message="Seek urgent medical care now. Do not use this tool to delay emergency evaluation.",
            medicine_skus=[],
        )
    if not selected_set:
        return Assessment("No assessment", 0, False, "Select at least one symptom.", [])
    if not SYMPTOM_MODEL.exists():
        train_symptom_model()
    artifact = joblib.load(SYMPTOM_MODEL)
    vector = [[int(symptom in selected_set) for symptom in artifact["features"]]]
    probabilities = artifact["model"].predict_proba(vector)[0]
    best = int(np.argmax(probabilities))
    label = str(artifact["model"].classes_[best])
    confidence = float(probabilities[best])
    if confidence < 0.55:
        return Assessment("Uncertain pattern", confidence, False, "The symptoms do not form a confident pattern. Consult a clinician or pharmacist.", [])
    return Assessment(
        label,
        confidence,
        False,
        "This is an educational pattern match, not a diagnosis or prescription. Confirm suitability with a pharmacist.",
        RECOMMENDATIONS.get(label, []),
    )


def _forecast_rows(db: Session) -> tuple[list[list[float]], list[int]]:
    features: list[list[float]] = []
    targets: list[int] = []
    for medicine in db.scalars(select(Medicine).order_by(Medicine.id)):
        usage = db.scalars(select(MonthlyUsage).where(MonthlyUsage.medicine_id == medicine.id).order_by(MonthlyUsage.month)).all()
        for index in range(3, len(usage)):
            features.append([medicine.id, usage[index].month.month, usage[index - 1].quantity, usage[index - 2].quantity, usage[index - 3].quantity])
            targets.append(usage[index].quantity)
    return features, targets


def train_demand_model(db: Session) -> None:
    features, targets = _forecast_rows(db)
    if len(features) < 10:
        raise ValueError("At least 10 monthly training rows are required")
    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    model.fit(features, targets)
    ARTIFACTS.mkdir(exist_ok=True)
    joblib.dump(model, DEMAND_MODEL)


def forecasts(db: Session) -> list[dict[str, int | str]]:
    train_demand_model(db)
    model = joblib.load(DEMAND_MODEL)
    output: list[dict[str, int | str]] = []
    for medicine in db.scalars(select(Medicine).order_by(Medicine.name)):
        recent = db.scalars(select(MonthlyUsage).where(MonthlyUsage.medicine_id == medicine.id).order_by(MonthlyUsage.month.desc()).limit(3)).all()
        if len(recent) < 3:
            continue
        next_month = 1 if date.today().month == 12 else date.today().month + 1
        predicted = max(0, round(float(model.predict([[medicine.id, next_month, recent[0].quantity, recent[1].quantity, recent[2].quantity]])[0])))
        suggested = max(0, predicted + medicine.reorder_level - medicine.stock)
        output.append({"id": medicine.id, "name": medicine.name, "stock": medicine.stock, "forecast": predicted, "suggested": suggested})
    return output