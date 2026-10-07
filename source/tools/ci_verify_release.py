#!/usr/bin/env python3
"""Check the current accepted Praxis candidate, preserving historical releases."""
from pathlib import Path
import hashlib,io,json,os,subprocess,sys,tempfile,zipfile
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
        if rebuilt.read_bytes()!=archive.read_bytes():
            def compare(left,right,prefix=''):
                with zipfile.ZipFile(io.BytesIO(left)) as a,zipfile.ZipFile(io.BytesIO(right)) as b:
                    aa={n:a.read(n) for n in a.namelist()};bb={n:b.read(n) for n in b.namelist()}
                    for n in sorted(set(aa)^set(bb)):print('NAMESPACE DIFFERENCE',prefix+n,flush=True)
                    for n in sorted(set(aa)&set(bb)):
                        if aa[n]==bb[n]:continue
                        if n.endswith('.zip'):compare(aa[n],bb[n],prefix+n+'::')
                        else:
                            print('MEMBER DIFFERENCE',prefix+n,'accepted',hashlib.sha256(aa[n]).hexdigest(),'rebuilt',hashlib.sha256(bb[n]).hexdigest(),flush=True)
                            if n.endswith('.json'):print('ACCEPTED',aa[n].decode('utf-8')[:1200],'REBUILT',bb[n].decode('utf-8')[:1200],flush=True)
            compare(archive.read_bytes(),rebuilt.read_bytes())
            raise AssertionError('Fresh build differs from accepted candidate; exact member diagnostics above')
        package=candidate/'package'
        run(package/'tools/verify_release.py',package,'--component-only')
        run('-m','unittest','discover','-s',package/'codex/praxis-mine/skills/praxis-mine/tests','-p','test_*.py','-v')
    print('PASS: exact accepted candidate rebuilt and packaged runtime checked; historical release untouched')
if __name__=='__main__':main()
