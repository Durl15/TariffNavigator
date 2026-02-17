from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Numeric, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

# Use standard UUID for SQLite compatibility
class ClassificationHistory(Base):
    __tablename__ = "classification_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_description = Column(Text, nullable=False)
    suggested_hts_code = Column(String(10))
    confidence_score = Column(Numeric(3, 2))
    rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))

class CostCalculationHistory(Base):
    __tablename__ = "cost_calculation_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customs_value = Column(Numeric(12, 2))
    total_landed_cost = Column(Numeric(12, 2))
    breakdown = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Import User model
from app.models.user import User
