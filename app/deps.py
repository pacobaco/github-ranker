from fastapi import Depends, HTTPException, status
from app.auth import get_current_user
from app.models import User
from app.plans import PLAN_ORDER

def require_plan(min_plan: str = "free"):
    def _dep(user: User = Depends(get_current_user)) -> User:
        current = user.plan if user.plan in PLAN_ORDER else "free"
        if PLAN_ORDER.index(current) < PLAN_ORDER.index(min_plan):
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"Requires {min_plan} plan or higher")
        return user
    return _dep
