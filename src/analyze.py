"""Reproduce the exploratory botulism-hazard enforcement cohort from frozen FDA data."""
from pathlib import Path
import hashlib, json, re, zipfile, warnings
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SEED = 1720406
SEAFOOD = r'\b(?:fish|salmon|tuna|herring|sardine|sardines|mackerel|crab|oyster|oysters|clam|clams|cod|halibut|trout|seafood|caviar|bangus|roach|rudd|bream|capelin|anchov\w*|sturgeon|steelhead)\b'

def cohort(records):
    raw = pd.DataFrame(records)
    for k in ['recall_number','event_id','reason_for_recall','product_description','recalling_firm']:
        assert raw[k].notna().all(), f'Missing {k}'
    dup = raw[raw.duplicated('recall_number', keep=False)]
    if len(dup):
        for _, g in dup.groupby('recall_number'):
            assert all(g[k].nunique(dropna=False) == 1 for k in raw.columns if k != 'openfda')
    raw = raw.drop_duplicates('recall_number').copy()
    raw['start'] = pd.to_datetime(raw.recall_initiation_date, format='%Y%m%d', errors='coerce')
    raw['report'] = pd.to_datetime(raw.report_date, format='%Y%m%d', errors='coerce')
    raw['classified'] = pd.to_datetime(raw.center_classification_date, format='%Y%m%d', errors='coerce')
    eligible = raw.start.between('2012-01-01','2025-12-31')
    selected = raw.loc[eligible & raw.reason_for_recall.str.contains('botul',case=False,regex=False)].copy()
    rows = []
    for event_id, g in selected.groupby('event_id',sort=True):
        assert event_id not in ['', 'N/A']
        assert g.classification.nunique()==1, f'Mixed severity {event_id}'
        assert g.recalling_firm.nunique()==1, f'Mixed firm {event_id}'
        allg = raw.loc[raw.event_id==event_id]
        reason = '\n'.join(sorted(set(g.reason_for_recall)))
        product = '\n'.join(sorted(set(g.product_description)))
        start, report = g.start.min(), g.report.min()
        firm = re.sub(r'[^a-z0-9]','',g.recalling_firm.iloc[0].lower())
        rows.append(dict(event_id=event_id,firm=g.recalling_firm.iloc[0],firm_cluster=firm,
            classification=g.classification.iloc[0], n_products=len(g), n_all_products=len(allg),
            start=start, report=report, classified=g.classified.min(),
            year=start.year, days=(report-start).days,
            max_days=(g.report.max()-start).days,
            all_days=(allg.report.min()-allg.start.min()).days,
            n_start_dates=g.start.nunique(), n_report_dates=g.report.nunique(),
            seafood=bool(re.search(SEAFOOD,product,re.I)),
            mixed_cronobacter=bool(re.search('cronobacter',reason,re.I)),
            reason=reason,product=product))
    return raw, selected, pd.DataFrame(rows)

def interval(k,n):
    lo,hi=proportion_confint(k,n,alpha=.05,method='wilson')
    return [float(lo),float(hi)]

def cluster_bootstrap_difference(d,B=20000):
    rng=np.random.default_rng(SEED)
    groups=[np.column_stack([g.days.to_numpy(),(g.classification=='Class II').to_numpy()])
            for _,g in d.groupby('firm_cluster')]
    # Resample firms; preserve all events within each selected firm.
    vals=[]
    for _ in range(B):
        g=np.concatenate([groups[i] for i in rng.integers(len(groups),size=len(groups))])
        a=g[g[:,1]==0,0]
        b=g[g[:,1]==1,0]
        if len(a) and len(b): vals.append(float(np.median(b)-np.median(a)))
    return dict(draws=len(vals),ci=np.quantile(vals,[.025,.975]).tolist())

