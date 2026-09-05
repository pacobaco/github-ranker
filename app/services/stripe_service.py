import stripe
from app.config import settings

stripe.api_key = settings.stripe_secret_key or None
PRICE_MAP = {"pro": settings.stripe_price_pro, "business": settings.stripe_price_business}

def create_checkout_session(customer_email: str, customer_id: str | None, plan: str) -> str:
    if plan not in PRICE_MAP or not PRICE_MAP[plan]:
        raise ValueError("Invalid or unconfigured plan price")
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id or None,
        customer_email=None if customer_id else customer_email,
        line_items=[{"price": PRICE_MAP[plan], "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}/billing/cancel",
        metadata={"plan": plan, "email": customer_email},
    )
    return session.url

def create_portal_session(customer_id: str) -> str:
    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=f"{settings.frontend_url}/account")
    return session.url
