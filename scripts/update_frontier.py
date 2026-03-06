#!/usr/bin/env python3
"""Update _data/frontier.json for journal TOC + NBER weekly papers with Kimi translation."""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "frontier.json"

HEADERS = {
    "User-Agent": "academic-frontier-bot/1.0 (mailto:jincaiqi@ucass.edu.cn)",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
}
TIMEOUT = 25

KIMI_API_BASE = os.getenv("KIMI_API_BASE", "https://api.moonshot.cn/v1").rstrip("/")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "").strip()
KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
KIMI_MIN_INTERVAL_SECONDS = float(os.getenv("KIMI_MIN_INTERVAL_SECONDS", "3.2"))
MAX_ABSTRACT_TRANSLATE_CHARS = int(os.getenv("MAX_ABSTRACT_TRANSLATE_CHARS", "2500"))
MAX_PAPERS_PER_JOURNAL = int(os.getenv("MAX_PAPERS_PER_JOURNAL", "12"))
MAX_NBER_PAPERS = int(os.getenv("MAX_NBER_PAPERS", "30"))

JOURNALS = [
    {
        "name": "American Economic Review (AER)",
        "issn": "0002-8282",
        "issue_url": "https://www.aeaweb.org/journals/aer",
    },
    {
        "name": "Journal of Political Economy (JPE)",
        "issn": "0022-3808",
        "issue_url": "https://www.journals.uchicago.edu/journals/jpe",
    },
    {
        "name": "Quarterly Journal of Economics (QJE)",
        "issn": "0033-5533",
        "issue_url": "https://academic.oup.com/qje",
    },
    {
        "name": "Review of Economic Studies (REStud)",
        "issn": "0034-6527",
        "issue_url": "https://academic.oup.com/restud",
    },
    {
        "name": "Econometrica",
        "issn": "0012-9682",
        "issue_url": "https://onlinelibrary.wiley.com/journal/14680262",
    },
]

NBER_API_URL = "https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_html_text(text: str) -> str:
    if not text:
        return ""
    content = unescape(text)
    soup = BeautifulSoup(content, "lxml")
    return normalize_text(soup.get_text(" ", strip=True))


def trim_for_translation(text: str, max_chars: int = MAX_ABSTRACT_TRANSLATE_CHARS) -> str:
    if not text:
        return ""
    s = normalize_text(text)
    if len(s) <= max_chars:
        return s
    return s[:max_chars].rsplit(" ", 1)[0] + " ..."


def fetch_json(url: str, params: Optional[Dict] = None) -> Dict:
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def safe_title(item: Dict) -> str:
    title = item.get("title", "")
    if isinstance(title, list):
        return normalize_text(title[0] if title else "")
    return normalize_text(title)


def extract_doi_from_url(url: str) -> str:
    m = re.search(r"https?://doi\.org/(.+)", url, flags=re.I)
    return m.group(1).strip() if m else ""


def openalex_abstract_from_doi_url(doi_url: str) -> str:
    doi = extract_doi_from_url(doi_url)
    if not doi:
        return ""

    api_url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    try:
        payload = fetch_json(api_url)
    except Exception:
        return ""

    inverted = payload.get("abstract_inverted_index")
    if not inverted:
        return ""

    words: Dict[int, str] = {}
    max_pos = -1
    for token, positions in inverted.items():
        for p in positions:
            try:
                pi = int(p)
            except Exception:
                continue
            words[pi] = token
            max_pos = max(max_pos, pi)

    if max_pos < 0:
        return ""

    sentence = " ".join(words.get(i, "") for i in range(max_pos + 1))
    return normalize_text(sentence)


def clean_translation_output(text: str) -> str:
    s = normalize_text(text)
    if not s:
        return ""

    s = re.sub(r"^(Type|类型)\s*[:：].{0,60}(Text|文本)\s*[:：]\s*", "", s, flags=re.I)
    s = re.sub(r"^(Translation|译文|翻译)\s*[:：]\s*", "", s, flags=re.I)
    s = s.strip("\"'“”")
    return normalize_text(s)


class KimiTranslator:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.enabled = bool(api_key)
        self.cache: Dict[str, str] = {}
        self.success_count = 0
        self.fail_count = 0
        self.fail_samples: List[str] = []
        self._last_call_ts = 0.0

    def warmup_cache(self, old_data: Dict) -> None:
        if not old_data:
            return

        def add_pair(en_text: str, zh_text: str) -> None:
            src = normalize_text(en_text)
            tgt = normalize_text(zh_text)
            if src and tgt:
                self.cache[src] = tgt

        for journal in old_data.get("journals", []):
            for paper in journal.get("papers", []):
                add_pair(paper.get("title_en") or paper.get("title"), paper.get("title_zh"))
                add_pair(paper.get("abstract_en"), paper.get("abstract_zh"))

        for paper in old_data.get("nber", {}).get("papers", []):
            add_pair(paper.get("title_en") or paper.get("title"), paper.get("title_zh"))
            add_pair(paper.get("abstract_en"), paper.get("abstract_zh"))

    def _record_failure(self, source: str, msg: str) -> None:
        self.fail_count += 1
        if len(self.fail_samples) < 6:
            self.fail_samples.append(f"{source[:80]} :: {msg[:160]}")

    def _respect_rate_limit(self) -> None:
        if KIMI_MIN_INTERVAL_SECONDS <= 0:
            return
        now = time.time()
        wait_s = KIMI_MIN_INTERVAL_SECONDS - (now - self._last_call_ts)
        if wait_s > 0:
            time.sleep(wait_s)

    def translate(self, text: str, kind: str = "text") -> str:
        source = normalize_text(text)
        if not source:
            return ""

        if source in self.cache:
            return self.cache[source]

        if not self.enabled:
            return ""

        user_prompt = (
            "Translate the following English content into Simplified Chinese. "
            "Keep economic terminology precise. Output translation only.\n\n"
            f"Type: {kind}\n"
            f"Text:\n{source}"
        )

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional economics translator.",
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(4):
            try:
                self._respect_rate_limit()
                resp = requests.post(
                    f"{KIMI_API_BASE}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=90,
                )
                self._last_call_ts = time.time()

                if resp.status_code >= 400:
                    raise requests.HTTPError(f"HTTP {resp.status_code}")

                data = resp.json()
                translated = clean_translation_output(data["choices"][0]["message"]["content"])
                if not translated:
                    raise ValueError("Empty translation")

                self.cache[source] = translated
                self.success_count += 1
                return translated
            except Exception as exc:
                if attempt < 3:
                    time.sleep(2 * (attempt + 1))
                else:
                    self.cache[source] = ""
                    self._record_failure(source, str(exc))
                    return ""

        return ""


