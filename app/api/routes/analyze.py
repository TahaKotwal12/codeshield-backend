from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.infra.db.postgres.postgres_config import get_db
from app.api.schemas.analyze_schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Vulnerability,
    Fix,
    RiskScore,
    AnalysisHistoryResponse
)
from app.api.schemas.common_schemas import CommonResponse
from app.services.gemini_service import GeminiService
from app.infra.db.postgres.models.code_analysis import CodeAnalysis, Vulnerability as VulnerabilityModel, Fix as FixModel
from app.config.logger import get_logger
from app.config.config import SECURITY_CONFIG

router = APIRouter(prefix="/analyze", tags=["analyze"])
logger = get_logger(__name__)

# Lazy initialization of Gemini service
_gemini_service = None

def get_gemini_service():
    """Get or create Gemini service instance (lazy initialization)."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

@router.post("", response_model=AnalyzeResponse)
async def analyze_code(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze code for security vulnerabilities using AI.
    
    This endpoint:
    1. Validates the code input
    2. Calls Gemini AI for analysis
    3. Stores the analysis in the database
    4. Returns the analysis results
    
    Returns the analysis directly (not wrapped in CommonResponse) for frontend compatibility.
    """
    try:
        # Validate code length
        if len(request.code) > SECURITY_CONFIG["max_code_length"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Code exceeds maximum length of {SECURITY_CONFIG['max_code_length']} characters"
            )
        
        logger.info(f"Analyzing code (length: {len(request.code)} characters)")
        
        # Analyze code using Gemini (lazy initialization)
        gemini_service = get_gemini_service()
        analysis_result = gemini_service.analyze_code(request.code)
        
        # Create analysis record
        code_analysis = CodeAnalysis(
            code_snippet=request.code[:1000],  # Store first 1000 chars for history
            risk_score=analysis_result["risk_score"],
            explanation=analysis_result["explanation"]
        )
        db.add(code_analysis)
        db.flush()  # Get the analysis_id
        
        # Create vulnerability records
        for vuln_data in analysis_result["vulnerabilities"]:
            vulnerability = VulnerabilityModel(
                analysis_id=code_analysis.analysis_id,
                line=vuln_data["line"],
                severity=vuln_data["severity"],
                type=vuln_data["type"],
                description=vuln_data["description"]
            )
            db.add(vulnerability)
        
        # Create fix records
        for fix_data in analysis_result["fixes"]:
            fix = FixModel(
                analysis_id=code_analysis.analysis_id,
                line=fix_data["line"],
                original=fix_data["original"],
                fixed=fix_data["fixed"],
                explanation=fix_data["explanation"]
            )
            db.add(fix)
        
        # Commit to database
        db.commit()
        db.refresh(code_analysis)
        
        logger.info(f"Analysis completed and saved (ID: {code_analysis.analysis_id})")
        
        # Build and return direct response (matching frontend expectations)
        response = AnalyzeResponse(
            vulnerabilities=[
                Vulnerability(
                    line=v["line"],
                    severity=v["severity"],
                    type=v["type"],
                    description=v["description"]
                )
                for v in analysis_result["vulnerabilities"]
            ],
            fixes=[
                Fix(
                    line=f["line"],
                    original=f["original"],
                    fixed=f["fixed"],
                    explanation=f["explanation"]
                )
                for f in analysis_result["fixes"]
            ],
            risk_score=analysis_result["risk_score"],
            explanation=analysis_result["explanation"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze code: {str(e)}"
        )

@router.get("/history", response_model=CommonResponse[List[AnalysisHistoryResponse]])
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get analysis history.
    
    Returns a list of recent code analyses with basic information.
    """
    try:
        analyses = db.query(CodeAnalysis).order_by(CodeAnalysis.created_at.desc()).offset(offset).limit(limit).all()
        
        history = [
            AnalysisHistoryResponse(
                analysis_id=str(analysis.analysis_id),
                code_snippet=analysis.code_snippet[:100] + "..." if len(analysis.code_snippet) > 100 else analysis.code_snippet,
                risk_score=analysis.risk_score.value,
                vulnerability_count=len(analysis.vulnerabilities),
                created_at=analysis.created_at.isoformat()
            )
            for analysis in analyses
        ]
        
        return CommonResponse(
            code=status.HTTP_200_OK,
            message="Analysis history retrieved successfully",
            message_id="0",
            data=history
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis history: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=CommonResponse[AnalyzeResponse])
async def get_analysis_by_id(
    analysis_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific analysis by ID.
    """
    try:
        analysis = db.query(CodeAnalysis).filter(CodeAnalysis.analysis_id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        response = AnalyzeResponse(
            vulnerabilities=[
                Vulnerability(
                    line=v.line,
                    severity=v.severity.value,
                    type=v.type,
                    description=v.description
                )
                for v in analysis.vulnerabilities
            ],
            fixes=[
                Fix(
                    line=f.line,
                    original=f.original,
                    fixed=f.fixed,
                    explanation=f.explanation
                )
                for f in analysis.fixes
            ],
            risk_score=analysis.risk_score.value,
            explanation=analysis.explanation or ""
        )
        
        return CommonResponse(
            code=status.HTTP_200_OK,
            message="Analysis retrieved successfully",
            message_id="0",
            data=response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )

