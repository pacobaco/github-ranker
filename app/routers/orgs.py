from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Organization, OrgMembership, OrgRole
from app.schemas import OrgCreate, InviteCreate, SeatPurchase
from app.auth import get_current_user
from app.deps import require_plan
from app.services.orgs import create_org, require_org_role, invite_member, accept_invite, seat_capacity, seat_used

router = APIRouter(prefix="/orgs", tags=["organizations"])

@router.post("")
def create(payload: OrgCreate, user: User = Depends(require_plan("business")), db: Session = Depends(get_db)):
    org = create_org(db, user, payload.name)
    return {"id":org.id,"name":org.name,"slug":org.slug,"seats_used":seat_used(db,org),"seat_limit":seat_capacity(org)}

@router.get("/mine")
def mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(OrgMembership).filter(OrgMembership.user_id == user.id).all()
    return [{"org_id":m.org.id,"name":m.org.name,"role":m.role,"seats_used":seat_used(db,m.org),"seat_limit":seat_capacity(m.org)} for m in rows]

@router.post("/{org_id}/invites")
def invite(org_id:int,payload:InviteCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    require_org_role(db,user,org_id,{OrgRole.owner.value,OrgRole.admin.value})
    org=db.query(Organization).filter(Organization.id==org_id).first()
    if not org: raise HTTPException(404,"Organization not found")
    inv=invite_member(db,org,payload.email,payload.role,user)
    return {"email":inv.email,"role":inv.role,"token":inv.token,"expires_at":inv.expires_at}

@router.post("/invites/{token}/accept")
def accept(token:str,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    m=accept_invite(db,user,token); return {"org_id":m.org_id,"role":m.role}

@router.delete("/{org_id}/members/{user_id}")
def remove_member(org_id:int,user_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    require_org_role(db,user,org_id,{OrgRole.owner.value,OrgRole.admin.value})
    m=db.query(OrgMembership).filter_by(org_id=org_id,user_id=user_id).first()
    if not m or m.role==OrgRole.owner.value: raise HTTPException(400,"Cannot remove this member")
    db.delete(m); db.commit(); return {"removed":True}

@router.post("/{org_id}/seats")
def buy_seats(org_id:int,payload:SeatPurchase,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    require_org_role(db,user,org_id,{OrgRole.owner.value})
    if payload.extra_seats<1: raise HTTPException(400,"extra_seats must be >= 1")
    org=db.query(Organization).filter(Organization.id==org_id).first()
    org.extra_seats += payload.extra_seats; db.commit()
    return {"seat_limit":seat_capacity(org),"extra_seats":org.extra_seats}
