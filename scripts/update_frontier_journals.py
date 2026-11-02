"""Refresh verified publisher issues; preserve all other Frontier data. Requires beautifulsoup4."""
import argparse,copy,json,re,os,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def research(t): return not re.match(r'^(front\s?matter|back\s?matter|recent referees|jpe turnaround|editorial|contents|cover)',t.strip(),re.I)
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'personal-homepage-metadata/1.0'}),timeout=45) as r:return r.read().decode('utf-8')
def records(spec,cache,cached):
 key=spec['id'];ps=[]
 if key in ('aer','ecta'):
  filename=cache/('aer.html' if key=='aer' else 'ecta_html.html')
  if not cached: filename.write_text(get(spec['issue_url']),encoding='utf-8')
  soup=BeautifulSoup(filename.read_text(encoding='utf-8'),'html.parser')
  if key=='aer':
   for a in soup.select('article.journal-article[id]'):
    h=a.select_one('h3.title');doi=a.get('id','')
    if h and doi.startswith('10.') and research(h.get_text()):
     ps.append({'title_en':h.get_text(' ',strip=True),'doi':doi,'authors':[x.get_text(' ',strip=True) for x in a.select('.fn.n')]})
  else:
   for h in soup.select('h3.article_title'):
    if not research(h.get_text()):continue
    box=h.find_parent('div',class_='article');link=box.select_one('a[href*="doi="]');doi=urllib.parse.parse_qs(urllib.parse.urlparse(link['href']).query)['doi'][0] if link else ''
    if not doi.startswith('10.'):raise ValueError('Publisher DOI missing')
    p=box.find('p');authors=p.contents[0].strip().split('|') if p else []
    ps.append({'title_en':h.get_text(' ',strip=True),'doi':doi,'authors':authors})
 else:
  filename=cache/(key+'.json')
  if not cached:
   url='https://api.crossref.org/journals/'+spec['issn']+'/works?rows=1000&sort=published&order=desc'
   filename.write_text(get(url),encoding='utf-8')
  raw=load(filename)['message']['items']
  selected=[p for p in raw if str(p.get('volume'))==str(spec['volume']) and str(p.get('issue'))==str(spec['issue']) and research(p.get('title',[''])[0])]
  def page(p):
   m=re.match(r'\d+',p.get('page',''));return int(m[0]) if m else 0
  for p in sorted(selected,key=page):
   ps.append({'title_en':p['title'][0],'doi':p['DOI'],'authors':[' '.join(filter(None,[x.get('given'),x.get('family')])) for x in p.get('author',[])],'pages':p.get('page','')})
 if len(ps)!=spec['expected_count'] or len({p['doi'].lower() for p in ps})!=len(ps):raise ValueError(key+': incomplete/duplicate issue metadata')
 for p in ps:p.update(url='https://doi.org/'+p['doi'],title_zh='',abstract_en='',abstract_zh='',is_research=True,source='Publisher / Crossref',journal=spec['name'],year=spec['year'])
 return ps

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--cached',action='store_true');a=ap.parse_args()
 manifest=load(a.manifest);old=load(ROOT/'_data/frontier.json');data=copy.deepcopy(old);stamp=datetime.now(timezone.utc).isoformat();a.cache.mkdir(parents=True,exist_ok=True)
 if len(manifest['journals'])!=5:raise ValueError('Exactly five verified issues required')
 for j,spec in zip(data['journals'],manifest['journals']):
  if j['name']!=spec['name']:raise ValueError('Journal order mismatch')
  if spec['verified_on']!=datetime.now(timezone.utc).date().isoformat():raise ValueError('Verify publisher issue on this run date; do not reuse old manifest')
  previous=(j.get('year',0),j.get('volume',0),j.get('issue',0))
  if all(previous) and (spec['year'],spec['volume'],spec['issue']) < previous:raise ValueError('Refusing older issue')
  papers=records(spec,a.cache,a.cached)
  j.update(papers=papers,issue_title=f"Volume {spec['volume']}, Issue {spec['issue']} ({spec['month']} {spec['year']})",issue_url=spec['issue_url'],source='出版社卷期核对 / Crossref 目录元数据',updated_at=stamp,checked_at=stamp,status='updated',volume=spec['volume'],issue=spec['issue'],year=spec['year'],toc_scope='research_articles',error=None)
  print(spec['id'],j['issue_title'],len(papers))
 assert data['working']==old['working'] and data['nber']==old['nber']
 data['updated_at']=stamp
 write(a.cache/('before-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.json'),old)
 target=ROOT/'_data/frontier.json';temp=target.with_suffix('.json.tmp');write(temp,data);os.replace(temp,target)
if __name__=='__main__': main()