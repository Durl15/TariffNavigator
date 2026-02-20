from sqlalchemy import Column, String, Numeric, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base


class Catalog(Base):
    __tablename__ = "catalogs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True)

    # Catalog metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    total_skus = Column(Integer, nullable=False, default=0)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    items = relationship("CatalogItem", back_populates="catalog", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Catalog {self.id} - {self.name} ({self.total_skus} SKUs)>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "name": self.name,
            "description": self.description,
            "currency": self.currency,
            "total_skus": self.total_skus,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    catalog_id = Column(String(36), ForeignKey('catalogs.id', ondelete='CASCADE'), nullable=False, index=True)

    # Product data
    sku = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=True)
    hs_code = Column(String(20), ForeignKey('hs_codes.code', ondelete='SET NULL'), nullable=True, index=True)
    origin_country = Column(String(2), nullable=False)
    cogs = Column(Numeric(12, 2), nullable=False)  # Cost of goods sold
    retail_price = Column(Numeric(12, 2), nullable=False)
    annual_volume = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=True, index=True)
    weight_kg = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)

    # Calculated fields (cached for performance)
    tariff_cost = Column(Numeric(12, 2), nullable=True)
    landed_cost = Column(Numeric(12, 2), nullable=True)
    gross_margin = Column(Numeric(12, 2), nullable=True)
    margin_percent = Column(Numeric(5, 2), nullable=True)
    annual_tariff_exposure = Column(Numeric(12, 2), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)

    # Relationships
    catalog = relationship("Catalog", back_populates="items")

    def __repr__(self):
        return f"<CatalogItem {self.sku} - {self.product_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "catalog_id": self.catalog_id,
            "sku": self.sku,
            "product_name": self.product_name,
            "hs_code": self.hs_code,
            "origin_country": self.origin_country,
            "cogs": float(self.cogs) if self.cogs else None,
            "retail_price": float(self.retail_price) if self.retail_price else None,
            "annual_volume": self.annual_volume,
            "category": self.category,
            "weight_kg": float(self.weight_kg) if self.weight_kg else None,
            "notes": self.notes,
            "tariff_cost": float(self.tariff_cost) if self.tariff_cost else None,
            "landed_cost": float(self.landed_cost) if self.landed_cost else None,
            "gross_margin": float(self.gross_margin) if self.gross_margin else None,
            "margin_percent": float(self.margin_percent) if self.margin_percent else None,
            "annual_tariff_exposure": float(self.annual_tariff_exposure) if self.annual_tariff_exposure else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
