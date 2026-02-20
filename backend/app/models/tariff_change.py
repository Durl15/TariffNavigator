from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON
from datetime import datetime
from app.db.base_class import Base


class TariffChangeLog(Base):
    """
    Log of detected tariff rate changes.
    Tracks what changed, when, and notification status.
    """
    __tablename__ = "tariff_change_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Change classification
    change_type = Column(String(50), nullable=False, index=True)  # 'rate_update', 'new_program', 'expiration'

    # What changed
    hs_code = Column(String(20), nullable=True, index=True)
    country = Column(String(2), nullable=True, index=True)

    # Change values (JSON for flexibility)
    old_value = Column(JSON, nullable=True)  # {mfn_rate: 5.0, fta_rate: 0.0}
    new_value = Column(JSON, nullable=True)  # {mfn_rate: 7.5, fta_rate: 2.0}

    # Metadata
    source = Column(String(100), nullable=True)  # 'internal', 'federal_register', 'cbp'
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Notification tracking
    notifications_sent = Column(Boolean, default=False, index=True)
    notification_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<TariffChangeLog {self.id}: {self.hs_code} {self.country} ({self.change_type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "change_type": self.change_type,
            "hs_code": self.hs_code,
            "country": self.country,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source": self.source,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "notifications_sent": self.notifications_sent,
            "notification_count": self.notification_count,
        }

    def get_summary(self) -> str:
        """Generate human-readable summary of the change."""
        if self.change_type == 'rate_update':
            old_rate = self.old_value.get('mfn_rate', 0) if self.old_value else 0
            new_rate = self.new_value.get('mfn_rate', 0) if self.new_value else 0
            return f"HS {self.hs_code} ({self.country}): {old_rate}% → {new_rate}%"
        return f"{self.change_type}: {self.hs_code} ({self.country})"
