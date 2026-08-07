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
