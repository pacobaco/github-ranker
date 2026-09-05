PLANS = {
    "free": {"name": "Free", "monthly_price": 0, "max_analyses_per_month": 3, "max_repos_per_analysis": 10, "max_orgs": 0, "included_seats": 1, "features": ["basic_ranking"]},
    "pro": {"name": "Pro", "monthly_price": 19, "max_analyses_per_month": 50, "max_repos_per_analysis": 100, "max_orgs": 0, "included_seats": 1, "features": ["full_rubric", "export", "history"]},
    "business": {"name": "Business", "monthly_price": 79, "max_analyses_per_month": 500, "max_repos_per_analysis": 9999, "max_orgs": 1, "included_seats": 5, "extra_seat_price": 12, "features": ["api_access", "team", "orgs", "seats", "shared_quota"]},
    "enterprise": {"name": "Enterprise", "monthly_price": None, "max_analyses_per_month": 99999, "max_repos_per_analysis": 9999, "max_orgs": 999, "included_seats": 25, "extra_seat_price": 8, "features": ["orgs", "seats", "sso", "sla", "white_label"]},
}
PLAN_ORDER = ["free", "pro", "business", "enterprise"]
