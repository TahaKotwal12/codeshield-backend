from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskScore(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Severity(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Vulnerability(BaseModel):
    line: int = Field(..., description="Line number where vulnerability is found")
    severity: Severity = Field(..., description="Severity level of the vulnerability")
    type: str = Field(..., description="Type of vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")

class Fix(BaseModel):
    line: int = Field(..., description="Line number where fix is needed")
    original: str = Field(..., description="Original vulnerable code")
    fixed: str = Field(..., description="Fixed code")
    explanation: str = Field(..., description="Explanation of the fix")

class AnalyzeRequest(BaseModel):
    code: str = Field(..., description="Code to analyze", min_length=1, max_length=50000)

class AnalyzeResponse(BaseModel):
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="List of vulnerabilities found")
    fixes: List[Fix] = Field(default_factory=list, description="List of suggested fixes")
    risk_score: RiskScore = Field(..., description="Overall risk score")
    explanation: str = Field(..., description="Detailed explanation of the analysis")

class AnalysisHistoryResponse(BaseModel):
    analysis_id: str
    code_snippet: str
    risk_score: RiskScore
    vulnerability_count: int
    created_at: str


