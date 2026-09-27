import json,tempfile,threading,uuid
from pathlib import Path
import praxis_mine as native
from runtime import atomic
class Mine:
    class Conflict(ValueError):pass
    def __init__(self,root):
        self.root=root;self.storage=native.load_storage();self.lock=threading.RLock();native.ensure_store(self.storage,root,'praxis-room')
    def records(self):return self.storage.list_records(self.root,'praxis_mine',status=None)
    def request(self,method,path,data):
        with self.lock:
            if path=='/api/list':return {'records':self.records(),'data_root':str(self.root)}
            if path=='/api/history':return {'history':self.storage.record_history(self.root,'praxis_mine',data['record_id'])}
            if path=='/api/save':
                if method!='POST':raise ValueError('POST required')
                record=self.storage.get_record(self.root,'praxis_mine',data['record_id'])
                if record['record_type'] not in {'candidate','source','run'}:raise ValueError('Evaluations are evidence records; use a new native evaluation')
                payload=data['payload']
                key=record['record_type']+'_key'
                if payload.get(key)!=record['payload'].get(key):raise ValueError('Record identity cannot change')
                if record['record_type']=='candidate':
                    if payload.get('source_key')!=record['payload'].get('source_key'):raise ValueError('Source identity cannot change on an existing finding; preserve its provenance trail')
                    if payload.get('candidate_status')!=record['payload'].get('candidate_status'):raise ValueError('Disposition changes require the native evaluation gate')
                    if native.find_record(self.storage,self.root,'source','source_key',payload['source_key']) is None:raise ValueError('Unknown source')
                try:result=self.storage.revise_record(self.root,'praxis_mine',data['record_id'],payload,'praxis-room','supplied',{'route':'local-workspace'},'owner room edit',expected_version=data['current_version'])
                except self.storage.SubstrateError as e:
                    if 'conflict' in str(e):raise self.Conflict(str(e))
                    raise ValueError(str(e))
                return result
            if path=='/api/create':
                kind=data['kind'];payload=data['payload']
                if kind=='source':payload=native.normalize_source(payload)
                elif kind=='candidate':
                    payload=native.normalize_candidate(payload)
                    if payload['candidate_status']!='triage':raise ValueError('New candidates begin in triage')
                    if native.find_record(self.storage,self.root,'source','source_key',payload['source_key']) is None:raise ValueError('Record a source first')
                else:raise ValueError('Create sources or candidates; imports record runs and evaluations use their gate')
                key=kind+'_key'
                if native.find_record(self.storage,self.root,kind,key,payload[key]):raise ValueError('Identity exists; edit its current record')
                result,_=native.upsert(self.storage,self.root,kind,key,payload,'praxis-room',{'route':'local-workspace'},'supplied')
                if kind=='candidate':
                    source=native.find_record(self.storage,self.root,'source','source_key',payload['source_key'])
                    self.storage.add_relation(self.root,'praxis_mine','source_contains_candidate',source['record_id'],result['record_id'],'praxis-room',{'route':'local-workspace'})
                return result
            if path=='/api/import':
                text=data['text'];manifest=json.loads(text)
                if not isinstance(manifest.get('sources'),list) or not isinstance(manifest.get('candidates'),list):raise ValueError('Native manifest needs sources and candidates arrays')
                sources={r['payload']['source_key'] for r in self.records() if r['record_type']=='source'}
                for s in manifest['sources']:sources.add(native.normalize_source(s)['source_key'])
                for c in manifest['candidates']:
                    if native.normalize_candidate(c)['source_key'] not in sources:raise ValueError('Candidate references an unknown source')
                file=self.root/'.workspace'/'imports'/(uuid.uuid4().hex+'.json');atomic(file,text)
                return native.ingest_manifest(self.storage,self.root,file,'praxis-room')
            if path=='/api/evaluate':
                file=self.root/'.workspace'/'evaluations'/(uuid.uuid4().hex+'.json');atomic(file,json.dumps(data['evaluation']))
                try:return native.evaluate(self.storage,self.root,data['candidate_key'],file,'praxis-room')
                except RuntimeError as e:raise ValueError(str(e))
            if path=='/api/export':
                result=self.storage.export_store(self.root,'praxis_mine',self.root/'exports'/('praxis-'+uuid.uuid4().hex+'.jsonl'))
                return Path(result['destination']).read_bytes(),'application/x-ndjson'
            if path=='/api/report':return native.report(self.storage,self.root),'text/markdown; charset=utf-8'
            if path=='/api/handoff':
                r=self.storage.get_record(self.root,'praxis_mine',data['record_id']);p=r['payload'];tags=p.get('tags',{})
                return '# Finding to current project\n\n'+json.dumps(p,indent=2)+'\n\nNative ledger: '+str(self.root)+'\nRecord: '+r['record_id']+'\n\nInspect source and evaluation evidence before acting. This handoff is a finding, not installation or production approval. Dormant Arm\'s Reach remains dormant.\n','text/markdown; charset=utf-8'
            raise ValueError('Unknown action')
