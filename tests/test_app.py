from datetime import date

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Medicine, MonthlyUsage, Order
from tests.conftest import csrf


def test_health_and_assessment_safety(client):
    assert client.get("/health").json() == {"status": "ok"}
    token = csrf(client, "/assessment")
    response = client.post(
        "/assessment",
        data={"csrf": token, "symptoms": ["chest_pain", "cough"]},
    )
    assert response.status_code == 200
    assert "Seek urgent medical care now" in response.text
    assert "Options to discuss" not in response.text


def test_assessment_returns_reviewable_options(client):
    token = csrf(client, "/assessment")
    response = client.post(
        "/assessment",
        data={"csrf": token, "symptoms": ["sneezing", "itching", "watery_eyes"]},
    )
    assert response.status_code == 200
    assert "Seasonal allergy" in response.text
    assert "Cetirizine" in response.text


def test_purchase_updates_stock_usage_and_order(client):
    token = csrf(client, "/login")
    response = client.post(
        "/login",
        data={"csrf": token, "email": "customer@intellimed.local", "password": "Customer123!"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with SessionLocal() as db:
        medicine = db.scalar(select(Medicine).where(Medicine.sku == "OTC-ORS"))
        medicine_id = medicine.id
        stock_before = medicine.stock

    token = csrf(client, "/catalog")
    assert client.post(
        "/cart/add",
        data={"csrf": token, "medicine_id": medicine_id, "quantity": 2},
        follow_redirects=False,
    ).status_code == 303
    token = csrf(client, "/cart")
    response = client.post("/checkout", data={"csrf": token}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/orders/")

    with SessionLocal() as db:
        medicine = db.get(Medicine, medicine_id)
        usage = db.scalar(
            select(MonthlyUsage).where(
                MonthlyUsage.medicine_id == medicine_id,
                MonthlyUsage.month == date.today().replace(day=1),
            )
        )
        assert medicine.stock == stock_before - 2
        assert usage.quantity == 2
        assert db.scalar(select(Order)) is not None


def test_admin_forecast_is_role_protected(client):
    token = csrf(client)
    client.post("/logout", data={"csrf": token})
    assert client.get("/admin", follow_redirects=False).headers["location"] == "/login"
    token = csrf(client, "/login")
    client.post(
        "/login",
        data={"csrf": token, "email": "admin@intellimed.local", "password": "Admin123!"},
    )
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Next month demand" in response.text
