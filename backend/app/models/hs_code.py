from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.base_class import Base


class HSCode(Base):
    __tablename__ = "hs_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    level = Column(String(20), default="tariff")
    country = Column(String(2), nullable=False, index=True)
    
    # Tariff rate columns
    mfn_rate = Column(Float, default=0.0)
    general_rate = Column(Float, default=0.0)
    vat_rate = Column(Float, default=0.0)
    consumption_tax = Column(Float, default=0.0)
    unit = Column(String(20), default="unit")
    # Add after consumption_tax column
    fta_rate = Column(Float, default=0.0)       # Preferential FTA duty rate
    fta_name = Column(String(100))               # Name of FTA agreement
    fta_countries = Column(String(200))          # Comma-separated list of FTA partner countries

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HSCode {self.country} {self.code}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "level": self.level,
            "country": self.country,
            "rates": {
                "mfn": self.mfn_rate,
                "general": self.general_rate,
                "vat": self.vat_rate,
                "consumption": self.consumption_tax
            },
            "unit": self.unit
        }