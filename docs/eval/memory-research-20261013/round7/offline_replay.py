"""Stdlib-only, read-only replay of frozen grades, tool timelines and hashes.

Usage: python -B -X utf8 offline_replay.py <extracted research directory>
No provider key, network, subprocess, graph engine or Memory write is used.
This replays saved evidence; it does not reproduce stochastic model sampling.
"""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text('utf8'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(relative):
    p=(root/relative).resolve()
    if not p.is_relative_to(root):raise ValueError('Path outside research root')
    return p
def events(p):return [json.loads(x) for x in p.read_text('utf8').splitlines() if x.strip()]

checks=0
for ledger in ('dataset-freeze.json','experiment-freeze.json'):
    for rel,sha in load(root/ledger)['files'].items():
        assert digest(inside(rel))==sha,(ledger,rel)
        checks+=1
snap=load(root/'candidate-S1-snapshot-receipt.json')['files']
for original,sha in load(root/'candidate-freeze.json')['files'].items():
    receipt=snap[original]
    assert receipt['sha256']==sha and digest(inside(receipt['snapshot']))==sha,original
    checks+=1

spec=importlib.util.spec_from_file_location('frozen_round7_grade',root/'grade.py')
grader=importlib.util.module_from_spec(spec);spec.loader.exec_module(grader);grader.ROOT=root
counts=collections.Counter();groups=collections.Counter();usage=collections.defaultdict(collections.Counter)
selected=collections.defaultdict(dict);trials=set();submitted_ids=0;argument_rejections=collections.Counter()
recall_rejections=collections.Counter();missing_submissions=collections.Counter()
for path in sorted((root/'runs').rglob('result.json')):
    result=load(path);out=path.parent;run=load(out/'run.json')
    assert run['mode'] in ('smoke','prospective')
    assert 'truth' not in run
    run={**run,'out':str(out)}
    again=grader.grade(run)
    assert again==result['grade'],str(path)
    receipt=load(out/'tool-receipts.json');visible=load(out/'visible-memory.json')
    es=events(out/'dsh.stdout.jsonl');calls=[x for x in es if x.get('type')=='tool_call']
    recalls=[x for x in calls if x['tool']=='memory_recall'];submits=[x for x in calls if x['tool']=='submit_answer']
    assert len(recalls)>=1 and len(receipt)==len(calls),str(path)
    assert receipt[0]['name']=='memory_recall' and receipt[0]['result']==visible
    accepted=[]
    for c,record in zip(calls,receipt):
        assert c['tool']==record['name'] and c['input']==record['args']
        r=next(x for x in es if x.get('type')=='tool_result' and x['callId']==c['callId'])
        assert r['status']=='completed'
        assert json.loads(r['result'])==record['result']
        if c is recalls[0]:assert record['result']==visible
        elif c['tool']=='memory_recall':
            assert record['result']=={'error':'One-retrieval budget already used.','kind':'argument'}
            if result['mode']=='prospective':recall_rejections[result['arm']]+=1
        elif record['result'].get('recorded'):accepted.append(c)
        else:
            # Citation/argument validation may reject a submission; this is not
            # correctness feedback or an API retry. Preserve its actual cost.
            assert record['result'].get('kind')=='argument'
            if result['mode']=='prospective':argument_rejections[result['arm']]+=1
    assert len(accepted)<=1
    if accepted:assert accepted[0]['input']==load(out/'answer.json')
    else:
        assert not (out/'answer.json').exists() and again['answer']=={} and not again['passed']
        if result['mode']=='prospective':missing_submissions[result['arm']]+=1
    assert len(calls)<=run['max_tool_calls'] and result['model_requests']<=run['max_model_requests']
    ids=visible.get('delivered_ids',[x['id'] for x in visible.get('pack',[])])
    if accepted:
        assert set(accepted[0]['input']['evidence_ids'])<=set(ids),str(path)
        submitted_ids+=len(accepted[0]['input']['evidence_ids'])
    u={k:sum(x.get('usage',{}).get(k,0) for x in es if x.get('type')=='status' and x.get('phase')=='step_end') for k in result['usage']}
    assert u==result['usage'] and u['inputTokens']+u['outputTokens']==result['uncached_input_plus_output']
    integration=load(out/'inventory.json')['tools']
    valid=len(integration)==2 and not receipt[0]['result'].get('error')
    success=valid and not result['infrastructure_error'] and not result['timed_out'] and again['passed']
    assert success==result['success'] and result['reflection_events']==0
    identity=(result['mode'],result['task'],result['rep'],result['arm'])
    assert identity not in trials;trials.add(identity);counts[result['mode']]+=1
    if result['mode']=='prospective':
        groups[result['arm']]+=int(success);usage[result['arm']].update(u)
        d=load(out/'delivery-diagnostics.json')
        if result['arm']!='A':selected[result['task'],result['rep']][result['arm']]=(d['candidate_ids'],d['selected_ids'])
assert counts=={'prospective':280,'smoke':5},counts
assert len(selected)==56 and all(len(v)==4 and len({json.dumps(x) for x in v.values()})==1 for v in selected.values())
analysis=load(root/'prospective-analysis.json')
assert groups=={a:g['success'] for a,g in analysis['groups'].items()}
assert all(dict(usage[a])==g['usage'] for a,g in analysis['groups'].items())

native=load(root/'native-DSH-profile-validation.json');native_results=load(root/'native-DSH-profile-results.json')
for r in native['cases']:
    out=root/'native-profile-runs'/r['case'];es=events(out/'dsh.stdout.jsonl')
    call=next(x for x in es if x.get('type')=='tool_call' and x['tool']=='r7_mdcg_recall')
    res=next(x for x in es if x.get('type')=='tool_result' and x['callId']==call['callId'])
    assert res['status']=='completed' and call['input']==r['actual_arguments']
    assert hashlib.sha256(res['result'].encode()).hexdigest()==r['response_sha256']
    value=json.loads(res['result'])
    assert value.get('evidence_status')==r['visible_evidence_status']
    if r['case']=='budget-safe-defer':assert value['pack']==[]
    if r['case']=='preserving-real-source':
        node=value['pack'][0]
        assert hashlib.sha256(node['content'].encode()).hexdigest()==node['source_sha256']
        assert node['metadata']['non_applicable_conditions']
    answer=load(out/'answer.json')
    submit=next(x for x in es if x.get('type')=='tool_call' and x['tool']=='submit_answer')
    assert submit['input']==answer
    assert any(x['case']==r['case'] and x['answer']==answer and x['passed'] for x in native_results['results'])
assert len(native['cases'])==3 and native['engineering_only'] and native['not_in_independent_success_rate']
full=load(root/'stability/verified-full-j5-s710197-result.json')
assert full['passed']==329 and not full['failed'] and len(full['results'])==329 and len(full['skipped'])==3
for record in full['results']:
    # Remap archived absolute log references only; do not execute saved commands.
    log=Path(str(record['log']).replace('\\','/').split('/memory-evidence-round7-20261013/',1)[1])
    assert digest(inside(log))==record['log_sha256'] and record['exit']==0
print(json.dumps({'passed':True,'mode':'read-only saved-evidence replay; no API or Memory writes',
    'frozen_files_verified':checks,'main_sessions':counts['prospective'],'smoke_sessions':counts['smoke'],
    'native_engineering_sessions':len(native['cases']),'total_DSH_sessions':sum(counts.values())+len(native['cases']),
    'strict_regrades_equal':285,'native_tool_timeline_equal':3,'main_success':dict(groups),
    'all_selected_orders_equal':56,'submitted_visible_ID_references':submitted_ids,
    'main_submission_argument_rejections_by_arm':dict(argument_rejections),
    'main_repeated_recall_rejections_by_arm':dict(recall_rejections),
    'main_missing_final_submissions_by_arm':dict(missing_submissions),
    'latest_parallel_logs_verified':329,'unavailable_private_corpus_tests':3,
    'does_not_reproduce_model_sampling':True},ensure_ascii=False,indent=2))
