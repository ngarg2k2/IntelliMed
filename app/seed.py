import os
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import Medicine, MonthlyUsage, User


MEDICINES = [
    ("OTC-PARA", "Paracetamol 500 mg", "Pain and fever", "For temporary relief of mild pain and fever.", 30.00, 90, 25),
    ("OTC-CET", "Cetirizine 10 mg", "Allergy", "For temporary relief of common allergy symptoms.", 45.00, 65, 20),
    ("OTC-ORS", "Oral rehydration salts", "Hydration", "Electrolyte solution powder for dehydration support.", 25.00, 80, 20),
    ("OTC-ANT", "Antacid tablets", "Digestive care", "Temporary relief of occasional heartburn and acidity.", 60.00, 55, 18),
    ("OTC-COUGH", "Saline cough lozenges", "Respiratory care", "Soothing lozenges for minor throat irritation.", 55.00, 70, 20),
]

LEGACY_PRICES = {
    "OTC-PARA": 4.50,
    "OTC-CET": 6.25,
    "OTC-ORS": 3.75,
    "OTC-ANT": 5.00,
    "OTC-COUGH": 4.00,
}


def month_offset(base: date, offset: int) -> date:
    absolute = base.year * 12 + base.month - 1 + offset
    return date(absolute // 12, absolute % 12 + 1, 1)


def seed_database(db: Session) -> None:
    if not db.scalar(select(func.count(User.id))):
        production = os.getenv("INTELLIMED_ENV") == "production"
        admin_email = os.getenv("INTELLIMED_ADMIN_EMAIL")
        admin_password = os.getenv("INTELLIMED_ADMIN_PASSWORD")
        if production and (not admin_email or not admin_password):
            raise RuntimeError("Production requires INTELLIMED_ADMIN_EMAIL and INTELLIMED_ADMIN_PASSWORD")
        users = [
            User(
                name="Store Admin",
                email=admin_email or "admin@intellimed.local",
                password_hash=hash_password(admin_password or "Admin123!"),
                role="admin",
            )
        ]
        if not production:
            users.append(
                User(
                    name="Demo Customer",
                    email="customer@intellimed.local",
                    password_hash=hash_password("Customer123!"),
                )
            )
        db.add_all(users)

    if not db.scalar(select(func.count(Medicine.id))):
        db.add_all(
            [Medicine(sku=sku, name=name, category=category, description=description, price=price, stock=stock, reorder_level=reorder)
             for sku, name, category, description, price, stock, reorder in MEDICINES]
        )
        db.flush()
    else:
        inr_prices = {sku: price for sku, _, _, _, price, _, _ in MEDICINES}
        for medicine in db.scalars(select(Medicine)).all():
            if medicine.price == LEGACY_PRICES.get(medicine.sku):
                medicine.price = inr_prices[medicine.sku]

    if not db.scalar(select(func.count(MonthlyUsage.id))):
        medicines = db.scalars(select(Medicine).order_by(Medicine.id)).all()
        current_month = date.today().replace(day=1)
        for medicine_index, medicine in enumerate(medicines):
            baseline = 18 + medicine_index * 4
            for offset in range(-18, 0):
                seasonal = 6 if month_offset(current_month, offset).month in {1, 2, 7, 8, 12} else 0
                quantity = baseline + seasonal + ((offset + medicine_index * 3) % 7)
                db.add(MonthlyUsage(medicine_id=medicine.id, month=month_offset(current_month, offset), quantity=quantity))
    db.commit()
