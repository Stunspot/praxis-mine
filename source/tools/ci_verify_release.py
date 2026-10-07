#!/usr/bin/env python3
"""Check the current accepted Praxis candidate, preserving historical releases."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
def run(*args):
    subprocess.run([sys.executable,'-B','-X','utf8',*map(str,args)],cwd=ROOT,check=True,env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'})
def main():
    current=json.loads((ROOT/'verification/estate-root-review/CURRENT-RELEASE.json').read_text(encoding='utf-8'))
    archive=ROOT/current['zip']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==current['sha256'],'Accepted ZIP changed'
    with tempfile.TemporaryDirectory(prefix='praxis-ci-',dir=ROOT.parent.resolve()) as tmp:
        os.environ.update(TMP=tmp,TEMP=tmp,TMPDIR=tmp)
        candidate=Path(tmp)/'candidate'
        run('source/tools/build_release.py','--output-dir',candidate)
        rebuilt=candidate/archive.name
        assert rebuilt.read_bytes()==archive.read_bytes(),'Fresh build differs from accepted candidate'
        package=candidate/'package'
        run(package/'tools/verify_release.py',package,'--component-only')
        run('-m','unittest','discover','-s',package/'codex/praxis-mine/skills/praxis-mine/tests','-p','test_*.py','-v')
    print('PASS: exact accepted candidate rebuilt and packaged runtime checked; historical release untouched')
if __name__=='__main__':main()
