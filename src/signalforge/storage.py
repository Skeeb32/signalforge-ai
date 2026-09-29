"""Prediction and monitoring audit storage; PostgreSQL in Compose, SQLite for local demo."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from signalforge.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(80), index=True)
    probability: Mapped[float] = mapped_column(Float)
    risk: Mapped[str] = mapped_column(String(10))
    model_version: Mapped[str] = mapped_column(String(80), index=True)
    features: Mapped[dict] = mapped_column(JSON)
    value_at_risk: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    label: Mapped[int | None] = mapped_column(Integer, nullable=True)


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    report: Mapped[dict] = mapped_column(JSON)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    version: Mapped[str] = mapped_column(String(80), primary_key=True)
    metadata_json: Mapped[dict] = mapped_column(JSON)


def make_engine(url: str = DATABASE_URL):
    return create_engine(url, pool_pre_ping=True,
                         connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})


engine = make_engine()
Session = sessionmaker(engine, expire_on_commit=False)
