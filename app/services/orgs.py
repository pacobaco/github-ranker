import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Organization, OrgMembership, OrgInvite, OrgRole
from app.plans import PLANS

def slugify(name: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    return slug[:80] or "org"

def seat_capacity(org: Organization) -> int:
    included = PLANS.get(org.plan, PLANS["business"]).get("included_seats", 5)
    return included + org.extra_seats

def seat_used(db: Session, org: Organization) -> int:
    return db.query(OrgMembership).filter(OrgMembership.org_id == org.id).count()

def require_org_role(db: Session, user: User, org_id: int, min_roles: set[str]) -> OrgMembership:
    m = db.query(OrgMembership).filter_by(org_id=org_id, user_id=user.id).first()
    if not m or m.role not in min_roles:
        raise HTTPException(403, "Insufficient organization permission")
    return m

def create_org(db: Session, user: User, name: str) -> Organization:
    if user.plan not in ("business", "enterprise"):
        raise HTTPException(402, "Organizations require Business or higher")
    owned = db.query(OrgMembership).filter(OrgMembership.user_id == user.id, OrgMembership.role == OrgRole.owner.value).count()
    if owned >= PLANS[user.plan].get("max_orgs", 1) and user.plan != "enterprise":
        raise HTTPException(402, "Org limit reached")
    org = Organization(name=name, slug=slugify(name) + "-" + secrets.token_hex(2), plan=user.plan)
    db.add(org)
    db.flush()
    db.add(OrgMembership(org_id=org.id, user_id=user.id, role=OrgRole.owner.value))
    db.commit()
    db.refresh(org)
    return org

def invite_member(db: Session, org: Organization, email: str, role: str, invited_by: User) -> OrgInvite:
    if role == OrgRole.owner.value:
        raise HTTPException(400, "Cannot invite another owner")
    if role not in {r.value for r in OrgRole if r != OrgRole.owner}:
        raise HTTPException(400, "Invalid role")
    if seat_used(db, org) >= seat_capacity(org):
        raise HTTPException(402, "No seats left")
    invite = OrgInvite(org_id=org.id, email=email.lower(), role=role, token=secrets.token_urlsafe(32),
                       invited_by=invited_by.id, expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite

def accept_invite(db: Session, user: User, token: str) -> OrgMembership:
    invite = db.query(OrgInvite).filter(OrgInvite.token == token, OrgInvite.accepted == False).first()
    if not invite or invite.expires_at < datetime.utcnow():
        raise HTTPException(400, "Invite invalid or expired")
    if user.email.lower() != invite.email.lower():
        raise HTTPException(403, "Invite email mismatch")
    org = db.query(Organization).filter(Organization.id == invite.org_id).first()
    if not org or seat_used(db, org) >= seat_capacity(org):
        raise HTTPException(402, "No seats left")
    membership = OrgMembership(org_id=org.id, user_id=user.id, role=invite.role)
    invite.accepted = True
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
