
from sqlalchemy import Column, Integer, String, Text, DateTime  # type: ignore
from datetime import datetime, timezone

from app.database import Base
from pgvector.sqlalchemy import Vector

class MaintenanceRequest(Base):

    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)

    request_code = Column(
        String(30),
        unique=True,
        index=True,
        nullable=False
    )

    title = Column(String(200), nullable=False)

    location = Column(String(150), nullable=False)

    category = Column(String(100), nullable=False)

    priority = Column(String(20), nullable=False)

    description = Column(Text, nullable=False)

    status = Column(
        String(30),
        default="Pending",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
class CampusDocument(Base):

    __tablename__ = "campus_documents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    source = Column(String(255), nullable=False)

    content = Column(Text, nullable=False)

    chunk_index = Column(Integer, nullable=False, default=0)

    embedding = Column(Vector(384), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )