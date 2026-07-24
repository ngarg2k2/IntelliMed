from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="customer")


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(60))
    description: Mapped[str] = mapped_column(String(300))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=10)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    total: Mapped[float] = mapped_column(Float)
    user: Mapped[User] = relationship()
    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    medicine: Mapped[Medicine] = relationship()


class MonthlyUsage(Base):
    __tablename__ = "monthly_usage"
    __table_args__ = (UniqueConstraint("medicine_id", "month", name="uq_usage_medicine_month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    month: Mapped[date] = mapped_column(Date)
    quantity: Mapped[int] = mapped_column(Integer)
    medicine: Mapped[Medicine] = relationship()