def build_journal_block(journal: Dict, translator: KimiTranslator) -> Dict:
    api = f"https://api.crossref.org/journals/{journal['issn']}/works"
    result = {
        "name": journal["name"],
        "issue_title": "Latest issue (Crossref)",
        "issue_url": journal["issue_url"],
        "papers": [],
        "error": None,
    }

    try:
        payload = fetch_json(
            api,
            params={
                "sort": "published",
                "order": "desc",
                "rows": 120,
                "select": "title,URL,volume,issue,type,abstract",
            },
        )
        items = payload.get("message", {}).get("items", [])

        latest_volume = None
        latest_issue = None
        for it in items:
            if it.get("type") != "journal-article":
                continue
            if it.get("volume") and it.get("issue"):
                latest_volume = str(it.get("volume"))
                latest_issue = str(it.get("issue"))
                break

        picked = []
        for it in items:
            if it.get("type") != "journal-article":
                continue

            title_en = safe_title(it)
            url = normalize_text(it.get("URL", ""))
            if not title_en or not url:
                continue

            if latest_volume and latest_issue:
                if str(it.get("volume", "")) != latest_volume or str(it.get("issue", "")) != latest_issue:
                    continue

            abstract_en = strip_html_text(it.get("abstract", ""))
            if not abstract_en:
                abstract_en = openalex_abstract_from_doi_url(url)
            abstract_en = normalize_text(abstract_en)

            title_zh = translator.translate(title_en, kind="title")
            abstract_zh = translator.translate(trim_for_translation(abstract_en), kind="abstract") if abstract_en else ""

            picked.append(
                {
                    "title_en": title_en,
                    "title_zh": title_zh,
                    "url": url,
                    "abstract_en": abstract_en,
                    "abstract_zh": abstract_zh,
                }
            )

            if len(picked) >= MAX_PAPERS_PER_JOURNAL:
                break

        if latest_volume and latest_issue:
            result["issue_title"] = f"Volume {latest_volume}, Issue {latest_issue}"
        result["papers"] = picked

    except Exception as exc:
        result["error"] = str(exc)

    return result


def build_nber_block(translator: KimiTranslator) -> Dict:
    result = {
        "source": NBER_API_URL,
        "window_days": 7,
        "papers": [],
        "error": None,
    }

    try:
        payload = fetch_json(NBER_API_URL)
        papers = []
        for it in payload.get("results", []):
            if not it.get("newthisweek"):
                continue

            url = normalize_text(it.get("url", ""))
            if url.startswith("/"):
                url = f"https://www.nber.org{url}"

            title_en = normalize_text(it.get("title", ""))
            abstract_en = normalize_text(it.get("abstract", ""))
            if not title_en or not url:
                continue

            pid = ""
            if "/papers/" in url:
                pid = url.split("/papers/")[-1].split("?")[0].upper()

            title_zh = translator.translate(title_en, kind="title")
            abstract_zh = translator.translate(trim_for_translation(abstract_en), kind="abstract") if abstract_en else ""

            papers.append(
                {
                    "id": pid or "NBER",
                    "title_en": title_en,
                    "title_zh": title_zh,
                    "url": url,
                    "date": normalize_text(it.get("displaydate", "")),
                    "abstract_en": abstract_en,
                    "abstract_zh": abstract_zh,
                }
            )

            if len(papers) >= MAX_NBER_PAPERS:
                break

        result["papers"] = papers

    except Exception as exc:
        result["error"] = str(exc)

    return result


def load_previous_data() -> Dict:
    if not OUTPUT.exists():
        return {}
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    previous = load_previous_data()
    translator = KimiTranslator(api_key=KIMI_API_KEY, model=KIMI_MODEL)
    translator.warmup_cache(previous)

    journals = [build_journal_block(j, translator) for j in JOURNALS]
    nber = build_nber_block(translator)

    payload = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "translation": {
            "engine": "kimi",
            "model": KIMI_MODEL,
            "enabled": translator.enabled,
            "success_count": translator.success_count,
            "fail_count": translator.fail_count,
            "failed_examples": translator.fail_samples,
            "note": "Set KIMI_API_KEY to enable Chinese translation.",
        },
        "journals": journals,
        "nber": nber,
    }

    if translator.enabled and translator.success_count == 0:
        raise RuntimeError(
            "Kimi translation is enabled but no translation succeeded. "
            f"Failures: {translator.fail_samples[:2]}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {OUTPUT}")
    print(
        "Translation stats: "
        f"enabled={translator.enabled}, success={translator.success_count}, fail={translator.fail_count}"
    )


if __name__ == "__main__":
    main()
