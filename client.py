import feedparser
import csv
import re
from collections import Counter
from datetime import datetime
from email.utils import parsedate_to_datetime


def strip_html(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

FEED_URL = "https://fintechnews.my/feed/"

CATEGORY_FEEDS = {
    "payments": "https://fintechnews.my/category/payments-remittance/feed/",
    "blockchain": "https://fintechnews.my/category/blockchain/feed/",
    "digital-banking": "https://fintechnews.my/category/digital-banking/feed/",
    "insurtech": "https://fintechnews.my/category/insurtech/feed/",
    "wealthtech": "https://fintechnews.my/category/wealthtech/feed/",
    "regtech": "https://fintechnews.my/category/regtech/feed/",
    "e-wallets": "https://fintechnews.my/category/e-wallets/feed/",
    "lending": "https://fintechnews.my/category/lending/feed/",
    "ai": "https://fintechnews.my/category/artificial-intelligence/feed/",
    "islamic-fintech": "https://fintechnews.my/category/islamic-fintech/feed/",
    "security": "https://fintechnews.my/category/security/feed/",
}


def parse_date(entry) -> str:
    try:
        dt = parsedate_to_datetime(entry.get("published", ""))
        return dt.strftime("%d %b %Y")
    except Exception:
        return "Unknown date"


def parse_datetime(entry) -> datetime:
    try:
        return parsedate_to_datetime(entry.get("published", "")).replace(tzinfo=None)
    except Exception:
        return datetime.min


def get_full_content(entry) -> str:
    content_list = entry.get("content", [])
    if content_list:
        return strip_html(content_list[0].get("value", ""))
    return strip_html(entry.get("summary", ""))


def fetch_articles(limit: int = 20, category: str = None) -> list[dict]:
    url = CATEGORY_FEEDS.get(category, FEED_URL) if category else FEED_URL
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:limit]:
        categories = [tag.term for tag in entry.get("tags", [])]
        articles.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "date": parse_date(entry),
            "datetime": parse_datetime(entry),
            "author": entry.get("author", "Fintech News Malaysia"),
            "summary": get_full_content(entry),
            "categories": categories,
        })
    return articles


def search_articles(keyword: str, limit: int = 20) -> list[dict]:
    feed = feedparser.parse(FEED_URL)
    keyword_lower = keyword.lower()
    results = []
    for entry in feed.entries:
        title = entry.get("title", "")
        full_content = get_full_content(entry)
        categories = [tag.term for tag in entry.get("tags", [])]
        if keyword_lower in title.lower() or keyword_lower in full_content.lower():
            results.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "datetime": parse_datetime(entry),
                "author": entry.get("author", "Fintech News Malaysia"),
                "summary": full_content,
                "categories": categories,
            })
        if len(results) >= limit:
            break
    return results


def track_keyword(keyword: str) -> dict:
    feed = feedparser.parse(FEED_URL)
    keyword_lower = keyword.lower()
    matches = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        categories = [tag.term for tag in entry.get("tags", [])]
        if keyword_lower in title.lower() or keyword_lower in summary.lower():
            matches.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "categories": categories,
            })
    category_counts = Counter(
        cat for article in matches for cat in article["categories"]
    )
    return {
        "keyword": keyword,
        "mention_count": len(matches),
        "articles": matches,
        "top_categories": category_counts.most_common(5),
    }


CATEGORY_TAG_MAP = {
    "payments": ["payments", "payments & remittance", "remittance"],
    "blockchain": ["blockchain", "blockchain/bitcoin", "bitcoin", "crypto", "tokenisation", "tokenization"],
    "digital-banking": ["digital banking", "digital bank", "neobank"],
    "insurtech": ["insurtech", "insurance", "takaful"],
    "wealthtech": ["wealthtech", "wealth", "investment"],
    "regtech": ["regtech", "regulation", "compliance", "bnm", "bank negara", "sc", "securities commission"],
    "e-wallets": ["e-wallet", "e-wallets", "ewallet"],
    "lending": ["lending", "loan", "financing", "credit"],
    "ai": ["ai", "artificial intelligence", "machine learning"],
    "islamic-fintech": ["islamic", "shariah", "sukuk", "halal"],
    "security": ["security", "fraud", "scam", "cybersecurity"],
}


