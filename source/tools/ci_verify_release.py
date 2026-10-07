#!/usr/bin/env python3
"""Verify current Praxis content across host-specific ZIP encodings; retain its exact delivery hash."""
from pathlib import Path
import copy,hashlib,io,json,os,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[2]
GENERATED={'manifest.json','component-custody.json'}
def run(*args):
    subprocess.run([sys.executable,'-B','-X','utf8',*map(str,args)],cwd=ROOT,check=True,env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'})
def comparable_manifest(data):
    result=copy.deepcopy(json.loads(data))
    archive_paths={row.get('path') for row in result.get('archives',[])}
    for row in result.get('archives',[]):
        row.pop('sha256',None);row.pop('bytes',None)
    if 'archives' in result:result['archives'].sort(key=lambda x:x['file'])
    for key in ('all_files','plugin_files','skill_files'):
        if key not in result:continue
        for row in result[key]:
            if key=='all_files' and (row['path'] in archive_paths or row['path']=='component-custody.json'):
                row.pop('sha256',None);row.pop('bytes',None)
        result[key].sort(key=lambda x:x['path'])
    return result

def compare_content(left,right,prefix=''):
    with zipfile.ZipFile(io.BytesIO(left)) as a,zipfile.ZipFile(io.BytesIO(right)) as b:
        aa={n:a.read(n) for n in a.namelist()};bb={n:b.read(n) for n in b.namelist()}
        assert len(aa)==len(a.namelist()) and len(bb)==len(b.namelist()),'Duplicate ZIP member'
        assert set(aa)==set(bb),'Archive namespace differs: '+prefix
        for name in sorted(aa):
            if aa[name]==bb[name]:continue
            if name.endswith('.zip'):compare_content(aa[name],bb[name],prefix+name+'::')
            elif not prefix and name in GENERATED:
                assert comparable_manifest(aa[name])==comparable_manifest(bb[name]),'Generated record differs beyond verified archive hash/size or inventory ordering: '+name
            else:raise AssertionError('Authored member differs: '+prefix+name)

def main():
    current=json.loads((ROOT/'verification/estate-root-review/CURRENT-RELEASE.json').read_text(encoding='utf-8'))
    archive=ROOT/current['zip']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==current['sha256'],'Accepted ZIP changed'
    with tempfile.TemporaryDirectory(prefix='praxis-ci-',dir=ROOT.parent.resolve()) as tmp:
        os.environ.update(TMP=tmp,TEMP=tmp,TMPDIR=tmp)
        candidate=Path(tmp)/'candidate'
        run('source/tools/build_release.py','--output-dir',candidate)
        rebuilt=candidate/archive.name
        compare_content(archive.read_bytes(),rebuilt.read_bytes())
        # Both sets of generated identities must verify against their own actual archives.
        accepted=Path(tmp)/'accepted';accepted.mkdir()
        with zipfile.ZipFile(archive) as z:z.extractall(accepted)
        run(accepted/'tools/verify_release.py',accepted,'--component-only')
        package=candidate/'package'
        run(package/'tools/verify_release.py',package,'--component-only')
        run('-m','unittest','discover','-s',package/'codex/praxis-mine/skills/praxis-mine/tests','-p','test_*.py','-v')
    print('PASS: accepted delivery hash retained; all authored members exact; both native manifests and rebuilt runtime pass. ZIP container hashes/inventory ordering may vary by host.')
if __name__=='__main__':main()