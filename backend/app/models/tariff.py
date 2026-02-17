from sqlalchemy import Column, String, Numeric, Text, Index, ForeignKey
from app.db.base_class import Base
import uuid


class Tariff(Base):
    __tablename__ = "tariffs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hs_code = Column(String(12), ForeignKey("hs_codes.code"), nullable=False, index=True)
    country_origin = Column(String(2), nullable=False, index=True)  # 'CN', 'US', 'EU'
    country_destination = Column(String(2), nullable=False, index=True)  # 'US', 'EU', 'CN'
    rate_type = Column(String(20), nullable=False)  # 'MFN', 'USMCA', 'RCEP', 'GSP', etc.
    duty_rate = Column(Numeric(10, 2), nullable=False)  # Percentage (e.g., 2.5 = 2.5%)
    min_duty = Column(Numeric(10, 2), nullable=True)
    max_duty = Column(Numeric(10, 2), nullable=True)
    unit = Column(String(10), nullable=True)  # '%', 'kg', 'liter', 'unit'
    quota_limit = Column(Numeric(15, 2), nullable=True)
    quota_year = Column(String(4), nullable=True)
    notes = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_tariff_search', 'hs_code', 'country_origin', 'country_destination', 'rate_type'),
        Index('ix_tariff_origin_dest', 'country_origin', 'country_destination'),
    )
