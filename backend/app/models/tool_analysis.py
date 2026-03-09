from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Index
from datetime import datetime
import uuid
from app.db.base_class import Base


class ToolAnalysis(Base):
    """Saved compliance tool analysis results."""
    __tablename__ = "tool_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    tool_type = Column(String(50), nullable=False, index=True)  # cashflow | drawback | usmca | supply_chain | hts_audit | sourcing | scenario
    title = Column(String(255), nullable=False)
    form_data = Column(JSON, nullable=True)   # inputs used to generate this analysis
    result_data = Column(JSON, nullable=False)  # full API response payload
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('idx_tool_analyses_user_type', 'user_id', 'tool_type'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tool_type": self.tool_type,
            "title": self.title,
            "form_data": self.form_data,
            "result_data": self.result_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
