from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..base import Base
import enum

class RiskScoreEnum(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SeverityEnum(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class CodeAnalysis(Base):
    """Code analysis model for storing analysis history."""
    __tablename__ = 'code_analysis'

    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_snippet = Column(Text, nullable=False)
    risk_score = Column(SQLEnum(RiskScoreEnum), nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    vulnerabilities = relationship("Vulnerability", back_populates="analysis", cascade="all, delete-orphan")
    fixes = relationship("Fix", back_populates="analysis", cascade="all, delete-orphan")

class Vulnerability(Base):
    """Vulnerability model for storing detected vulnerabilities."""
    __tablename__ = 'vulnerabilities'

    vulnerability_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('code_analysis.analysis_id'), nullable=False)
    line = Column(Integer, nullable=False)
    severity = Column(SQLEnum(SeverityEnum), nullable=False)
    type = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    analysis = relationship("CodeAnalysis", back_populates="vulnerabilities")

class Fix(Base):
    """Fix model for storing suggested fixes."""
    __tablename__ = 'fixes'

    fix_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('code_analysis.analysis_id'), nullable=False)
    line = Column(Integer, nullable=False)
    original = Column(Text, nullable=False)
    fixed = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    analysis = relationship("CodeAnalysis", back_populates="fixes")


