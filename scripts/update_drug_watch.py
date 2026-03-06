#!/usr/bin/env python3
"""Update _data/drug_watch.json with latest innovative-drug intelligence."""

from __future__ import annotations

import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "drug_watch.json"

HEADERS = {
    "User-Agent": "drug-watch-bot/1.0 (mailto:jincaiqi@ucass.edu.cn)",
    "Accept": "application/json, application/xml, text/xml;q=0.9, */*;q=0.8",
}

TIMEOUT_SECONDS = int(os.getenv("DRUG_WATCH_TIMEOUT_SECONDS", "35"))
WINDOW_DAYS = int(os.getenv("DRUG_WATCH_WINDOW_DAYS", "7"))
MAX_DAILY_NEWS = int(os.getenv("DRUG_WATCH_MAX_DAILY_NEWS", "24"))
MAX_LATEST_RESEARCH = int(os.getenv("DRUG_WATCH_MAX_LATEST_RESEARCH", "24"))
MAX_INDUSTRY_RESEARCH = int(os.getenv("DRUG_WATCH_MAX_INDUSTRY_RESEARCH", "24"))
MAX_PUBMED_ITEMS = int(os.getenv("DRUG_WATCH_MAX_PUBMED_ITEMS", "18"))
MAX_RSS_ITEMS_PER_QUERY = int(os.getenv("DRUG_WATCH_MAX_RSS_ITEMS_PER_QUERY", "18"))
MAX_YUANBAO_ITEMS_PER_CATEGORY = int(os.getenv("DRUG_WATCH_MAX_YUANBAO_ITEMS_PER_CATEGORY", "10"))

PUBMED_QUERY = os.getenv(
    "DRUG_WATCH_PUBMED_QUERY",
    (
        '("drug therapy"[Majr] OR "pharmaceutical preparations"[Majr] '
        'OR "innovative drug"[Title/Abstract] OR "first-in-class"[Title/Abstract] '
        'OR "clinical trial"[Title/Abstract] OR "new molecular entity"[Title/Abstract])'
    ),
)

NEWS_QUERY_EN = os.getenv(
    "DRUG_WATCH_NEWS_QUERY_EN",
    (
        '"innovative drug" OR biotech OR "clinical trial" OR "trial readout" '
        'OR FDA OR NMPA OR "drug approval"'
    ),
)
INDUSTRY_QUERY_EN = os.getenv(
    "DRUG_WATCH_INDUSTRY_QUERY_EN",
    (
        '"biotech deal" OR "licensing deal" OR "pharma M&A" '
        'OR "drug pipeline" OR "industry report" OR "biotech financing"'
    ),
)

CORE_DRUG_TERMS = [
    "drug",
    "biotech",
    "pharma",
    "clinical trial",
    "trial",
    "approval",
    "therap",
    "oncology",
    "gene therapy",
    "antibody",
    "first-in-class",
    "new molecular entity",
]

INDUSTRY_SIGNAL_TERMS = [
    "deal",
    "licensing",
    "m&a",
    "financing",
    "pipeline",
    "commercial",
    "market",
    "strategy",
]

HUNYUAN_API_BASE = os.getenv("HUNYUAN_API_BASE", "https://api.hunyuan.cloud.tencent.com/v1").rstrip("/")
HUNYUAN_API_KEY = (
    os.getenv("HUNYUAN_API_KEY", "").strip()
    or os.getenv("TENCENT_YUANBAO_API_KEY", "").strip()
)
HUNYUAN_MODEL = os.getenv("HUNYUAN_MODEL", "hunyuan-turbos-latest")
ENABLE_YUANBAO = (
    os.getenv("DRUG_WATCH_ENABLE_YUANBAO", "true").strip().lower() in {"1", "true", "yes", "on"}
)

DEFAULT_WATCH_KEYWORDS = [
    "innovative drug",
    "clinical trial",
    "NDA",
    "BLA",
    "FDA",
    "NMPA",
    "phase 1",
    "phase 2",
    "phase 3",
    "licensing deal",
    "biotech financing",
]