def map_to_category(tags: list[str]) -> str:
    tags_lower = [t.lower() for t in tags]
    for category, keywords in CATEGORY_TAG_MAP.items():
        for kw in keywords:
            if any(kw in t for t in tags_lower):
                return category
    return "other"


IMPORTANT_ENTITIES = [
    "bank negara", "bnm", "securities commission", "sc malaysia",
    "khazanah", "maybank", "cimb", "rhb", "hong leong", "public bank",
    "blackrock", "central bank", "ministry of finance", "mof",
    "bursa malaysia", "petronas", "epf", "kwap", "pnb",
]

HIGH_WEIGHT_TAGS = [
    "blockchain", "tokenisation", "tokenization", "regulation", "regtech",
    "policy", "digital banking", "central bank", "sukuk", "security", "fraud",
]


def score_article(entry) -> float:
    score = 0.0

    # Recency — freshest articles score highest
    dt = parse_datetime(entry)
    hours_ago = (datetime.utcnow() - dt).total_seconds() / 3600
    if hours_ago < 12:
        score += 12
    elif hours_ago < 24:
        score += 9
    elif hours_ago < 48:
        score += 6
    elif hours_ago < 72:
        score += 3
    else:
        score += 1

    # Important institution mentions
    combined = (entry.get("title", "") + " " + get_full_content(entry)).lower()
    for entity in IMPORTANT_ENTITIES:
        if entity in combined:
            score += 2

    # High-weight topic tags
    tags = [tag.term.lower() for tag in entry.get("tags", [])]
    for tag in HIGH_WEIGHT_TAGS:
        if any(tag in t for t in tags):
            score += 3

    # Content depth — longer articles tend to be more substantial
    content_len = len(get_full_content(entry))
    score += min(content_len / 600, 5)

    # Tag specificity — penalise generic "Various" articles
    specific_tags = [t for t in tags if t not in ("various", "featured")]
    score += len(specific_tags) * 0.5

    return score


def parse_timestamp(entry) -> str:
    try:
        dt = parsedate_to_datetime(entry.get("published", ""))
        return dt.strftime("%d %b %Y · %H:%M")
    except Exception:
        return "Unknown"


def get_top_news(limit: int = 10) -> list[dict]:
    feed = feedparser.parse(FEED_URL)
    scored = []
    for entry in feed.entries:
        tags = [tag.term for tag in entry.get("tags", [])]
        clean_tags = [t for t in tags if t.lower() not in ("various", "featured")]
        scored.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "timestamp": parse_timestamp(entry),
            "summary": get_full_content(entry),
            "tags": clean_tags,
            "score": score_article(entry),
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def get_digest() -> dict:
    feed = feedparser.parse(FEED_URL)
    today = datetime.utcnow().strftime("%d %b %Y")
    grouped = {}
    for entry in feed.entries:
        tags = [tag.term for tag in entry.get("tags", [])]
        category = map_to_category(tags)
        article = {
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "date": parse_date(entry),
            "summary": get_full_content(entry),
            "tags": tags,
        }
        grouped.setdefault(category, []).append(article)

    sorted_sections = dict(
        sorted(grouped.items(), key=lambda x: (x[0] == "other", -len(x[1])))
    )
    return {"date": today, "sections": sorted_sections}


def get_trending(top_n: int = 10) -> list[tuple]:
    feed = feedparser.parse(FEED_URL)
    tag_counter = Counter()
    for entry in feed.entries:
        tags = [tag.term for tag in entry.get("tags", [])]
        # skip generic tags
        filtered = [t for t in tags if t.lower() not in ("various", "featured")]
        tag_counter.update(filtered)
    return tag_counter.most_common(top_n)


def export_articles(articles: list[dict], filepath: str):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "date", "categories", "link", "summary"])
        writer.writeheader()
        for a in articles:
            writer.writerow({
                "title": a["title"],
                "date": a["date"],
                "categories": ", ".join(a["categories"]),
                "link": a["link"],
                "summary": a.get("summary", ""),
            })


def list_categories() -> list[str]:
    return list(CATEGORY_FEEDS.keys())
