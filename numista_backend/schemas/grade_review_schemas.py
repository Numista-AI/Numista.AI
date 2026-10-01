"""
Nicknames and Grade Review Community Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class NicknameSubmitRequest(BaseModel):
    user_email: str
    coin_title: str
    nickname: str
    rationale: Optional[str] = ""

class GradeReviewSubmission(BaseModel):
    user_email: str
    coin_id: str
    submitted_grade: str
    notes: Optional[str] = ""

class GradeReviewSubmitRequest(BaseModel):
    """JSON body for POST /api/grade_review/submit sent by HttpAuthClient."""
    coin_id: str
    action: str                          # 'confirmed' | 'corrected'
    suggested_grade: Optional[str] = ""
    rating: int = Field(..., ge=1, le=5)
    notes: Optional[str] = ""
