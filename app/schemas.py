from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    plan: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RankRequest(BaseModel):
    username: str
    max_repos: int = 25
    org_id: Optional[int] = None

class RankItem(BaseModel):
    name: str
    total: float
    grade: str
    stars: int
    forks: int
    language: Optional[str] = None
    url: Optional[str] = None
    breakdown: dict

class RankResponse(BaseModel):
    github_username: str
    plan: str
    remaining_analyses: int
    ranked: List[RankItem]

class CheckoutRequest(BaseModel):
    plan: str

class OrgCreate(BaseModel):
    name: str

class InviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"

class SeatPurchase(BaseModel):
    extra_seats: int

class HistoryItem(BaseModel):
    id: int
    github_username: str
    repo_count: int
    created_at: datetime