DEFAULT_SOURCES = [
    {"name": "WeChat Official Accounts", "url": "https://weixin.qq.com/", "type": "social_media"},
    {"name": "Toutiao", "url": "https://www.toutiao.com/", "type": "social_media"},
    {"name": "Weibo", "url": "https://weibo.com/", "type": "social_media"},
    {"name": "Zhihu", "url": "https://www.zhihu.com/", "type": "social_media"},
    {"name": "Xiaohongshu", "url": "https://www.xiaohongshu.com/", "type": "social_media"},
    {"name": "People's Daily", "url": "http://www.people.com.cn/", "type": "news_media"},
    {"name": "Xinhua News Agency", "url": "http://www.news.cn/", "type": "news_media"},
    {"name": "The Economist", "url": "https://www.economist.com/", "type": "news_media"},
    {"name": "Financial Times", "url": "https://www.ft.com/", "type": "news_media"},
    {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/", "type": "academic_database"},
]


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def strip_html_text(value: str) -> str:
    if not value:
        return ""
    s = unescape(value)
    s = re.sub(r"<[^>]+>", " ", s)
    return normalize_text(s)


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def shrink_text(value: str, max_chars: int = 780) -> str:
    s = normalize_text(value)
    if len(s) <= max_chars:
        return s
    return s[:max_chars].rsplit(" ", 1)[0] + " ..."


def parse_date(value: Any) -> str:
    s = normalize_text(value)
    if not s:
        return ""

    for fmt in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y-%m",
        "%Y/%m",
        "%Y %b %d",
        "%Y %b",
        "%Y",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            if fmt == "%Y":
                return f"{dt.year:04d}-01-01"
            if fmt in {"%Y-%m", "%Y/%m"}:
                return f"{dt.year:04d}-{dt.month:02d}-01"
            return dt.date().isoformat()
        except Exception:
            continue

    try:
        dt2 = parsedate_to_datetime(s)
        if dt2:
            if dt2.tzinfo:
                dt2 = dt2.astimezone(timezone.utc)
            return dt2.date().isoformat()
    except Exception:
        pass

    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    if m:
        return m.group(0)

    m2 = re.search(r"\d{4}/\d{2}/\d{2}", s)
    if m2:
        return m2.group(0).replace("/", "-")

    return s[:20]


def is_recent_date(value: str, *, window_days: int) -> bool:
    s = normalize_text(value)
    if not s:
        return True
    try:
        dt = datetime.strptime(s[:10], "%Y-%m-%d").date()
        now_date = datetime.now(timezone.utc).date()
        delta = (now_date - dt).days
        return 0 <= delta <= max(1, window_days + 1)
    except Exception:
        return True


def request_with_retry(url: str, *, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    last_error: Optional[Exception] = None
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(attempt * 2)
    raise RuntimeError(f"GET failed for {url}: {last_error}")


def is_relevant_text(
    text: str,
    *,
    any_terms: Optional[List[str]] = None,
    required_groups: Optional[List[List[str]]] = None,
) -> bool:
    lower = normalize_text(text).lower()
    if not lower:
        return False

    if any_terms and not any(term in lower for term in any_terms):
        return False

    if required_groups:
        for group in required_groups:
            if group and not any(term in lower for term in group):
                return False

    return True


def load_existing() -> Dict[str, Any]:
    if not OUTPUT.exists():
        return {}
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_existing_category_items(existing: Dict[str, Any], category_id: str) -> List[Dict[str, Any]]:
    for cat in existing.get("categories", []):
        if normalize_text(cat.get("id")) == category_id:
            items = cat.get("items", [])
            return items if isinstance(items, list) else []
    return []


def dedupe_items(items: Iterable[Dict[str, Any]], *, limit: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for item in items:
        title = normalize_text(item.get("title"))
        if not title:
            continue
        url = normalize_text(item.get("url")).lower()
        key = ("u", url) if url else ("t", title.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def fetch_pubmed_latest() -> Tuple[List[Dict[str, Any]], Optional[str]]:
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    try:
        search_resp = request_with_retry(
            esearch_url,
            params={
                "db": "pubmed",
                "term": PUBMED_QUERY,
                "retmode": "json",
                "retmax": MAX_PUBMED_ITEMS,
                "sort": "pub+date",
                "datetype": "pdat",
                "reldate": WINDOW_DAYS,
            },
        )
        search_data = search_resp.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        id_list = [normalize_text(i) for i in id_list if normalize_text(i)]
        if not id_list:
            return [], None

        joined_ids = ",".join(id_list)

        summary_resp = request_with_retry(
            esummary_url,
            params={"db": "pubmed", "id": joined_ids, "retmode": "json"},
        )
        summary_data = summary_resp.json().get("result", {})

        abstract_resp = request_with_retry(
            efetch_url,
            params={"db": "pubmed", "id": joined_ids, "retmode": "xml"},
        )
        abstract_map = parse_pubmed_abstracts(abstract_resp.text)

        items: List[Dict[str, Any]] = []
        for pmid in id_list:
            row = summary_data.get(pmid, {})
            if not isinstance(row, dict):
                continue

            title = strip_html_text(row.get("title", ""))
            if not title:
                continue

            date_value = parse_date(row.get("pubdate") or row.get("sortpubdate"))
            journal = normalize_text(row.get("fulljournalname") or row.get("source") or "PubMed")
            abstract_text = shrink_text(abstract_map.get(pmid, ""))

            items.append(
                {
                    "title": title,
                    "date": date_value,
                    "source": journal,
                    "platform": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "summary": abstract_text or "No abstract captured from PubMed.",
                    "tags": ["latest research", "pubmed", "innovative drug"],
                }
            )

        return items, None
    except Exception as exc:
        return [], str(exc)


def parse_pubmed_abstracts(xml_text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return out

    for article in root.findall(".//PubmedArticle"):
        pmid = normalize_text(article.findtext(".//MedlineCitation/PMID"))
        if not pmid:
            continue

        parts: List[str] = []
        for node in article.findall(".//Abstract/AbstractText"):
            label = normalize_text(node.attrib.get("Label", ""))
            text = normalize_text(" ".join(node.itertext()))
            if not text:
                continue
            parts.append(f"{label}: {text}" if label else text)

        out[pmid] = normalize_text(" ".join(parts))
    return out


def fetch_google_news_rss(
    query: str,
    *,
    max_items: int,
    tags: List[str],
    any_terms: Optional[List[str]] = None,
    required_groups: Optional[List[List[str]]] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    url = "https://news.google.com/rss/search"
    params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    try:
        resp = request_with_retry(url, params=params)
        root = ET.fromstring(resp.content)
        items: List[Dict[str, Any]] = []
        for node in root.findall(".//item"):
            title_raw = normalize_text(node.findtext("title"))
            link = normalize_text(node.findtext("link"))
            pub_date = parse_date(node.findtext("pubDate"))
            if not is_recent_date(pub_date, window_days=WINDOW_DAYS):
                continue
            source_name = normalize_text(node.findtext("source"))
            description = strip_html_text(node.findtext("description") or "")

            title = title_raw
            if source_name and title.endswith(f" - {source_name}"):
                title = title[: -len(source_name) - 3]
            title = normalize_text(title)

            if not title:
                continue

            relevance_text = f"{title} {description} {source_name}"
            if not is_relevant_text(
                relevance_text,
                any_terms=any_terms,
                required_groups=required_groups,
            ):
                continue

            items.append(
                {
                    "title": title,
                    "date": pub_date,
                    "source": source_name or "Google News",
                    "platform": "Google News RSS",
                    "url": link,
                    "summary": shrink_text(description or "No summary captured from RSS."),
                    "tags": tags,
                }
            )

            if len(items) >= max_items:
                break

        return items, None
    except Exception as exc:
        return [], str(exc)


def fetch_yuanbao_structured_digest() -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any]]:
    meta: Dict[str, Any] = {
        "enabled": bool(HUNYUAN_API_KEY) and ENABLE_YUANBAO,
        "model": HUNYUAN_MODEL,
        "error": None,
        "search_info_count": 0,
    }
    empty = {"daily_news": [], "latest_research": [], "industry_research": []}

    if not (HUNYUAN_API_KEY and ENABLE_YUANBAO):
        return empty, meta

    today_utc = datetime.now(timezone.utc).date().isoformat()
    prompt = (
        "Build an innovative-drug intelligence digest for the most recent 7 days. "
        "Focus on: WeChat official accounts, Toutiao, Weibo, Zhihu, Xiaohongshu, "
        "People's Daily, Xinhua, The Economist, Financial Times, and PubMed. "
        "Only keep items that are likely true and include a source URL when possible. "
        "Return strict JSON only, no markdown.\n\n"
        "JSON schema:\n"
        "{\n"
        '  "daily_news": [{"title":"","date":"","source":"","platform":"","url":"","summary":"","tags":["",""]}],\n'
        '  "latest_research": [{"title":"","date":"","source":"","platform":"","url":"","summary":"","tags":["",""]}],\n'
        '  "industry_research": [{"title":"","date":"","source":"","platform":"","url":"","summary":"","tags":["",""]}]\n'
        "}\n"
        f"Constraints: max {MAX_YUANBAO_ITEMS_PER_CATEGORY} items per category; date <= {today_utc}; "
        "if URL is unknown keep URL empty."
    )

    payload = {
        "model": HUNYUAN_MODEL,
        "temperature": 0.1,
        "max_tokens": 3200,
        "messages": [
            {"role": "system", "content": "You are a biotech intelligence analyst. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "enable_enhancement": True,
        "force_search_enhancement": True,
        "search_info": True,
        "citation": True,
    }

    headers = {
        "Authorization": f"Bearer {HUNYUAN_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        last_exc: Optional[Exception] = None
        resp_data: Dict[str, Any] = {}
        for attempt in range(1, 4):
            try:
                resp = requests.post(
                    f"{HUNYUAN_API_BASE}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:260]}")
                resp_data = resp.json()
                break
            except Exception as exc:
                last_exc = exc
                if attempt < 3:
                    time.sleep(attempt * 2)
                else:
                    raise

        if not resp_data and last_exc:
            raise RuntimeError(str(last_exc))

        search_info = resp_data.get("search_info", [])
        meta["search_info_count"] = len(search_info) if isinstance(search_info, list) else 0

        content = normalize_text(resp_data.get("choices", [{}])[0].get("message", {}).get("content", ""))
        parsed = parse_json_object_from_text(content)
        structured = {
            "daily_news": normalize_yuanbao_items(parsed.get("daily_news"), "daily news"),
            "latest_research": normalize_yuanbao_items(parsed.get("latest_research"), "latest research"),
            "industry_research": normalize_yuanbao_items(parsed.get("industry_research"), "industry research"),
        }
        return structured, meta
    except Exception as exc:
        meta["error"] = str(exc)
        return empty, meta


def parse_json_object_from_text(text: str) -> Dict[str, Any]:
    s = text.strip()
    if not s:
        return {}

    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?", "", s, flags=re.I).strip()
        s = re.sub(r"```$", "", s).strip()

    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        pass

    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        block = s[start : end + 1]
        try:
            obj2 = json.loads(block)
            return obj2 if isinstance(obj2, dict) else {}
        except Exception:
            return {}
    return {}


def normalize_yuanbao_items(raw_items: Any, fallback_tag: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(raw_items, list):
        return out

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue

        title = normalize_text(raw.get("title"))
        if not title:
            continue

        url = normalize_text(raw.get("url"))
        if url and not re.match(r"^https?://", url, flags=re.I):
            url = ""

        date_value = parse_date(raw.get("date"))
        if not is_recent_date(date_value, window_days=WINDOW_DAYS):
            continue
        source = normalize_text(raw.get("source") or "Yuanbao AI Search")
        platform = normalize_text(raw.get("platform") or source)
        summary = shrink_text(raw.get("summary") or "")

        tags_raw = raw.get("tags")
        if isinstance(tags_raw, list):
            tags = [normalize_text(t) for t in tags_raw if normalize_text(t)]
        else:
            tags = [fallback_tag]
        if fallback_tag not in tags:
            tags.append(fallback_tag)

        out.append(
            {
                "title": title,
                "date": date_value,
                "source": source,
                "platform": platform,
                "url": url,
                "summary": summary or "Captured from Tencent Yuanbao AI Search.",
                "tags": tags[:6],
            }
        )

        if len(out) >= MAX_YUANBAO_ITEMS_PER_CATEGORY:
            break

    return out


def resolve_category_meta(existing: Dict[str, Any], category_id: str, default_name: str, default_desc: str) -> Tuple[str, str]:
    for cat in existing.get("categories", []):
        if normalize_text(cat.get("id")) == category_id:
            name = normalize_text(cat.get("name")) or default_name
            desc = normalize_text(cat.get("description")) or default_desc
            return name, desc
    return default_name, default_desc


def apply_previous_fallback(
    existing: Dict[str, Any],
    category_id: str,
    new_items: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], bool]:
    if new_items:
        return new_items, False
    prev_items = get_existing_category_items(existing, category_id)
    if prev_items:
        return prev_items, True
    return [], False


def build_payload(existing: Dict[str, Any]) -> Dict[str, Any]:
    pubmed_items, pubmed_error = fetch_pubmed_latest()

    daily_news_rss, daily_news_rss_error = fetch_google_news_rss(
        NEWS_QUERY_EN,
        max_items=MAX_RSS_ITEMS_PER_QUERY,
        tags=["news", "innovative drug"],
        any_terms=CORE_DRUG_TERMS,
    )
    industry_rss, industry_rss_error = fetch_google_news_rss(
        INDUSTRY_QUERY_EN,
        max_items=MAX_RSS_ITEMS_PER_QUERY,
        tags=["industry research", "innovative drug"],
        required_groups=[CORE_DRUG_TERMS, INDUSTRY_SIGNAL_TERMS],
    )

    yuanbao_data, yuanbao_meta = fetch_yuanbao_structured_digest()

    daily_items = dedupe_items(
        [
            *yuanbao_data.get("daily_news", []),
            *daily_news_rss,
        ],
        limit=MAX_DAILY_NEWS,
    )
    latest_items = dedupe_items(
        [
            *pubmed_items,
            *yuanbao_data.get("latest_research", []),
        ],
        limit=MAX_LATEST_RESEARCH,
    )
    industry_items = dedupe_items(
        [
            *yuanbao_data.get("industry_research", []),
            *industry_rss,
        ],
        limit=MAX_INDUSTRY_RESEARCH,
    )

    daily_items, daily_fallback = apply_previous_fallback(existing, "daily-news", daily_items)
    latest_items, latest_fallback = apply_previous_fallback(existing, "latest-research", latest_items)
    industry_items, industry_fallback = apply_previous_fallback(existing, "industry-research", industry_items)

    daily_name, daily_desc = resolve_category_meta(
        existing,
        "daily-news",
        "Daily News",
        "Track high-frequency media updates, approvals, policy signals, and readouts.",
    )
    latest_name, latest_desc = resolve_category_meta(
        existing,
        "latest-research",
        "Latest Academic Research",
        "Track newly published or preprint studies with translational relevance.",
    )
    industry_name, industry_desc = resolve_category_meta(
        existing,
        "industry-research",
        "Latest Industry Research",
        "Track strategic reports, financing, licensing, M&A, and pipeline signals.",
    )

    payload = {
        "updated_at": iso_now(),
        "maintainer_note": normalize_text(existing.get("maintainer_note"))
        or "Auto-updated by scripts/update_drug_watch.py. Review entries before decision-making.",
        "watch_keywords": existing.get("watch_keywords") or DEFAULT_WATCH_KEYWORDS,
        "categories": [
            {
                "id": "daily-news",
                "name": daily_name,
                "description": daily_desc,
                "items": daily_items,
            },
            {
                "id": "latest-research",
                "name": latest_name,
                "description": latest_desc,
                "items": latest_items,
            },
            {
                "id": "industry-research",
                "name": industry_name,
                "description": industry_desc,
                "items": industry_items,
            },
        ],
        "sources": existing.get("sources") or DEFAULT_SOURCES,
        "fetch": {
            "window_days": WINDOW_DAYS,
            "pubmed": {
                "query": PUBMED_QUERY,
                "count": len(pubmed_items),
                "error": pubmed_error,
            },
            "google_news": {
                "daily_query": NEWS_QUERY_EN,
                "daily_count": len(daily_news_rss),
                "daily_error": daily_news_rss_error,
                "industry_query": INDUSTRY_QUERY_EN,
                "industry_count": len(industry_rss),
                "industry_error": industry_rss_error,
            },
            "yuanbao": yuanbao_meta,
            "fallback": {
                "daily_news_used_previous": daily_fallback,
                "latest_research_used_previous": latest_fallback,
                "industry_research_used_previous": industry_fallback,
            },
        },
    }
    return payload


def main() -> None:
    existing = load_existing()
    payload = build_payload(existing)

    total_items = 0
    for category in payload.get("categories", []):
        total_items += len(category.get("items", []))

    if total_items == 0:
        raise RuntimeError("No items captured for any category; stop to avoid overwriting with empty data.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote: {OUTPUT}")
    print(
        "Counts: "
        f"daily={len(payload['categories'][0]['items'])}, "
        f"research={len(payload['categories'][1]['items'])}, "
        f"industry={len(payload['categories'][2]['items'])}"
    )
    print(
        "Yuanbao: "
        f"enabled={payload['fetch']['yuanbao']['enabled']}, "
        f"error={payload['fetch']['yuanbao']['error']}"
    )


if __name__ == "__main__":
    main()
