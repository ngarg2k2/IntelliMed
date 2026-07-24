import os
import secrets
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.auth import authenticate, current_user, hash_password
from app.db import Base, SessionLocal, engine, get_db
from app.ml import SYMPTOMS, assess, forecasts, train_symptom_model
from app.models import Medicine, MonthlyUsage, Order, OrderItem, User
from app.seed import seed_database


ROOT = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=ROOT / "app" / "templates")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_database(db)
    train_symptom_model()
    yield


app = FastAPI(title="IntelliMed", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("INTELLIMED_SESSION_SECRET", "development-only-change-me"),
    https_only=os.getenv("INTELLIMED_SECURE_COOKIES", "false").lower() == "true",
    same_site="lax",
)
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")


def csrf_token(request: Request) -> str:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(24)
    return request.session["csrf_token"]


def verify_csrf(request: Request, submitted: str) -> None:
    expected = request.session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(expected, submitted):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid form token")


def view_context(request: Request, db: Session, **values: object) -> dict[str, object]:
    cart = request.session.get("cart", {})
    return {
        "request": request,
        "user": current_user(request, db),
        "cart_count": sum(int(quantity) for quantity in cart.values()),
        "csrf_token": csrf_token(request),
        **values,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    medicines = db.scalars(select(Medicine).order_by(Medicine.name).limit(3)).all()
    return templates.TemplateResponse(request, "index.html", view_context(request, db, medicines=medicines))


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "auth.html", view_context(request, db, mode="login"))


@app.post("/login")
def login(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    csrf: str = Form(),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf)
    user = authenticate(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "auth.html",
            view_context(request, db, mode="login", error="Invalid email or password."),
            status_code=400,
        )
    request.session["user_id"] = user.id
    return RedirectResponse("/admin" if user.role == "admin" else "/", status_code=303)


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "auth.html", view_context(request, db, mode="signup"))


@app.post("/signup")
def signup(
    request: Request,
    name: str = Form(min_length=2, max_length=80),
    email: str = Form(max_length=160),
    password: str = Form(min_length=10, max_length=128),
    csrf: str = Form(),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf)
    normalized_email = email.lower().strip()
    if db.scalar(select(User).where(User.email == normalized_email)):
        return templates.TemplateResponse(
            request,
            "auth.html",
            view_context(request, db, mode="signup", error="An account already exists for this email."),
            status_code=400,
        )
    user = User(name=name.strip(), email=normalized_email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
def logout(request: Request, csrf: str = Form()):
    verify_csrf(request, csrf)
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/assessment", response_class=HTMLResponse)
def assessment_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request, "assessment.html", view_context(request, db, symptoms=SYMPTOMS, result=None, recommendations=[])
    )


@app.post("/assessment", response_class=HTMLResponse)
async def assessment_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    verify_csrf(request, str(form.get("csrf", "")))
    selected = [str(value) for value in form.getlist("symptoms")]
    result = assess(selected)
    recommendations = []
    if result.medicine_skus:
        recommendations = db.scalars(select(Medicine).where(Medicine.sku.in_(result.medicine_skus))).all()
    return templates.TemplateResponse(
        request,
        "assessment.html",
        view_context(
            request,
            db,
            symptoms=SYMPTOMS,
            selected=selected,
            result=result,
            recommendations=recommendations,
        ),
    )


@app.get("/catalog", response_class=HTMLResponse)
def catalog(request: Request, db: Session = Depends(get_db)):
    medicines = db.scalars(select(Medicine).order_by(Medicine.category, Medicine.name)).all()
    return templates.TemplateResponse(request, "catalog.html", view_context(request, db, medicines=medicines))


@app.post("/cart/add")
def cart_add(
    request: Request,
    medicine_id: int = Form(),
    quantity: int = Form(ge=1, le=10),
    csrf: str = Form(),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf)
    medicine = db.get(Medicine, medicine_id)
    if not medicine or medicine.stock < quantity:
        raise HTTPException(status_code=400, detail="Medicine unavailable in requested quantity")
    cart = request.session.get("cart", {})
    new_quantity = int(cart.get(str(medicine_id), 0)) + quantity
    if new_quantity > min(10, medicine.stock):
        raise HTTPException(status_code=400, detail="Cart quantity exceeds available stock")
    cart[str(medicine_id)] = new_quantity
    request.session["cart"] = cart
    return RedirectResponse("/cart", status_code=303)


def cart_details(request: Request, db: Session) -> tuple[list[dict[str, object]], float]:
    cart = request.session.get("cart", {})
    items: list[dict[str, object]] = []
    total = 0.0
    for medicine_id, quantity in cart.items():
        medicine = db.get(Medicine, int(medicine_id))
        if medicine:
            subtotal = medicine.price * int(quantity)
            items.append({"medicine": medicine, "quantity": int(quantity), "subtotal": subtotal})
            total += subtotal
    return items, total


@app.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request, db: Session = Depends(get_db)):
    items, total = cart_details(request, db)
    return templates.TemplateResponse(request, "cart.html", view_context(request, db, items=items, total=total))


@app.post("/checkout")
def checkout(request: Request, csrf: str = Form(), db: Session = Depends(get_db)):
    verify_csrf(request, csrf)
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    items, total = cart_details(request, db)
    if not items:
        return RedirectResponse("/cart", status_code=303)
    for item in items:
        medicine = item["medicine"]
        if medicine.stock < item["quantity"]:
            raise HTTPException(status_code=409, detail=f"Insufficient stock for {medicine.name}")
    order = Order(user_id=user.id, total=total)
    db.add(order)
    current_month = date.today().replace(day=1)
    for item in items:
        medicine = item["medicine"]
        quantity = item["quantity"]
        medicine.stock -= quantity
        order.items.append(OrderItem(medicine_id=medicine.id, quantity=quantity, unit_price=medicine.price))
        usage = db.scalar(select(MonthlyUsage).where(MonthlyUsage.medicine_id == medicine.id, MonthlyUsage.month == current_month))
        if usage:
            usage.quantity += quantity
        else:
            db.add(MonthlyUsage(medicine_id=medicine.id, month=current_month, quantity=quantity))
    db.commit()
    request.session["cart"] = {}
    return RedirectResponse(f"/orders/{order.id}", status_code=303)


@app.get("/orders/{order_id}", response_class=HTMLResponse)
def order_confirmation(order_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    order = db.get(Order, order_id)
    if not user or not order or (order.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "order.html", view_context(request, db, order=order))


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if user.role != "admin":
        raise HTTPException(status_code=403)
    return templates.TemplateResponse(request, "admin.html", view_context(request, db, forecasts=forecasts(db)))


@app.post("/admin/restock")
def restock(
    request: Request,
    medicine_id: int = Form(),
    quantity: int = Form(ge=1, le=1000),
    csrf: str = Form(),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf)
    user = current_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403)
    medicine = db.get(Medicine, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404)
    medicine.stock += quantity
    db.commit()
    return RedirectResponse("/admin", status_code=303)
