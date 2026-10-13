"""Offline evidence audit; executes bounded SQL/schema grading, never calls an API."""
from pathlib import Path
import hashlib,json,sys,importlib.util
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parent).resolve()
def read(p):return json.loads(Path(p).read_text('utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
verified={}
for name in ('dataset-freeze.json','A-memory-freeze.json','experiment-code-freeze.json'):
 ledger=read(root/name)['files']
 for rel,digest in ledger.items():assert sha(root/rel)==digest,(name,rel)
 verified[name]=len(ledger)
for original,digest in read(root/'D1-candidate-freeze.json')['files'].items():
 rel=original.replace('\\','/').split('/dsh-memory-round8-20261013/',1)[1]
 assert sha(root/'candidate-source-research'/rel)==digest,rel
spec=importlib.util.spec_from_file_location('round8_external_grader',root/'grade.py')
grader=importlib.util.module_from_spec(spec);spec.loader.exec_module(grader);grader.ROOT=root
main=0;development=0;costs={};violations=[]
for split in ('prospective','smoke'):
 for resultpath in sorted((root/'runs'/split).glob('*/rep-*/*/result.json')):
  r=read(resultpath);base=resultpath.parent;run=read(base/'run.json');run['out']=str(base)
  fresh=grader.grade(run);assert fresh==r['grade'],str(base)
  events=[json.loads(l) for l in (base/'dsh.stdout.jsonl').read_text('utf8').splitlines() if l.startswith('{')]
  usage={k:sum(e.get('usage',{}).get(k,0) for e in events if e.get('type')=='status' and e.get('phase')=='step_end') for k in ('inputTokens','outputTokens','cacheReadTokens','cacheWriteTokens','totalTokens')}
  assert usage==r['usage'],str(base)
  requests=sum(e.get('type')=='status' and e.get('phase')=='step_start' for e in events)
  assert requests==r['model_requests'] and requests<=8
  toolcalls=[e for e in events if e.get('type')=='tool_call'];assert len(toolcalls)<=14
  accepted=[]
  for e in events:
   if e.get('type')!='tool_result' or e.get('status')!='completed':continue
   try:v=json.loads(e.get('result',''))
   except (ValueError,TypeError):continue
   if isinstance(v,dict) and v.get('recorded') is True:accepted.append(e['callId'])
  if (base/'answer.json').exists():
   assert accepted and any(e.get('callId')==accepted[-1] and e.get('input')==read(base/'answer.json') for e in toolcalls)
  if r['arm']!='A':
   a=read(base/'actual-native-arguments.json')
   assert a['budget_tokens']==240 and a['max_item_tokens']==120 and a['k']==4 and a['evidence_budget_tokens']==1200
   assert a['delivery_mode']==('evidence_preserving' if r['arm']=='D1' else 'original')
  payload=(base/'payload-text.txt').read_text('utf8');assert json.loads(payload)==read(base/'visible-memory.json')
  timing=read(base/'delivery-timing.json');assert len(payload)==timing['unicode_codepoints'] and len(payload.encode('utf8'))==timing['utf8_bytes'] and timing['pinned_tokenizer_tokens']<=4096
  if r['arm']=='D1' and read(base/'visible-memory.json').get('evidence_status')=='INCOMPLETE' and fresh['answer'].get('disposition')=='ANSWER':violations.append(str(base.relative_to(root)))
  for config in read(base/'request-configs.json'):assert config['model']=='deepseek-flash' and config['provider']=='deepseek-official'
  assert r['success']==(r['integration_valid'] and not r['timed_out'] and not r['provider_error'] and fresh['passed'])
  if split=='prospective':main+=1;costs[r['arm']]=costs.get(r['arm'],0)+usage['inputTokens']+usage['outputTokens']
  else:development+=1
assert main==144 and development==3
seeded=0
for p in (root/'seed-v2-runs').glob('*/result.json'):
 r=read(p);assert r['success'] and r['usage']['totalTokens']==0
 receipt=read(p.parent/'A-write-readback.json');assert receipt['passed'] and receipt['no_model_API']
 for record in receipt['records']:assert record['stored']['content']
 seeded+=1
assert seeded==27
analysis=read(root/'analysis.json')
assert costs=={arm:v['uncached_input_plus_output'] for arm,v in analysis['arms'].items()}
assert len(violations)==analysis['arms']['D1']['caller_incomplete_violations']==1
raw_sessions=len(list(root.rglob('dsh.stdout.jsonl')))
print(json.dumps({'passed':True,'main_model_trials_regraded':main,'development_trials_regraded':development,'successful_zero_API_seed_sessions':seeded,'raw_DSH_attempt_logs':raw_sessions,'freezes_verified':verified,'uncached_costs_verified':costs,'preserved_caller_INCOMPLETE_violations':violations,'API_calls':0,'scope':'Original scoring unchanged; known safety violation retained. Bundled evaluation runtime is Windows CPython 3.12; other platforms need pinned dependencies.'},ensure_ascii=False))
