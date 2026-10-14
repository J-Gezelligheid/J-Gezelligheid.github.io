#!/usr/bin/env python3
"""Fetch candidates, then apply reviewed selections. Never prints credentials or raw errors."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / 'scripts/frontier_plan.json').read_text(encoding='utf-8'))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def text(value):
    return value.strip() if isinstance(value, str) else ''


def safe_url(value):
    value = text(value)
    p = urlparse(value)
    return value if p.scheme in ('https', 'http') and p.netloc and not p.username and not p.password else ''


def normalize(item, topic, stamp):
    if not item.get('paper_key') or not text(item.get('title_en')):
        raise ValueError('Missing paper identifier/title')
    if item.get('source_lane') not in ('formal', 'external_authority', 'working'):
        raise ValueError('Unknown evidence lane')
    if not isinstance(item.get('year'), int) or not 1900 <= item['year'] <= int(stamp[:4]):
        raise ValueError('Invalid publication year')
    if not isinstance(item.get('authors'), list):
        raise ValueError('Invalid authors')
    publication_date = text(item.get('publication_date'))
    if publication_date:
        datetime.fromisoformat(publication_date)
        if publication_date[:10] > stamp[:10]:
            raise ValueError('Future publication date needs review')
    doi = text(item.get('doi'))
    if doi and not re.fullmatch(r'10\.\d{4,9}/[^\s<>"\\]+', doi):
        doi = ''
    return {
        'paper_key': item['paper_key'], 'title_en': text(item.get('title_en')),
        'title_zh': text(item.get('title_cn')), 'authors': [text(x) for x in item.get('authors', []) if text(x)],
        'journal': text(item.get('journal')), 'year': item.get('year'),
        'date': text(item.get('publication_date')), 'doi': doi,
        'url': safe_url(item.get('source_url')) or ('https://doi.org/' + doi if doi else ''),
        'source_id': text(item.get('source_id')), 'source_lane': item['source_lane'],
        'abstract_en': text(item.get('abstract_en')), 'summary_zh': text(item.get('summary_cn')),
        'topic': topic, 'retrieved_at': stamp, 'source': 'TopSight',
        'match_level': text(item.get('match_level')),
    }


def merge(previous, batch, selections):
    """Only replace explicitly reviewed nonempty groups; failed/empty groups keep old dates."""
    stamp = batch['retrieved_at']
    datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    if selections.get('reviewed') is not True:
        raise ValueError('Selection must be reviewed before applying')
    queries = batch['queries']
    candidates = {}
    statuses = []
    for q in queries:
        response = q['response']
        lanes = response.get('lanes', {}) if response.get('ok') else {}
        statuses.append({'term': q['topic'], 'journal':q.get('request', {}).get('journal', q.get('request', {}).get('filters', {}).get('journal', '')), 'lanes': {
            lane: {'status': result.get('status', 'failed'), 'count': len(result.get('items', [])),
                   'error': result.get('error', {}).get('code', ''),
                   'bounded': bool(result.get('candidate_pool_truncated'))}
            for lane, result in lanes.items()}, 'ok': bool(response.get('ok'))})
        for lane, result in lanes.items():
            if result.get('status') != 'complete':
                continue
            for p in result.get('items', []):
                if p.get('source_lane') != lane:
                    raise ValueError('Lane mismatch')
                candidates[p['paper_key']] = p
    data = copy.deepcopy(previous)
    data['schema_version'] = 2
    data['checked_at'] = stamp
    old_stamp = previous['updated_at']
    if not previous.get('schema_version'):
        for j in data['journals']:
            j['updated_at'] = old_stamp
            j['source'] = 'Crossref / OpenAlex；原站历史快照'
            j['status'] = 'retained'
        data['nber']['updated_at'] = old_stamp
    old_groups = {g['id']: g for g in data.get('working', {}).get('topics', [])}
    groups = []
    identities = set()
    selected_keys = set()
    for topic in PLAN['topics']:
        chosen = selections.get('topics', {}).get(topic['id'], [])
        papers = []
        for key in chosen:
            p = candidates.get(key)
            if not p or p.get('source_lane') != 'working':
                raise ValueError('Selected working paper absent from successful lane')
            normalized = normalize(p, topic['id'], stamp)
            identity = (normalized['doi'] or normalized['title_en']).casefold()
            if identity in identities or key in selected_keys:
                raise ValueError('Duplicate selection across topics')
            identities.add(identity)
            selected_keys.add(key)
            papers.append(normalized)
        if papers:
            groups.append({'id': topic['id'], 'label': topic['label'], 'papers': papers,
                           'updated_at': stamp, 'status': 'updated'})
        elif topic['id'] in old_groups:
            group = copy.deepcopy(old_groups[topic['id']])
            group['status'] = 'retained'
            # Reject accidental overlap with a retained topic as well.
            groups.append(group)
        else:
            groups.append({'id':topic['id'],'label':topic['label'],'papers':[],
                           'updated_at':None,'status':'empty'})
    all_keys = [p['paper_key'] for g in groups for p in g['papers']]
    all_ids = [(p.get('doi') or p['title_en']).casefold() for g in groups for p in g['papers']]
    if len(all_keys) != len(set(all_keys)) or len(all_ids) != len(set(all_ids)):
        raise ValueError('Duplicate with retained section')
    for i, journal in enumerate(data['journals']):
        chosen = selections.get('journals', {}).get(PLAN['journals'][i], [])
        if not chosen:
            journal['status'] = 'retained'
            continue
        papers = []
        for key in chosen:
            p = candidates.get(key)
            if not p or p.get('source_lane') not in ('formal', 'external_authority'):
                raise ValueError('Journal candidate absent')
            name = text(p.get('journal')).casefold().removeprefix('the ')
            if name != PLAN['journals'][i].casefold().removeprefix('the '):
                raise ValueError('Journal scope mismatch')
            if p.get('source_lane') == 'external_authority' and p.get('match_level') != 'core':
                raise ValueError('External journal selection requires core evidence')
            papers.append(normalize(p, 'journal', stamp))
        journal.update(papers=papers, updated_at=stamp, source='TopSight', status='updated',
                       issue_title='主题检索选文（非完整卷期目录）')
    # Retain non-research entries in data for audit, but do not show as research cards.
    for journal in data['journals']:
        for p in journal['papers']:
            p['is_research'] = not bool(re.search(r'^(front matter|back matter|cover|index|editorial board|table of contents)', p['title_en'], re.I))
    if not any(g['papers'] for g in groups) and not selected_keys:
        raise ValueError('No usable working papers; old file left intact')
    years = [q.get('request', {}).get('year_from', q.get('request', {}).get('filters', {}).get('year_from')) for q in queries]
    start_year = min(y for y in years if isinstance(y, int)) if any(isinstance(y,int) for y in years) else int(stamp[:4])-1
    data['working'] = {'source':'TopSight', 'topics':groups, 'window_note':f'{start_year} 年起的主题检索选文；非当月全部新论文'}
    data['source_checks'] = statuses
    if selected_keys or any(selections.get('journals', {}).values()):
        data['updated_at'] = stamp
    return data


def fetch(output):
    import tomllib
    home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
    config = tomllib.loads((home / 'config.toml').read_text(encoding='utf-8'))['mcp_servers']['topsight-literature']
    sys.path.insert(0, config['cwd'])
    for key in ('TOPSIGHT_API_BASE_URL', 'TOPSIGHT_API_KEY_FILE'):
        os.environ[key] = config['env'][key]
    from topsight_api.mcp_server import TopsightApiClient
    client = TopsightApiClient.from_env()
    usage = client.usage()
    required_calls = len(PLAN['topics']) + len(PLAN['journals'])
    if not usage.get('ok') or usage.get('usage', {}).get('monthly_remaining', 0) < required_calls:
        raise ValueError('Quota unavailable or insufficient')
    now = datetime.now(timezone.utc)
    batch = {'retrieved_at': now.isoformat(), 'queries': []}
    queries = [dict(t) for t in PLAN['topics']]
    queries.extend({'id':journal, 'term':term, 'journal':journal} for journal,term in zip(PLAN['journals'],PLAN['journal_terms']))
    for topic in queries:
        request = {'query':topic['term'], 'terms':[topic['term']], 'corpora':'all', 'mode':'all',
                   'sort':'relevance', 'filters':{'year_from':now.year-1},
                   'limit_per_corpus':PLAN['limit_per_corpus']}
        if topic.get('journal'):
            request['filters']['journal'] = topic['journal']
        response = client.evidence_search(request)
        batch['queries'].append({'topic':topic['term'],'request':request,'response':response})
        write(output, batch)
        print(topic['id'] + ': ' + ('received' if response.get('ok') else 'unavailable'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', type=Path, help='Fetch candidate batch to an ignored .local path')
    parser.add_argument('--batch', type=Path)
    parser.add_argument('--selections', type=Path)
    args = parser.parse_args()
    if args.fetch:
        if not args.fetch.resolve().is_relative_to((ROOT / '.local').resolve()):
            parser.error('Raw candidates must stay in .local')
        fetch(args.fetch)
    else:
        if not args.batch or not args.selections:
            parser.error('--batch and --selections are required')
        target = ROOT / '_data/frontier.json'
        old = read(target)
        data = merge(old, read(args.batch), read(args.selections))
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        write(ROOT / '.local/frontier' / ('before-' + stamp + '.json'), old)
        temp = target.with_suffix('.json.tmp')
        write(temp, data)
        os.replace(temp, target)
        print('Updated Frontier: ' + str(sum(len(g['papers']) for g in data['working']['topics'])) + ' working papers')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Frontier stopped safely: ' + type(exc).__name__, file=sys.stderr)
        raise SystemExit(1) from None
