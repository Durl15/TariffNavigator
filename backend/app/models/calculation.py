from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Text, JSON, ForeignKey, Integer
from datetime import datetime
import uuid
from app.db.base_class import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True)

    # User metadata
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Input data
    hs_code = Column(String(20), ForeignKey('hs_codes.code', ondelete='SET NULL'), nullable=False, index=True)
    product_description = Column(Text, nullable=True)
    origin_country = Column(String(2), nullable=False)
    destination_country = Column(String(2), nullable=False)
    cif_value = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')

    # Results
    result = Column(JSON, nullable=False)  # Full calculation result
    total_cost = Column(Numeric(12, 2), nullable=False)
    customs_duty = Column(Numeric(12, 2), nullable=True)
    vat_amount = Column(Numeric(12, 2), nullable=True)
    fta_eligible = Column(Boolean, nullable=False, default=False)
    fta_savings = Column(Numeric(12, 2), nullable=True)

    # Metadata
    is_favorite = Column(Boolean, nullable=False, default=False, index=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    view_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Calculation {self.id} - {self.hs_code} ({self.origin_country}→{self.destination_country})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "hs_code": self.hs_code,
            "product_description": self.product_description,
            "origin_country": self.origin_country,
            "destination_country": self.destination_country,
            "cif_value": float(self.cif_value),
            "currency": self.currency,
            "result": self.result,
            "total_cost": float(self.total_cost),
            "customs_duty": float(self.customs_duty) if self.customs_duty else None,
            "vat_amount": float(self.vat_amount) if self.vat_amount else None,
            "fta_eligible": self.fta_eligible,
            "fta_savings": float(self.fta_savings) if self.fta_savings else None,
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SharedLink(Base):
    __tablename__ = "shared_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(100), nullable=False, unique=True, index=True)
    calculation_id = Column(String(36), ForeignKey('calculations.id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    access_level = Column(String(20), nullable=False, default='view')
    password_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SharedLink {self.token}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True)

    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(36), nullable=True, index=True)
    changes = Column(JSON, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}>"
