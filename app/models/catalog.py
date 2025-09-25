# app/models/catalog.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id], backref="children")

    __table_args__ = (Index("ix_categories_parent", "parent_id"),)


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    brand: Mapped[Optional[Brand]] = relationship()
    category: Mapped[Optional[Category]] = relationship()

    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (UniqueConstraint("slug", name="uq_products_slug"),)

    # отношения
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    inventory: Mapped[Optional["Inventory"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    product: Mapped["Product"] = relationship(back_populates="images")


class Inventory(Base):
    __tablename__ = "inventory"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    track_inventory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    product: Mapped["Product"] = relationship(back_populates="inventory")
