import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parents[1];sys.path[:0]=[str(ROOT/'workspace'),str(ROOT/'scripts')]
from mine import Mine
class MineRoomTests(unittest.TestCase):
 def test_native_records_conflicts_evaluation_export_reopen(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp));source=m.request('POST','/api/create',{'kind':'source','payload':{'source_key':'fixture','title':'Example source','kind':'fixture','locator':'example:source','access_posture':'manual'}})
   c=m.request('POST','/api/create',{'kind':'candidate','payload':{'candidate_key':'fixture_candidate','source_key':'fixture','title':'Example mechanism','locator':'example:mechanism','candidate_kind':'workflow','summary':'A fixture with an explicit test.','tags':{'mechanism':'Detect first divergence','why_cared':'Avoid repeated wrong fixes','project':'example:current-project'}}})
   p=dict(c['payload']);p['summary']='Revised fixture';r=m.request('POST','/api/save',{**c,'payload':p})
   with self.assertRaises(m.Conflict):m.request('POST','/api/save',{**c,'payload':p})
   e=json.loads((ROOT/'assets'/'evaluation.template.json').read_text());e.update(capability_delta='A bounded fixture delta',evidence=['A supplied fixture, not proven capability'],next_test='Compare the fixture with baseline')
   result=m.request('POST','/api/evaluate',{'candidate_key':'fixture_candidate','evaluation':e});self.assertIn(result['disposition'],{'monitor','reject'})
   self.assertEqual(len(Mine(Path(tmp)).request('POST','/api/list',{})['records']),3)
   self.assertIn(b'ds_record_versions',m.request('POST','/api/export',{})[0])
   self.assertIn('example:current-project',m.request('POST','/api/handoff',{'record_id':c['record_id']})[0])
 def test_workspace_cannot_promote_disposition_or_rewrite_identity(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp));m.request('POST','/api/create',{'kind':'source','payload':{'source_key':'fixture','title':'Fixture','kind':'fixture','locator':'example:source','access_posture':'manual'}})
   c=m.request('POST','/api/create',{'kind':'candidate','payload':{'candidate_key':'bounded','source_key':'fixture','title':'Fixture candidate','locator':'example:candidate','candidate_kind':'workflow','summary':'Not an adoption.'}})
   promoted=dict(c['payload']);promoted['candidate_status']='adopt'
   with self.assertRaisesRegex(ValueError,'evaluation gate'):m.request('POST','/api/save',{**c,'payload':promoted})
   renamed=dict(c['payload']);renamed['candidate_key']='another_identity'
   with self.assertRaisesRegex(ValueError,'identity'):m.request('POST','/api/save',{**c,'payload':renamed})
   relinked=dict(c['payload']);relinked['source_key']='different_source'
   with self.assertRaisesRegex(ValueError,'Source identity'):m.request('POST','/api/save',{**c,'payload':relinked})
   current=m.storage.get_record(m.root,'praxis_mine',c['record_id'])
   self.assertEqual(current['current_version'],c['current_version'])
   self.assertEqual(current['payload']['candidate_status'],'triage')

