from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# --- Category ---
class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Payload для создания категории."""


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Brand ---
class BrandBase(BaseModel):
    name: str
    slug: str


class BrandCreate(BrandBase):
    """Payload для создания бренда."""


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class BrandRead(BrandBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Product ---
class ProductBase(BaseModel):
    sku: str
    name: str
    slug: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    price_cents: Optional[int] = None
    is_active: Optional[bool] = None


class ProductCreate(BaseModel):
    sku: str
    name: str
    slug: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    price_cents: int
    is_active: bool = True


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    price_cents: Optional[int] = None
    is_active: Optional[bool] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Пэйджинг ---
class Page(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ProductRead]
