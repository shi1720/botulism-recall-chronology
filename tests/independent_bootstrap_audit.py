"""Independent raw-record grouping and weighted-order-statistic bootstrap audit.
Does not import analyze.py or read its derived event rows to build the cohort.
"""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import hashlib,json,re,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'data/raw/food-enforcement.json.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='7f8e2b5bd6e05e0cbf15e43860c74538ad09e1f8b07928e9c92de3ead3dac9c6'
with zipfile.ZipFile(archive) as z:records=json.loads(z.read(z.namelist()[0]))['results']
groups=defaultdict(list)
for r in records:
 if '20120101'<=r['recall_initiation_date']<='20251231' and 'botul' in r['reason_for_recall'].lower():groups[r['event_id']].append(r)
assert sum(map(len,groups.values()))==327 and len(groups)==81
rows=[]
for event,rs in sorted(groups.items()):
 start=min(datetime.strptime(r['recall_initiation_date'],'%Y%m%d') for r in rs)
 report=min(datetime.strptime(r['report_date'],'%Y%m%d') for r in rs)
 classes={r['classification'] for r in rs};assert len(classes)==1
 rows.append({'event':event,'class':classes.pop(),'days':(report-start).days,'firm':re.sub('[^a-z0-9]','',rs[0]['recalling_firm'].lower()),'products':len(rs)})
assert len({r['firm'] for r in rows})==79
assert next(r for r in rows if r['event']=='90667')['products']==77
assert sum(r['products'] for r in rows if r['class']=='Class I')==113
primary=[r for r in rows if r['class'] in ['Class I','Class II']]
firms=sorted({r['firm'] for r in primary});assert len(primary)==75 and len(firms)==74
firm_index={x:i for i,x in enumerate(firms)}
by_class={}
for c in ['Class I','Class II']:
 rr=sorted((r for r in primary if r['class']==c),key=lambda r:r['days'])
 by_class[c]=(np.array([r['days'] for r in rr]),np.array([firm_index[r['firm']] for r in rr]))
def weighted_median(days,weights):
 total=int(weights.sum())
 if not total:return None
 cumulative=np.cumsum(weights)
 lo=np.searchsorted(cumulative,(total-1)//2+1);hi=np.searchsorted(cumulative,total//2+1)
 return (float(days[lo])+float(days[hi]))/2
rng=np.random.default_rng(1720406);values=[]
for _ in range(20000):
 counts=np.bincount(rng.integers(len(firms),size=len(firms)),minlength=len(firms));medians=[]
 for c in ['Class I','Class II']:
  days,idx=by_class[c];medians.append(weighted_median(days,counts[idx]))
 if all(m is not None for m in medians):values.append(medians[1]-medians[0])
ci=np.quantile(values,[.025,.975]).tolist();assert ci==[-16.0,19.5],ci
record={'source_records':len(records),'selected_records':327,'events':81,'normalized_firms':79,'primary_events':75,'primary_firms':74,'bootstrap_draws':len(values),'independent_weighted_median_ci':ci,'implementation':'Raw standard-library grouping; frequency-weighted central ranks, no concatenated cluster samples; no import of primary analysis.'}
(ROOT/'results/independent_audit.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
