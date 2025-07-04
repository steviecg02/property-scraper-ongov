from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
import uuid
from datetime import datetime

Base = declarative_base()

class PropertyReport(Base):
    __tablename__ = "property_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swiscode = Column(String, nullable=False)
    printkey = Column(String, nullable=False)
    report_json = Column(JSONB, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('swiscode', 'printkey', name='uq_swiscode_printkey'),
    )