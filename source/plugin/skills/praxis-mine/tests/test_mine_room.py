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
