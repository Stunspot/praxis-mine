"""Consequential local controls; fixtures are fictional, not model performance trials."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'workspace')]
import praxis_mine as native
from mine import Mine

class DecisionCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='praxis-control-')
        self.root=Path(self.temp.name);self.home=self.root/'ledger';self.mine=Mine(self.home);self.store=self.mine.storage
        self.manifest={'sources':[{'source_key':'source','title':'Fictional parser','kind':'local_fixture','locator':'fixture:repo','access_posture':'owner-supplied read-only'}], 'candidates':[{'candidate_key':'parser','source_key':'source','title':'Line parser','locator':'fixture:parser','candidate_kind':'software_tool','summary':'Reports malformed lines instead of truncating them','content_hash':'fixture-revision-one','license':'MIT'}]}
        self.mine.request('POST','/api/import',{'text':json.dumps(self.manifest)})
    def tearDown(self):self.temp.cleanup()
    def evidence(self, preferred='adapt'):
        return {'positive_scores':dict.fromkeys(native.POSITIVE_KEYS,4),'risk_scores':dict.fromkeys(native.RISK_KEYS,0),'preferred_disposition':preferred,'capability_delta':'Expose malformed row number to the user','evidence':['fixture:parse-results — three malformed rows detected; artificial test only'], 'next_test':'Adapt the parser in its canonical owner and run mixed valid/malformed rows; do not deploy until the owner checks error display.', 'decision_context':{'baseline':'Current fictional parser silently omits malformed rows','comparison':'Fictional unit fixture reports all three errors; GUI behavior remains untested','rights_status':'compatible','rights_basis':'Fictional repository LICENSE: MIT, preserve notice in copied parser','reason':'The isolated mechanism fixes an observed loss; whole-package installation adds no useful behavior','owner':'Fixture parser repository','action_scope':'Authorized local adaptation and tests only'},'notes':'No production performance or UI success claimed.'}
    def evaluate(self, value=None):return self.mine.request('POST','/api/evaluate',{'candidate_key':'parser','evaluation':value or self.evidence()})
    def candidate(self):return native.find_record(self.store,self.home,'candidate','candidate_key','parser')
    def test_useful_adaptation_and_handoff_preserve_basis(self):
        result=self.evaluate();self.assertEqual(result['disposition'],'adapt')
        handoff=self.mine.request('POST','/api/handoff',{'record_id':self.candidate()['record_id']})[0]
        for claim in ('three errors','MIT','Fixture parser repository','GUI behavior remains untested','adapt'):self.assertIn(claim,handoff)
        self.assertNotIn(str(self.home),handoff)
    def test_explicit_reject_and_monitor_cannot_be_promoted(self):
        for choice in ('reject','monitor'):
            value=self.evidence(choice);value['positive_scores']=dict.fromkeys(native.POSITIVE_KEYS,5)
            self.assertEqual(self.evaluate(value)['disposition'],choice)
    def test_reject_needs_no_invented_future_test(self):
        value=self.evidence('reject');value['next_test']='';value['decision_context']={};value['capability_delta']='Duplicates the existing parser with no additional outcome'
        self.assertEqual(self.evaluate(value)['disposition'],'reject')
    def test_missing_and_unresolved_rights_cannot_become_actionable(self):
        for change in ({}, {'rights_status':'unresolved'}, {'rights_status':'incompatible'}):
            value=self.evidence();value['decision_context']=change
            self.assertIn(self.evaluate(value)['disposition'],{'monitor','reject'})
    def test_license_filename_is_not_rights_conclusion(self):
        record=self.candidate();record['payload']['license']='LICENSE.md';self.mine.request('POST','/api/save',record)
        self.assertEqual(self.evaluate()['disposition'],'monitor')
    def test_original_idea_can_be_considered_without_copy_license(self):
        record=self.candidate();record['payload']['license']='unknown';self.mine.request('POST','/api/save',record)
        value=self.evidence('pilot');value['decision_context'].update(rights_status='not_applicable',rights_basis='Independently implement the original fixture concept; copy no third-party code or text')
        self.assertEqual(self.evaluate(value)['disposition'],'pilot')
    def test_material_change_stales_evaluation_in_room_report_and_rerun(self):
        first=self.evaluate();self.manifest['candidates'][0]['content_hash']='fixture-revision-two'
        self.mine.request('POST','/api/import',{'text':json.dumps(self.manifest)})
        records=self.mine.request('POST','/api/list',{})['records'];old=next(r for r in records if r['record_type']=='evaluation')
        self.assertFalse(old['current_for_candidate']);self.assertEqual(self.candidate()['payload']['candidate_status'],'triage')
        report=native.report(self.store,self.home);self.assertIn('stale or legacy',report);self.assertIn('Disposition: **triage**',report)
        second=self.evaluate();self.assertNotEqual(first['evaluation_key'],second['evaluation_key'])
    def test_source_locator_change_stales_evidence_but_title_does_not(self):
        self.evaluate();source=native.find_record(self.store,self.home,'source','source_key','source')
        source['payload']['title']='Renamed label';source=self.mine.request('POST','/api/save',source)
        self.assertIsNotNone(native.latest_evaluation(self.store,self.home,'parser'))
        source['payload']['locator']='fixture:other-repo';self.mine.request('POST','/api/save',source)
        self.assertIsNone(native.latest_evaluation(self.store,self.home,'parser'))
    def test_final_import_failure_rolls_back_every_record_and_retry_works(self):
        value={'sources':[{**self.manifest['sources'][0],'source_key':'other'}],'candidates':[{**self.manifest['candidates'][0],'candidate_key':'other','source_key':'other'}]}
        before=self.mine.records();real=native.upsert
        def fail(*args,**kwargs):
            if args[2]=='run':raise RuntimeError('injected final run failure')
            return real(*args,**kwargs)
        with mock.patch.object(native,'upsert',side_effect=fail),self.assertRaisesRegex(ValueError,'final run'):
            self.mine.request('POST','/api/import',{'text':json.dumps(value)})
        self.assertEqual(self.mine.records(),before)
        self.assertEqual(self.mine.request('POST','/api/import',{'text':json.dumps(value)})['counts']['candidates_created'],1)
    def test_final_evaluation_failure_does_not_leave_evidence_or_relation(self):
        before=self.mine.records()
        with mock.patch.object(self.store,'revise_record',side_effect=RuntimeError('injected disposition failure')),self.assertRaisesRegex(ValueError,'disposition failure'):self.evaluate()
        self.assertEqual(self.mine.records(),before)
        self.assertEqual(self.evaluate()['disposition'],'adapt')
    def test_room_create_relation_failure_rolls_back_candidate(self):
        before=self.mine.records();payload={**self.manifest['candidates'][0],'candidate_key':'other'}
        with mock.patch.object(self.store,'add_relation',side_effect=RuntimeError('injected relation failure')),self.assertRaises(ValueError):self.mine.request('POST','/api/create',{'kind':'candidate','payload':payload})
        self.assertEqual(self.mine.records(),before)
    def test_import_cannot_create_admitted_record(self):
        for choice in ('adopt','pilot','reject'):
            value={'sources':[],'candidates':[{**self.manifest['candidates'][0],'candidate_key':'other','candidate_status':choice}]}
            with self.assertRaises(ValueError):self.mine.request('POST','/api/import',{'text':json.dumps(value)})
    def test_get_mutations_and_bad_json_are_controlled(self):
        for action in ('create','save','import','evaluate','export'):
            with self.assertRaisesRegex(ValueError,'POST'):self.mine.request('GET','/api/'+action,{})
        for value in ('{"sources":[],"sources":[],"candidates":[]}','{"sources":[],"candidates":[],"notes":NaN}'):
            with self.assertRaises(ValueError):self.mine.request('POST','/api/import',{'text':value})
        with self.assertRaises(ValueError):self.mine.request('POST','/api/list',[])
    def test_status_and_report_do_not_initialize_a_mistyped_home(self):
        missing=self.root/'misspelled'
        with self.assertRaisesRegex(RuntimeError,'No Praxis ledger'):native.report(self.store,missing)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/praxis_mine.py'),'--data-home',str(missing),'status'],capture_output=True)
        self.assertNotEqual(result.returncode,0);self.assertFalse(missing.exists())
    def test_future_schema_and_corrupt_content_stop_writes(self):
        path=self.store.store_path(self.home,'praxis_mine');candidate_id=self.candidate()['record_id']
        connection=sqlite3.connect(path);connection.execute("UPDATE ds_meta SET value_json='999' WHERE key='substrate_schema_version'");connection.commit();connection.close()
        with self.assertRaisesRegex(ValueError,'unsupported'):self.evaluate()
        connection=sqlite3.connect(path);connection.execute("UPDATE ds_meta SET value_json='1' WHERE key='substrate_schema_version'");connection.execute("UPDATE ds_record_versions SET content_hash='wrong' WHERE record_id=?",(candidate_id,));connection.commit();connection.close()
        with self.assertRaisesRegex(ValueError,'integrity'):self.evaluate()
    def test_logical_export_digest_matches_exact_snapshot_rows(self):
        self.evaluate();raw=self.mine.request('POST','/api/export',{})[0];head,*rows=raw.splitlines(keepends=True);header=json.loads(head)
        self.assertEqual(header['snapshot_sha256'],hashlib.sha256(b''.join(rows)).hexdigest());self.assertNotIn('source_hash',header)
    def test_restore_registration_failure_leaves_no_unregistered_store(self):
        backup=self.store.backup_store(self.home,'praxis_mine',self.root/'backup.sqlite');real=self.store.connect
        class FailingCommit:
            def __init__(self,c):self.c=c
            def __getattr__(self,n):return getattr(self.c,n)
            def commit(self):raise RuntimeError('injected registry commit')
        def connect(path,**kwargs):
            c=real(path,**kwargs)
            return FailingCommit(c) if Path(path).name=='registry.sqlite' and not kwargs.get('read_only') else c
        with mock.patch.object(self.store,'connect',side_effect=connect),self.assertRaisesRegex(RuntimeError,'registry commit'):
            self.store.restore_as_store(self.home,Path(backup['destination']),'restored','probe')
        self.assertFalse(self.store.store_path(self.home,'restored').exists());self.assertNotIn('restored',[r['store_name'] for r in self.store.list_stores(self.home)])
        self.assertTrue(self.store.restore_as_store(self.home,Path(backup['destination']),'restored','probe')['healthy'])
    def test_backup_destination_is_never_overwritten(self):
        path=self.root/'backup.sqlite';path.write_bytes(b'owner data')
        with self.assertRaises(RuntimeError):self.store.backup_store(self.home,'praxis_mine',path)
        self.assertEqual(path.read_bytes(),b'owner data')
    def test_framed_tree_hash_and_unreadable_member(self):
        a=self.root/'a';b=self.root/'b';a.mkdir();b.mkdir();(a/'a').write_bytes(b'bc');(b/'ab').write_bytes(b'c')
        self.assertNotEqual(native.directory_hash(a)[0],native.directory_hash(b)[0])
        real=Path.open
        def denied(path,*args,**kwargs):
            if path==a/'a':raise PermissionError('injected unreadable')
            return real(path,*args,**kwargs)
        with mock.patch.object(Path,'open',denied),self.assertRaises(PermissionError):native.directory_hash(a)
    def test_scan_preserves_owner_tags_and_current_assessment(self):
        scan=self.root/'collection';scan.mkdir();(scan/'SKILL.md').write_text('---\nname: fixture\ndescription: Original fixture mechanism\n---\n')
        native.scan_local(self.store,self.home,scan,'scan','probe');c=next(r for r in self.mine.records() if r['record_type']=='candidate' and r['payload']['source_key']=='scan')
        c['payload']['tags']['project']='fixture:owner';c['payload']['license']='MIT';c=self.mine.request('POST','/api/save',c)
        self.mine.request('POST','/api/evaluate',{'candidate_key':c['payload']['candidate_key'],'evaluation':self.evidence()})
        native.scan_local(self.store,self.home,scan,'scan','probe');current=self.store.get_record(self.home,'praxis_mine',c['record_id'])
        self.assertEqual(current['payload']['tags']['project'],'fixture:owner');self.assertEqual(current['payload']['candidate_status'],'adapt')

    def test_backup_connect_failure_removes_only_our_reservation(self):
        destination=self.root/'failed-backup.sqlite';real=self.store.connect
        def failed(path,**kwargs):
            if Path(path)==destination:raise OSError('injected destination open')
            return real(path,**kwargs)
        with mock.patch.object(self.store,'connect',side_effect=failed),self.assertRaisesRegex(OSError,'destination open'):
            self.store.backup_store(self.home,'praxis_mine',destination)
        self.assertFalse(destination.exists())
    def test_restore_rejects_damaged_record_content_without_registering(self):
        backup=self.root/'damaged.sqlite';self.store.backup_store(self.home,'praxis_mine',backup)
        connection=sqlite3.connect(backup);connection.execute("UPDATE ds_record_versions SET content_hash='damaged'");connection.commit();connection.close()
        with self.assertRaisesRegex(RuntimeError,'content/pointer'):
            self.store.restore_as_store(self.home,backup,'damaged','probe')
        self.assertFalse(self.store.store_path(self.home,'damaged').exists())
    def test_future_registry_is_not_relabelled(self):
        path=self.home/'registry.sqlite';c=sqlite3.connect(path);c.execute("UPDATE ds_registry_meta SET value_json='999' WHERE key='schema_version'");c.commit();c.close()
        with self.assertRaisesRegex(RuntimeError,'unsupported registry'):self.store.initialize_home(self.home)
        c=sqlite3.connect(path);self.assertEqual(c.execute("SELECT value_json FROM ds_registry_meta WHERE key='schema_version'").fetchone()[0],'999');c.close()

if __name__=='__main__':unittest.main()
