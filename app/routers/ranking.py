from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Analysis, AnalysisResult, OrgRole
from app.schemas import RankRequest, RankResponse
from app.auth import get_current_user
from app.deps import require_plan
from app.services.ranker import rank_github_user
from app.services.usage import remaining_analyses, record_usage
from app.services.orgs import require_org_role
from app.plans import PLANS

router = APIRouter(prefix="/rank", tags=["ranking"])

@router.post("", response_model=RankResponse)
def rank_repos(payload: RankRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.org_id: require_org_role(db, user, payload.org_id, {OrgRole.owner.value, OrgRole.admin.value, OrgRole.member.value})
    limits = PLANS.get(user.plan, PLANS["free"])
    max_repos = min(payload.max_repos, limits["max_repos_per_analysis"])
    left = remaining_analyses(db, user, payload.org_id)
    if left <= 0: raise HTTPException(402, "Monthly quota exceeded")
    try: ranked = rank_github_user(payload.username, max_repos=max_repos)
    except Exception as e: raise HTTPException(400, str(e))
    analysis = Analysis(user_id=user.id, org_id=payload.org_id, github_username=payload.username, repo_count=len(ranked))
    db.add(analysis); db.flush()
    for item in ranked:
        db.add(AnalysisResult(analysis_id=analysis.id, repo_name=item["name"], total_score=item["total"], grade=item["grade"], stars=item.get("stars",0), uniqueness=item.get("breakdown",{}).get("uniqueness",0)))
    record_usage(db, user, len(ranked), payload.org_id)
    return RankResponse(github_username=payload.username, plan=user.plan, remaining_analyses=left-1, ranked=ranked)

@router.get("/history")
def history(user: User = Depends(require_plan("pro")), db: Session = Depends(get_db)):
    rows = db.query(Analysis).filter(Analysis.user_id == user.id).order_by(Analysis.created_at.desc()).limit(50).all()
    return [{"id":r.id,"github_username":r.github_username,"repo_count":r.repo_count,"created_at":r.created_at} for r in rows]
