from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class OrgRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(32), default="free")
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usages: Mapped[list["UsageRecord"]] = relationship(back_populates="user")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="user")
    memberships: Mapped[list["OrgMembership"]] = relationship(back_populates="user")

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(32), default="business")
    extra_seats: Mapped[int] = mapped_column(Integer, default=0)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    members: Mapped[list["OrgMembership"]] = relationship(back_populates="org")
    invites: Mapped[list["OrgInvite"]] = relationship(back_populates="org")

class OrgMembership(Base):
    __tablename__ = "org_memberships"
    __table_args__ = (UniqueConstraint("org_id", "user_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(16), default=OrgRole.member.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    org: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

class OrgInvite(Base):
    __tablename__ = "org_invites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(16), default=OrgRole.member.value)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invited_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    org: Mapped["Organization"] = relationship(back_populates="invites")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    repos_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="usages")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    github_username: Mapped[str] = mapped_column(String(255), index=True)
    repo_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="analyses")
    results: Mapped[list["AnalysisResult"]] = relationship(back_populates="analysis")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    repo_name: Mapped[str] = mapped_column(String(255))
    total_score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(8))
    stars: Mapped[int] = mapped_column(Integer, default=0)
    uniqueness: Mapped[float] = mapped_column(Float, default=0)
    analysis: Mapped["Analysis"] = relationship(back_populates="results")
