import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Set
from github import Github, Auth
from app.config import settings

STOPWORDS = {"the","and","for","with","this","that","from","are","was","have","has","been","will","can","into","your","you","our"}

def extract_keywords(text: str) -> Set[str]:
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}

def build_feature_set(repo) -> Set[str]:
    features = set()
    try: features.update(t.lower() for t in repo.get_topics())
    except Exception: pass
    try: features.update(lang.lower() for lang in repo.get_languages().keys())
    except Exception: pass
    if repo.language: features.add(repo.language.lower())
    text = repo.description or ""
    try:
        readme = repo.get_readme()
        text += " " + readme.decoded_content.decode("utf-8", errors="ignore")[:8000]
    except Exception: pass
    features.update(extract_keywords(text))
    return features

def uniqueness_map(feature_sets: Dict[str, Set[str]]) -> Dict[str, float]:
    out, names = {}, list(feature_sets)
    for name in names:
        others = set().union(*(feature_sets[n] for n in names if n != name)) if len(names) > 1 else set()
        unique = feature_sets[name] - others
        out[name] = len(unique) / max(1, len(feature_sets[name]))
    return out

def score_repo(repo, uniqueness: float) -> Dict[str, Any]:
    scores = {"uniqueness": round(uniqueness * 30, 1)}
    scores["usage"] = min(20.0, round(math.log1p(repo.stargazers_count)*2.8 + math.log1p(repo.forks_count)*1.6, 1))
    days = 9999
    if repo.pushed_at:
        days = (datetime.now(timezone.utc) - repo.pushed_at.replace(tzinfo=timezone.utc)).days
    scores["activity"] = 15 if days <= 30 else 11 if days <= 90 else 7 if days <= 180 else 4 if days <= 365 else 1
    doc = 0
    try:
        content = repo.get_readme().decoded_content.decode("utf-8", errors="ignore")
        doc += 6
        doc += 5 if len(content) > 2000 else 3 if len(content) > 800 else 1 if len(content) > 300 else 0
    except Exception: pass
    if repo.description and len(repo.description) > 20: doc += 2
    if repo.has_wiki or repo.has_pages: doc += 2
    scores["documentation"] = min(15, doc)
    purpose = 3
    desc = (repo.description or "").lower()
    if any(w in desc for w in ["platform","system","framework","engine","tool","network","dashboard"]): purpose += 3
    if len(desc) > 60: purpose += 2
    try:
        if repo.get_topics(): purpose += 2
    except Exception: pass
    scores["purpose"] = min(10, purpose)
    tech = 2 + (2 if repo.language else 0) + (3 if repo.license else 0) + (2 if repo.size > 50 else 0) + (1 if repo.has_issues else 0)
    scores["technical"] = min(10, tech)
    total = sum(scores.values())
    grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F"
    return {"name": repo.name, "total": round(total,1), "grade": grade, "stars": repo.stargazers_count, "forks": repo.forks_count, "language": repo.language, "url": repo.html_url, "breakdown": scores}

def rank_github_user(username: str, max_repos: int = 25) -> List[Dict[str, Any]]:
    if not settings.github_token: raise RuntimeError("GITHUB_TOKEN is not configured")
    g = Github(auth=Auth.Token(settings.github_token))
    user = g.get_user(username)
    repos = list(user.get_repos(type="owner", sort="updated"))[:max_repos]
    features = {r.name: build_feature_set(r) for r in repos}
    uniq = uniqueness_map(features)
    ranked = [score_repo(r, uniq.get(r.name, 0.3)) for r in repos]
    ranked.sort(key=lambda x: x["total"], reverse=True)
    return ranked
