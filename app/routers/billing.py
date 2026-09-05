from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe
from app.database import get_db
from app.models import User
from app.schemas import CheckoutRequest
from app.auth import get_current_user
from app.services.stripe_service import create_checkout_session, create_portal_session
from app.config import settings

router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/checkout")
def checkout(payload: CheckoutRequest, user: User = Depends(get_current_user)):
    if payload.plan not in ("pro", "business"): raise HTTPException(400, "Plan must be pro or business")
    try: url = create_checkout_session(user.email, user.stripe_customer_id, payload.plan)
    except Exception as e: raise HTTPException(400, str(e))
    return {"checkout_url": url}

@router.post("/portal")
def portal(user: User = Depends(get_current_user)):
    if not user.stripe_customer_id: raise HTTPException(400, "No Stripe customer on file")
    return {"portal_url": create_portal_session(user.stripe_customer_id)}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try: event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except Exception: raise HTTPException(400, "Invalid webhook")
    obj = event["data"]["object"]
    if event["type"] == "checkout.session.completed":
        email = obj.get("customer_email") or obj.get("metadata", {}).get("email")
        plan = obj.get("metadata", {}).get("plan", "pro")
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.plan = plan; user.stripe_customer_id = obj.get("customer"); db.commit()
    if event["type"] in ("customer.subscription.deleted", "invoice.payment_failed"):
        user = db.query(User).filter(User.stripe_customer_id == obj.get("customer")).first()
        if user: user.plan = "free"; db.commit()
    return {"received": True}
