from datetime import datetime
from sqlalchemy.orm import Session
from app.models import User, UsageRecord
from app.plans import PLANS

def _month_start():
    return datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def remaining_analyses(db: Session, user: User, org_id: int | None = None) -> int:
    q = db.query(UsageRecord).filter(UsageRecord.created_at >= _month_start())
    if org_id:
        q = q.filter(UsageRecord.org_id == org_id)
    else:
        q = q.filter(UsageRecord.user_id == user.id, UsageRecord.org_id.is_(None))
    used = q.count()
    limit = PLANS.get(user.plan, PLANS["free"])["max_analyses_per_month"]
    return max(0, limit - used)

def record_usage(db: Session, user: User, repos_analyzed: int, org_id: int | None = None) -> None:
    db.add(UsageRecord(user_id=user.id, org_id=org_id, repos_analyzed=repos_analyzed))
    db.commit()