def model(d):
    d=d[d.classification.isin(['Class I','Class II']) & d.days.ge(0)].copy()
    d['class_ii']=(d.classification=='Class II').astype(int)
    d['year_c']=d.year-2018
    fit=smf.ols('np.log1p(days) ~ class_ii + year_c + seafood',data=d).fit(
        cov_type='cluster',cov_kwds={'groups':d.firm_cluster,'use_correction':True},use_t=True)
    ci=fit.conf_int().loc['class_ii'].tolist()
    return dict(n=int(fit.nobs),firms=d.firm_cluster.nunique(),ratio=float(np.exp(fit.params['class_ii'])),
        ci=np.exp(ci).tolist(),p=float(fit.pvalues['class_ii']),
        coef=fit.params.to_dict(),condition_number=float(fit.condition_number),
        max_cooks_d=float(fit.get_influence().cooks_distance[0].max()))

def main():
    archive=ROOT/'data/raw/food-enforcement.json.zip'
    with zipfile.ZipFile(archive) as z:
        source=json.loads(z.read(z.namelist()[0]))
    raw, selected, events=cohort(source['results'])
    assert events.days.notna().all()
    events.to_csv(ROOT/'data/derived/events.csv',index=False)
    selected.to_json(ROOT/'data/derived/matching_records.json',orient='records',indent=2,date_format='iso')
    valid=events[events.days.ge(0)].copy()
    out={'source_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'source_meta':source['meta'],
         'raw_records':len(source['results']),'unique_records':len(raw),'matching_records':len(selected),
         'events':len(events),'firms':events.firm_cluster.nunique(),
         'negative_intervals':events.loc[events.days.lt(0),'event_id'].tolist(),
         'multi_start_dates':int(events.n_start_dates.gt(1).sum()),
         'multi_report_dates':int(events.n_report_dates.gt(1).sum()),'classes':{}}
    for c,g in valid.groupby('classification',sort=True):
        q=np.quantile(g.days,[.25,.5,.75])
        out['classes'][c]={'n':len(g),'records':int(g.n_products.sum()),'q':q.tolist(),
            'seafood':int(g.seafood.sum()),'min':int(g.days.min()),'max':int(g.days.max()),
            'windows':{str(t):{'n':int((g.days<=t).sum()),'fraction':float((g.days<=t).mean()),
                'ci':interval(int((g.days<=t).sum()),len(g))} for t in [30,60,90]}}
    d=valid[valid.classification.isin(['Class I','Class II'])]
    a=d.loc[d.classification=='Class I','days'];b=d.loc[d.classification=='Class II','days']
    out['primary']={'median_difference':float(b.median()-a.median()),
        'bootstrap':cluster_bootstrap_difference(d),
        'mann_whitney_p':float(mannwhitneyu(a,b,alternative='two-sided',method='asymptotic').pvalue),
        'adjusted':model(d)}
    variants={'exclude_2012':d[d.year>2012], 'since_2017':d[d.year>=2017],
              'exclude_cronobacter':d[~d.mixed_cronobacter]}
    for name,col in [('latest_report','max_days'),('all_event_records','all_days')]:
        v=d.copy();v['days']=v[col];variants[name]=v
    out['sensitivity']={k:{'adjusted':model(v),'median_difference':float(
        v.loc[v.classification=='Class II','days'].median()-v.loc[v.classification=='Class I','days'].median())}
        for k,v in variants.items()}
    loo=[model(d[d.event_id!=i])['ratio'] for i in d.event_id]
    out['leave_one_out_ratio_range']=[min(loo),max(loo)]
    out['threshold_composition']={str(t):{'n':int((valid.days<=t).sum()),'class_i':int(((valid.days<=t)&(valid.classification=='Class I')).sum())} for t in [30,60,90]}
    out['year_counts']=valid.groupby('year').size().to_dict()
    # Diagnostics and exact membership are saved, not suppressed.
    out['seafood_cross_tab']=pd.crosstab(valid.seafood,valid.classification).to_dict()
    (ROOT/'results/summary.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
    figures(valid,out)
    print(json.dumps(out,indent=2,default=str))

def figures(e,s):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'savefig.dpi':220,'axes.titleweight':'bold'})
    colors={'Class I':'#a33b35','Class II':'#24658a','Class III':'#929ca5'}
    fig,ax=plt.subplots(figsize=(7,3.8))
    for c,g in e.groupby('classification',sort=True):
        x=np.sort(g.days); y=np.arange(1,len(x)+1)/len(x)
        ax.step(x,y,where='post',label=f'{c} (n={len(g)})',color=colors[c],lw=2)
    ax.axvline(30,color='#444444',ls=':',lw=1)
    ax.set(xlabel='Recorded initiation-to-report interval (days; logarithmic scale)',ylabel='Cumulative proportion of events',ylim=(0,1.03),xlim=(15,2200),xscale='log')
    ax.set_xticks([20,30,60,90,180,365,730,2000],labels=['20','30','60','90','180','365','730','2000'])
    ax.legend(frameon=False,loc='lower right'); ax.grid(alpha=.15);fig.tight_layout()
    fig.savefig(ROOT/'figures/01_intervals.png');fig.savefig(ROOT/'figures/01_intervals.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7,3.5))
    for c,g in e.groupby('classification',sort=True):
        k=['Class I','Class II','Class III'].index(c)
        rng=np.random.default_rng(SEED+k)
        axes[0].scatter(k+rng.uniform(-.18,.18,len(g)),g.days,s=18,color=colors[c],alpha=.7)
        q=np.quantile(g.days,[.25,.5,.75]);axes[0].plot([k,k],[q[0],q[2]],color='black',lw=3)
        axes[0].plot([k-.18,k+.18],[q[1],q[1]],color='black',lw=2)
    axes[0].set(xticks=[0,1,2],xticklabels=['Class I','Class II','Class III'],ylabel='Interval (days; log scale)',yscale='log',title='A  Event intervals')
    ts=[30,60,90];x=np.arange(3)
    for idx,c in enumerate(['Class I','Class II']):
        vals=[s['classes'][c]['windows'][str(t)] for t in ts];p=np.array([v['fraction'] for v in vals]);ci=np.array([v['ci'] for v in vals])
        axes[1].errorbar(x+(idx-.5)*.15,p,yerr=np.array([p-ci[:,0],ci[:,1]-p]),marker='o',capsize=3,label=c,color=colors[c])
    axes[1].set(xticks=x,xticklabels=[str(t) for t in ts],xlabel='Interval threshold (days)',ylabel='Proportion at or below threshold',ylim=(0,1.03),title='B  Threshold summaries')
    axes[1].legend(frameon=False);fig.tight_layout();fig.savefig(ROOT/'figures/02_thresholds.png');fig.savefig(ROOT/'figures/02_thresholds.pdf');plt.close(fig)
    labels=['Events','Product entries','Events\n<=30 days','Events\n<=60 days','Events\n<=90 days'];totals=[len(e),e.n_products.sum()]+[s['threshold_composition'][str(t)]['n'] for t in ts]
    fig,ax=plt.subplots(figsize=(7,3.5));bottom=np.zeros(5)
    for c in ['Class I','Class II','Class III']:
        counts=[int((e.classification==c).sum()),int(e.loc[e.classification==c,'n_products'].sum())]+[int(((e.classification==c)&(e.days<=t)).sum()) for t in ts]
        v=np.array(counts)/totals*100
        ax.bar(np.arange(5),v,bottom=bottom,color=colors[c],label=c,width=.65)
        for i,(n,p) in enumerate(zip(counts,v)):
            if p>8:ax.text(i,bottom[i]+p/2,f'{n}\n({p:.0f}%)',ha='center',va='center',color='white',fontsize=9)
        bottom+=v
    ax.set(xticks=np.arange(5),xticklabels=labels,ylabel='Composition (%)',ylim=(0,101))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.17),ncol=3,frameon=False)
    fig.tight_layout();fig.savefig(ROOT/'figures/03_composition.png');fig.savefig(ROOT/'figures/03_composition.pdf');plt.close(fig)

if __name__=='__main__': main()