class LedgerRegressionTests(unittest.TestCase):
 def test_replayed_evaluation_and_reimport_preserve_latest_disposition(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp))
   manifest={'sources':[{'source_key':'s','title':'Source','kind':'fixture','locator':'fixture:s','access_posture':'manual'}], 'candidates':[{'candidate_key':'c','source_key':'s','title':'Candidate','locator':'fixture:c','candidate_kind':'workflow','summary':'A candidate'}]}
   m.request('POST','/api/import',{'text':json.dumps(manifest)})
   first=json.loads((ROOT/'assets'/'evaluation.template.json').read_text())
   first.update(capability_delta='Initial promise',evidence=['fixture:first'],next_test='Compare with baseline',preferred_disposition='pilot')
   first['decision_context']={'baseline':'Manual fixture comparison','comparison':'Synthetic control only; a bounded trial remains needed','rights_status':'not_applicable','rights_basis':'Original fictional mechanism, no third-party material reused','reason':'Try one isolated fixture to resolve whether it improves the baseline'}
   first['positive_scores']={key:5 for key in first['positive_scores']}
   first['risk_scores']={key:0 for key in first['risk_scores']}
   self.assertEqual(m.request('POST','/api/evaluate',{'candidate_key':'c','evaluation':first})['disposition'],'pilot')
   second=json.loads(json.dumps(first));second.update(capability_delta='New disqualifying evidence',evidence=['fixture:second'])
   second['risk_scores']['security']=5
   self.assertEqual(m.request('POST','/api/evaluate',{'candidate_key':'c','evaluation':second})['disposition'],'reject')
   before=next(r for r in m.records() if r['record_type']=='candidate')
   replayed=m.request('POST','/api/evaluate',{'candidate_key':'c','evaluation':first})
   self.assertEqual(replayed['action'],'unchanged')
   self.assertEqual(replayed['current_disposition'],'reject')
   m.request('POST','/api/import',{'text':json.dumps(manifest)})
   after=next(r for r in m.records() if r['record_type']=='candidate')
   self.assertEqual(after['payload']['candidate_status'],'reject')
   self.assertEqual(after['current_version'],before['current_version'])
   self.assertIn('Disposition: **reject**',m.request('POST','/api/report',{})[0])
   export=m.request('POST','/api/export',{})[0]
   rows=[json.loads(line) for line in export.splitlines()]
   self.assertEqual(sum(row.get('table')=='ds_records' for row in rows),6)
   self.assertEqual(sum(row.get('table')=='ds_record_versions' for row in rows),8)

 def test_bad_native_inputs_are_client_errors_without_records(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp))
   for value in ('[]','{"sources":[],"candidates":{}}','{"sources":[{}],"candidates":[]}'):
    with self.subTest(value=value),self.assertRaises(ValueError):m.request('POST','/api/import',{'text':value})
   with self.assertRaises(ValueError):m.request('POST','/api/create',{'kind':'source','payload':{}})
   self.assertEqual(m.records(),[])

 def test_import_rejects_partial_mutation_and_source_relink(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp))
   source={'source_key':'s','title':'Source','kind':'fixture','locator':'fixture:s','access_posture':'manual'}
   candidate={'candidate_key':'c','source_key':'s','title':'Candidate','locator':'fixture:c','candidate_kind':'workflow','summary':'C'}
   bad={'sources':[source], 'candidates':[candidate,{**candidate,'candidate_key':'bad','title':12}]}
   with self.assertRaises(ValueError):m.request('POST','/api/import',{'text':json.dumps(bad)})
   self.assertEqual(m.records(),[])
   m.request('POST','/api/import',{'text':json.dumps({'sources':[source], 'candidates':[candidate]})})
   relink={'sources':[{**source,'source_key':'other','title':'Other'}], 'candidates':[{**candidate,'source_key':'other'}]}
   before=len(m.records())
   with self.assertRaisesRegex(ValueError,'source identity'):m.request('POST','/api/import',{'text':json.dumps(relink)})
   self.assertEqual(len(m.records()),before)
   self.assertEqual(next(r for r in m.records() if r['record_type']=='candidate')['payload']['source_key'],'s')

 def test_invalid_evaluation_shape_does_not_enter_ledger(self):
  with tempfile.TemporaryDirectory() as tmp:
   m=Mine(Path(tmp))
   m.request('POST','/api/create',{'kind':'source','payload':{'source_key':'s','title':'S','kind':'fixture','locator':'fixture:s','access_posture':'manual'}})
   m.request('POST','/api/create',{'kind':'candidate','payload':{'candidate_key':'c','source_key':'s','title':'C','locator':'fixture:c','candidate_kind':'workflow','summary':'C'}})
   template=json.loads((ROOT/'assets'/'evaluation.template.json').read_text())
   template.update(capability_delta='Claim',next_test='Test',evidence='a single string')
   with self.assertRaisesRegex(ValueError,'evidence list'):m.request('POST','/api/evaluate',{'candidate_key':'c','evaluation':template})
   self.assertEqual(len([r for r in m.records() if r['record_type']=='evaluation']),0)
