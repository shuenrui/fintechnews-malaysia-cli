import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime

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
            "author": entry.get("author", "Fintech News Malaysia"),
            "summary": entry.get("summary", "")[:200].strip(),
            "categories": categories,
        })
    return articles


def search_articles(keyword: str, limit: int = 20) -> list[dict]:
    feed = feedparser.parse(FEED_URL)
    keyword_lower = keyword.lower()
    results = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        categories = [tag.term for tag in entry.get("tags", [])]
        if keyword_lower in title.lower() or keyword_lower in summary.lower():
            results.append({
                "title": title,
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "author": entry.get("author", "Fintech News Malaysia"),
                "summary": summary[:200].strip(),
                "categories": categories,
            })
        if len(results) >= limit:
            break
    return results


def list_categories() -> list[str]:
    return list(CATEGORY_FEEDS.keys())
