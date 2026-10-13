#!/usr/bin/env python3
"""Offline checks for homepage data and referenced local assets. No network/writes."""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path, today: date) -> dict:
    report = {"as_of": today.isoformat(), "errors": [], "warnings": [], "counts": {}}

    def error(message):
        report["errors"].append(message)

    def warn(message):
        report["warnings"].append(message)

    def obj(value, label):
        if not isinstance(value, dict):
            error(f"{label}: expected object")
            return {}
        return value

    def array(value, label):
        if not isinstance(value, list):
            error(f"{label}: expected array")
            return []
        return value

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def check_url(value, label):
        if not nonempty(value):
            warn(f"{label}: missing source URL")
            return
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            error(f"{label}: expected HTTP(S) URL")

    def load(name):
        try:
            data = obj(json.loads((root / "_data" / f"{name}.json").read_text(encoding="utf-8")), name)
        except (OSError, ValueError) as exc:
            error(f"{name}: {type(exc).__name__}")
            return {}
        try:
            stamp = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            age = (today - stamp.date()).days
            if age > 7:
                warn(f"{name}: snapshot is {age} days old ({stamp.date()})")
            if age < 0:
                warn(f"{name}: future update date")
        except (KeyError, TypeError, ValueError, AttributeError):
            error(f"{name}: invalid updated_at")
        return data

    def records(items, label, paper=False):
        items = array(items, label)
        report["counts"][label] = len(items)
        if not items:
            warn(f"{label}: empty list")
        seen = set()
        missing = {key: 0 for key in ("title_zh", "abstract_en", "abstract_zh")} if paper else {}
        for index, raw in enumerate(items):
            item_label = f"{label}[{index}]"
            item = obj(raw, item_label)
            title = item.get("title_en") or item.get("title") if paper else item.get("title")
            if not nonempty(title):
                error(f"{item_label}: missing title")
            check_url(item.get("url"), item_label)
            identity = item.get("url") or title
            if isinstance(identity, str):
                identity = identity.strip().casefold()
                if identity in seen:
                    warn(f"{item_label}: duplicate URL/title in this section")
                seen.add(identity)
            if paper:
                for key in missing:
                    missing[key] += not nonempty(item.get(key))
            else:
                for key in ("source", "summary"):
                    if not nonempty(item.get(key)):
                        warn(f"{item_label}: missing {key}")
                try:
                    date.fromisoformat(item["date"])
                except (KeyError, TypeError, ValueError):
                    error(f"{item_label}: date must be YYYY-MM-DD")
                tags = array(item.get("tags", []), f"{item_label}.tags")
                if any(not isinstance(tag, str) for tag in tags):
                    error(f"{item_label}: tags must contain strings")
        for key, count in missing.items():
            if count:
                warn(f"{label}: {count} records missing {key}")

    def inspect_status(value, label):
        if not isinstance(value, dict):
            return
        for key, child in value.items():
            if (key == "error" or key.endswith("_error")) and child:
                warn(f"{label}.{key}: source reported an error; inspect data locally")
            elif key.endswith("used_previous") and child:
                warn(f"{label}.{key}: previous data reused")
            elif isinstance(child, dict):
                inspect_status(child, f"{label}.{key}")

    drug = load("drug_watch")
    categories = array(drug.get("categories"), "drug_watch.categories")
    ids = []
    for index, raw in enumerate(categories):
        category = obj(raw, f"drug_watch.categories[{index}]")
        cid = category.get("id")
        if not isinstance(cid, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", cid):
            error(f"drug_watch.categories[{index}]: invalid anchor id")
        else:
            ids.append(cid)
        records(category.get("items"), f"drug_watch.{cid}")
    if set(ids) != {"daily-news", "latest-research", "industry-research"} or len(ids) != 3:
        error("drug_watch: expected three distinct category IDs")
    inspect_status(drug.get("fetch"), "drug_watch.fetch")

    frontier = load("frontier")
    for index, raw in enumerate(array(frontier.get("journals"), "frontier.journals")):
        journal = obj(raw, f"frontier.journals[{index}]")
        label = f"frontier.{journal.get('name', index)}"
        records(journal.get("papers"), label, paper=True)
        inspect_status(journal, label)
    nber = obj(frontier.get("nber"), "frontier.nber")
    records(nber.get("papers"), "frontier.nber", paper=True)
    inspect_status(nber, "frontier.nber")
    translation = obj(frontier.get("translation"), "frontier.translation")
    if translation.get("fail_count"):
        warn("frontier.translation: translation failures recorded")

    for name, key in (("drug-watch.md", "drug_watch"), ("frontier.md", "frontier")):
        try:
            page = (root / name).read_text(encoding="utf-8")
            if f"site.data.{key}" not in page:
                error(f"{name}: expected data binding absent")
            for asset in re.findall(r'(?:href|src)="(/assets/[^"?#]+)', page):
                if not (root / asset.lstrip("/")).is_file():
                    error(f"{name}: missing local asset {asset}")
        except OSError:
            error(f"{name}: page missing")
    for script in (root / "scripts").glob("*.py"):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=script.name)
        except (OSError, SyntaxError) as exc:
            error(f"{script.name}: {type(exc).__name__}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args()
    report = validate(ROOT, args.as_of)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
