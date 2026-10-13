"""D1 regression: conditions, provenance, authorization and explicit partiality."""
import copy,hashlib,json,unittest
from .evidence_delivery import preserving_recall
from .mdcos import est_tokens

class Graph:
    def __init__(self,nodes):self.nodes=nodes;self.reads=[]
    def get(self,id):self.reads.append(id);return copy.deepcopy(self.nodes.get(id))

class DeliveryInvariants(unittest.TestCase):
    def node(self,id='one',body='Archived fact 19; except maintenance=true.',**fm):
        return {'id':id,'content':body,'frontmatter':{'condition_space':{'domain':'probe','time_window':[100,200]},'non_applicable_conditions':['maintenance=true'],'source':{'reference':'first-party','version':'v3'},'created_at':100,'effective_until':300,'verification_state':'unverified','verification_basis':'signed source observation',**fm}}
    def run_delivery(self,nodes=None,budget=1200,**kw):
        nodes=nodes or [self.node()];g=Graph({n['id']:n for n in nodes});original=copy.deepcopy(nodes)
        raw={'pack':[{'id':n['id'],'content':'WRONG CLIPPED CACHE'} for n in nodes],'recent':[]}
        value=preserving_recall(g,raw,'Archived fact',budget_tokens=budget,**kw)
        self.assertEqual(nodes,original);self.assertEqual(g.reads,[n['id'] for n in nodes]);return value
    def test_original_source_and_native_negatives(self):
        n=self.node();v=self.run_delivery([n]);self.assertEqual(v['evidence_status'],'COMPLETE_SELECTED_SOURCES')
        self.assertIn(n['content'],v['text']);self.assertNotIn('WRONG CLIPPED CACHE',v['text'])
        self.assertIn('maintenance=true',v['text']);self.assertIn('signed source observation',v['text'])
        self.assertEqual(v['records'][0]['source_sha256'],hashlib.sha256(n['content'].encode()).hexdigest())
    def test_time_version_and_id_are_traceable(self):
        v=self.run_delivery();self.assertIn('observation_time_window',v['text']);self.assertIn('effective_until',v['text']);self.assertIn('v3',v['text']);self.assertEqual(v['delivered_ids'],['one'])
    def test_partial_source_explicit_not_silent(self):
        n=self.node(body='Archived fact 19\n'+'unrelated background '*300+'\nExcept when emergency=true.')
        v=self.run_delivery([n],max_item_tokens=100);self.assertEqual(v['evidence_status'],'INCOMPLETE');self.assertTrue(v['records'][0]['truncated'])
        self.assertEqual(v['incomplete_ids'],['one'])
    def test_budget_counts_whole_wire_object(self):
        for budget in (40,80,160,300,1200):
            v=self.run_delivery(budget=budget);self.assertLessEqual(est_tokens(json.dumps(v,ensure_ascii=False,separators=(',',':'))),budget)
    def test_budget_below_minimum_is_explicit_error(self):
        with self.assertRaises(ValueError):self.run_delivery(budget=0)
    def test_invalid_budget_types(self):
        for b in (True,2.5,'300',-1):
            with self.assertRaises(ValueError):self.run_delivery(budget=b)
    def test_conflicting_sources_remain_separate(self):
        v=self.run_delivery([self.node('x','Archived fact 19.'),self.node('y','Archived fact 20.')]);self.assertEqual(v['delivered_ids'],['x','y']);self.assertIn('19',v['text']);self.assertIn('20',v['text'])
    def test_empty_is_not_certified_sufficient(self):
        v=preserving_recall(Graph({}),{'pack':[]},'q');self.assertEqual(v['evidence_status'],'INSUFFICIENT');self.assertEqual(v['delivered_ids'],[])
    def test_visibility_loss_does_not_leak_any_source(self):
        v=preserving_recall(Graph({'a':self.node('a','PRIVATE-A')}),{'pack':[{'id':'a'},{'id':'hidden'}]},'q')
        self.assertEqual(v['evidence_status'],'INCOMPLETE');self.assertNotIn('PRIVATE-A',json.dumps(v));self.assertNotIn('hidden',json.dumps(v))
    def test_identity_crypto_metadata_never_copied(self):
        n=self.node(token='RAW-TOKEN-SENTINEL',owner='PRIVATE-OWNER',crypto={'key':'MASTER-SENTINEL'})
        v=self.run_delivery([n]);s=json.dumps(v);self.assertNotIn('RAW-TOKEN-SENTINEL',s);self.assertNotIn('PRIVATE-OWNER',s);self.assertNotIn('MASTER-SENTINEL',s)
    def test_nested_credential_metadata_fails_closed(self):
        n=self.node(source={'reference':'source','api_key':'SECRET-SENTINEL'})
        v=self.run_delivery([n]);self.assertEqual(v['evidence_status'],'INCOMPLETE');self.assertNotIn('SECRET-SENTINEL',json.dumps(v))
    def test_unknown_json_keeps_outer_exception(self):
        body=json.dumps({'source_document':'fact','important_exception':'never in emergency'})
        v=self.run_delivery([self.node(body=body)]);self.assertIn(body,v['text'])
    def test_same_input_same_delivery(self):
        self.assertEqual(self.run_delivery(),self.run_delivery())
    def test_condition_comment_is_not_discarded(self):
        v=self.run_delivery([self.node(state_attributes={'comment':'Only after independent confirmation.'})]);self.assertIn('Only after independent confirmation.',v['text'])
    def test_changed_same_id_is_not_merged(self):
        nodes=iter([self.node(body='first'),self.node(body='second')])
        class Changing:
            def get(self,id):return next(nodes)
        v=preserving_recall(Changing(),{'pack':[{'id':'one'},{'id':'one'}]},'q')
        self.assertEqual(v['evidence_status'],'INCOMPLETE');self.assertIn('same_id',v['reason']);self.assertNotIn('first',v['text'])
    def test_recent_feature_does_not_silently_disappear(self):
        v=preserving_recall(Graph({}),{'pack':[],'recent':[{'text':'RECENT'}]},'q');self.assertEqual(v['evidence_status'],'INCOMPLETE');self.assertIn('recent',v['reason'])

if __name__=='__main__':unittest.main(verbosity=2)
