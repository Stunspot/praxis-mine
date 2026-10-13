"""Native room adapter: one ledger, current assessments, bounded local requests."""
import json
import tempfile
import threading
from pathlib import Path
import praxis_mine as native

class Mine:
    class Conflict(ValueError): pass

    def __init__(self, root):
        self.root = root
        self.storage = native.load_storage()
        self.lock = threading.RLock()
        native.ensure_store(self.storage, root, 'praxis-room')

    def records(self):
        records = self.storage.list_records(self.root, 'praxis_mine')
        candidates = {r['payload']['candidate_key']: r for r in records if r['record_type'] == 'candidate'}
        for record in records:
            if record['record_type'] == 'evaluation':
                candidate = candidates.get(record['payload']['candidate_key'])
                record['current_for_candidate'] = bool(candidate and native.evaluation_is_current(self.storage, self.root, candidate, record))
                record['assessment_state'] = 'current material snapshot' if record['current_for_candidate'] else 'stale or legacy unbound; reassess'
        return records

    def request(self, method, path, data):
        if not isinstance(data, dict): raise ValueError('Request body must be a JSON object')
        if method not in {'GET', 'POST'}: raise ValueError('Unsupported method')
        if path in {'/api/save', '/api/create', '/api/import', '/api/evaluate', '/api/export'} and method != 'POST':
            raise ValueError('POST required for this action')
        with self.lock:
            try:
                native.existing_store(self.storage, self.root)
                with self.storage.transaction(self.root, 'praxis_mine', read_only=path not in {'/api/save', '/api/create', '/api/import', '/api/evaluate'}):
                    return self._request(path, data)
            except self.storage.SubstrateError as error:
                if 'conflict' in str(error): raise self.Conflict(str(error)) from error
                raise ValueError(str(error)) from error
            except (RuntimeError, TypeError) as error:
                raise ValueError(str(error)) from error

    def _request(self, path, data):
        if path == '/api/list': return {'records': self.records(), 'data_root': str(self.root)}
        if path == '/api/history': return {'history': self.storage.record_history(self.root, 'praxis_mine', data['record_id'])}
        if path == '/api/save':
            record = self.storage.get_record(self.root, 'praxis_mine', data['record_id'])
            kind = record['record_type']
            if kind not in {'candidate', 'source', 'run'}: raise ValueError('Evaluations are evidence records; use a new native evaluation')
            payload = data['payload']
            if not isinstance(payload, dict): raise ValueError('Payload must be an object')
            if payload.get(kind + '_key') != record['payload'].get(kind + '_key'): raise ValueError('Record identity cannot change')
            version = data['current_version']
            if not isinstance(version, int) or isinstance(version, bool) or version < 1: raise ValueError('current_version must be a positive integer')
            if kind == 'candidate':
                if payload.get('source_key') != record['payload']['source_key']: raise ValueError('Source identity cannot change on an existing finding')
                if payload.get('candidate_status') != record['payload']['candidate_status']: raise ValueError('Disposition changes require the native evaluation gate')
                payload = native.normalize_candidate(payload)
                assessment = native.latest_evaluation(self.storage, self.root, payload['candidate_key'])
                payload['candidate_status'] = assessment['payload']['disposition'] if assessment and native.evaluation_is_current(self.storage, self.root, payload, assessment) else 'triage'
            elif kind == 'source': payload = native.normalize_source(payload)
            else:
                if any(payload.get(key) != value for key, value in record['payload'].items() if key != 'notes') or set(payload) - set(record['payload']) - {'notes'}:
                    raise ValueError('Recorded run evidence is immutable; only explanatory notes may be amended')
            return self.storage.revise_record(self.root, 'praxis_mine', data['record_id'], payload, 'praxis-room', 'supplied', {'route': 'local-workspace'}, 'owner room edit', expected_version=version)
        if path == '/api/create':
            kind, payload = data['kind'], data['payload']
            if kind == 'source': payload = native.normalize_source(payload)
            elif kind == 'candidate': payload = native.normalize_candidate(payload)
            else: raise ValueError('Create sources or candidates; runs and evaluations use their native gate')
            if kind == 'candidate':
                if payload['candidate_status'] != 'triage': raise ValueError('New candidates begin in triage')
                if native.find_record(self.storage, self.root, 'source', 'source_key', payload['source_key']) is None: raise ValueError('Record a source first')
            key = kind + '_key'
            if native.find_record(self.storage, self.root, kind, key, payload[key]): raise ValueError('Identity exists; edit its current record')
            result, _ = native.upsert(self.storage, self.root, kind, key, payload, 'praxis-room', {'route': 'local-workspace'}, 'supplied')
            if kind == 'candidate':
                source = native.find_record(self.storage, self.root, 'source', 'source_key', payload['source_key'])
                self.storage.add_relation(self.root, 'praxis_mine', 'source_contains_candidate', source['record_id'], result['record_id'], 'praxis-room', {'route': 'local-workspace'})
            return result
        if path in {'/api/import', '/api/evaluate'}:
            # Request bytes are temporary transport, not an untracked second ledger.
            value = native.strict_json(data['text']) if path == '/api/import' else data['evaluation']
            with tempfile.TemporaryDirectory(prefix='praxis-request-') as temp:
                file = Path(temp) / 'request.json'
                file.write_text(native.canonical(value), encoding='utf-8', newline='\n')
                if path == '/api/import': return native.ingest_manifest(self.storage, self.root, file, 'praxis-room')
                return native.evaluate(self.storage, self.root, data['candidate_key'], file, 'praxis-room')
        if path == '/api/export':
            with tempfile.TemporaryDirectory(prefix='praxis-export-') as temp:
                result = self.storage.export_store(self.root, 'praxis_mine', Path(temp) / 'export.jsonl')
                return Path(result['destination']).read_bytes(), 'application/x-ndjson'
        if path == '/api/report': return native.report(self.storage, self.root), 'text/markdown; charset=utf-8'
        if path == '/api/handoff':
            record = self.storage.get_record(self.root, 'praxis_mine', data['record_id'])
            if record['record_type'] != 'candidate': raise ValueError('Select a finding for project handoff')
            text = '# Finding to current project\n\n' + native.candidate_report(self.storage, self.root, record)
            text += '\nConfirm this recipient may see the cited sources and project context. Route to the current capability owner. Carry an already-authorized adaptation through that owner and its appropriate checks; otherwise present the bounded next action. This is assessment evidence, not proof of installation or adoption.\n'
            return text, 'text/markdown; charset=utf-8'
        raise ValueError('Unknown action')
