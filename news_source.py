import hashlib
import urllib.parse
import feedparser

SEARCH_QUERIES = [
    "Ethereum ETH ETF SEC staking",
    "Ethereum upgrade EVM layer 2 fees",
    "Ethereum hack exploit bridge security",
    "Ethereum Foundation Vitalik roadmap",
    "ETH whale exchange inflow outflow staking",
    "Ethereum DeFi TVL liquidation stablecoin",
    "ETH institutional treasury company purchase",
    "Federal Reserve inflation crypto Ethereum",
    "Solana Ethereum liquidity migration",
]


def _rss_url(query: str) -> str:
    encoded = urllib.parse.quote(query)
    return (
        f"https://news.google.com/rss/search?q={encoded}"
        "&hl=en-US&gl=US&ceid=US:en"
    )


def fetch_news(max_per_query: int = 5) -> list[dict]:
    results = []
    seen = set()

    for query in SEARCH_QUERIES:
        feed = feedparser.parse(_rss_url(query))

        for entry in feed.entries[:max_per_query]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            published = entry.get("published", "")
            source = entry.get("source", {}).get("title", "Google News")

            external_id = hashlib.sha256(
                f"{title}|{link}".encode("utf-8")
            ).hexdigest()

            if external_id in seen:
                continue

            seen.add(external_id)
            results.append(
                {
                    "external_id": external_id,
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": published,
                }
            )

    return results
