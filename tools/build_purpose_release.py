"""Build complete incremented purpose-led candidates from accepted complete kits."""
from pathlib import Path
import hashlib,io,json,zipfile,shutil,unicodedata
BASES={
 'praxis-mine':('1.2.1','1.3.0','Praxis Mine','release-candidates/current-v1.2.1/Praxis-Mine-v1.2.1.zip','source/plugin/skills/praxis-mine'),
 'signalhouse':('0.2.1','0.3.0','Signalhouse','release-candidates/current-v0.2.1/signalhouse-v0.2.1-complete.zip','source/skills/signalhouse'),
 'promiseloop-creator-studio':('0.2.1','0.3.0','PromiseLoop Creator Studio','release-candidates/current-v0.2.1/promiseloop-creator-studio-v0.2.1-complete.zip','source/skills/promiseloop-creator-studio')}
def digest(b):return hashlib.sha256(b).hexdigest()
def encode(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
def tree(root):return {p.relative_to(root).as_posix():p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'}}
def archive(rows):
 seen=set();stream=io.BytesIO()
 for name in rows:
  normalized=unicodedata.normalize('NFC',name).casefold()
  if normalized in seen:raise ValueError('Colliding name '+name)
  seen.add(normalized)
  if len(('C:/Users/Owner/Downloads/'+name).encode('utf-16-le'))//2>=260:raise ValueError('Long extraction path '+name)
  if any(len(part.encode())>255 for part in name.split('/')):raise ValueError('Long path component '+name)
 with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,body in sorted(rows.items()):
   info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100755 if name.endswith('.command') else 0o100644)<<16;z.writestr(info,body)
 return stream.getvalue()
def build(slug, output_suffix="", root=None, baseline_override=None):
 old,new,title,baseline,source=BASES[slug];repo=(Path(root).resolve() if root else Path(__file__).resolve().parents[1]);skill=repo/source
 if baseline_override:baseline=str(Path(baseline_override).resolve())
 if digest((repo/baseline).read_bytes()) != EXPECTED_BASE:raise ValueError('Prior complete kit hash does not match the accepted constructor baseline')
 with zipfile.ZipFile(repo/baseline) as z:rows={x:z.read(x) for x in z.namelist() if not x.endswith('/')}
 prefix='release-v'+old+'/'
 if all(k.startswith(prefix) for k in rows):rows={k[len(prefix):]:v for k,v in rows.items()}
 # Keep historical cutoffs and documentation attribution. Replace every active runtime mirror.
 prefixes=['codex/','maintainer-source/','claude/','archives/']
 for k in list(rows):
  if any(k.startswith(p) for p in prefixes):del rows[k]
 runtime=tree(skill)
 if slug=='praxis-mine':
  plugin=tree(repo/'source/plugin')
  rows.update({'codex/'+slug+'/'+p:v for p,v in plugin.items()})
  rows['archives/'+slug+'-plugin-v'+new+'.zip']=archive({slug+'/'+p:v for p,v in plugin.items()})
  rows['archives/'+slug+'-skill-v'+new+'.zip']=archive({slug+'/'+p:v for p,v in runtime.items()})
 else:rows.update({'codex/'+slug+'/'+p:v for p,v in runtime.items()})
 rows.update({'maintainer-source/'+slug+'-v'+new+'/skills/'+slug+'/'+p:v for p,v in runtime.items()})
 rows['claude/'+slug+'-v'+new+'.zip']=archive({slug+'/'+p:v for p,v in runtime.items()})
 # Make the entry instructions and current release identity agree; retained old release notes stay historical.
 for k in list(rows):
  if (k in {'README.md','START-HERE.md','OPEN-WORKSPACE.md','SUPPORT.md'} or k.startswith('docs/')) and k.endswith('.md'):
   rows[k]=rows[k].decode('utf-8-sig').replace(old,new).encode()
 for k in list(rows):
  if k.startswith('delivery-sidecars/'):del rows[k]
 for p,v in tree(repo/('delivery-v'+new)).items():
  if not p.endswith('.zip'):rows['delivery-sidecars/'+p]=v
 guide=runtime['workspace/WORKING-GUIDE.md'];rows['WORKING-GUIDE.md']=guide
 rows['START-HERE.md']=('# '+title+' '+new+'\n\nOpen the app with Open.cmd on Windows or Open.command on macOS. Read [Working guide](WORKING-GUIDE.md) for ordinary entry and useful work.\n\nExisting saved work stays in its separate work folder. The new interface uses the existing native objects; no conversion packet is needed.\n').encode()
 if slug!='praxis-mine':
  rows['Open.cmd']=('@echo off\r\npy -3 "%~dp0codex\\'+slug+'\\workspace\\host.py"\r\nif errorlevel 1 pause\r\n').encode()
  rows['Open.command']=('#!/bin/sh\ncd "$(dirname "$0")"\nexec python3 "codex/'+slug+'/workspace/host.py"\n').encode()
 for name in [f'RELEASE-NOTES-v{new}.md',f'release-decision-v{new}.json']:rows[name]=(repo/name).read_bytes()
 rows['RELEASE-DECISION.md']=('# Current release decision\n\nThis '+new+' product update replaces the '+old+' application experience under the owner\'s explicit instruction. See release-decision-v'+new+'.json. Older decisions and qualification records are historical; they do not certify this new interface.\n').encode()
 for manifest in ['manifest.json','release-manifest.json','component-custody.json','documentation-manifest.json']:
  if manifest in rows:
   rows['historical-'+old+'-'+manifest]=rows.pop(manifest)
 rows['documentation-manifest.json']=encode({'product':slug,'version':new,'current_guide':'WORKING-GUIDE.md','guide_sha256':digest(guide),'boundary':'Current working guide and behavior were authored with the implementation; old documentation evidence retains its historical scope.'})
 if output_suffix:
  if 'documentation-authorship.json' in rows:rows['historical-'+old+'-documentation-authorship.json']=rows['documentation-authorship.json']
  for name in ['documentation-authorship.json','docs/DOCUMENTATION-CUSTODY.json','verification/companion-format-20261015/prior-documentation-authorship.json']:
   rows[name]=(repo/name).read_bytes()
  receipt=json.loads(rows['documentation-authorship.json'])
  for ref in [receipt['documentation_manifest'],receipt['evidence_packet'],receipt['authoring_response'],receipt['authoring']['capability_snapshot'],*receipt['execution_evidence']]:rows[ref['path']]=(repo/ref['path']).read_bytes()
  dm=json.loads(rows['documentation-manifest.json']);dm['companion_authorship']='documentation-authorship.json';dm['companion']=receipt['authored_files'][0]['path'];rows['documentation-manifest.json']=encode(dm)
 entries=[{'path':p,'bytes':len(v),'sha256':digest(v)} for p,v in sorted(rows.items())]
 rows['release-manifest.json']=encode({'format':'cd-purpose-led-release/v1','product':slug,'version':new,'baseline':old,'release_treatment':'update','runtime_source':source,'files':entries,'qualification':'Ordinary-input browser journeys and targeted file/storage recovery checks; see builder evidence in the canonical repository. No model or audience outcome claim.'})
 out=repo/('release-v'+new);out.mkdir(exist_ok=True)
 for p,v in rows.items():dest=out/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(v)
 complete=archive({'release-v'+new+'/'+p:v for p,v in rows.items()});target=repo/('release-candidates/purpose-v'+new+output_suffix);target.mkdir(parents=True,exist_ok=True)
 zipfile_path=target/(title+' v'+new+'.zip');zipfile_path.write_bytes(complete);(target/(zipfile_path.name+'.sha256')).write_text(digest(complete)+'  '+zipfile_path.name+'\n')
 # Direct archive readback includes all active native and nested-host runtime bytes.
 with zipfile.ZipFile(zipfile_path) as z:
  assert z.testzip() is None
  for e in entries:assert digest(z.read('release-v'+new+'/'+e['path']))==e['sha256']
  with zipfile.ZipFile(io.BytesIO(z.read('release-v'+new+'/claude/'+slug+'-v'+new+'.zip'))) as inner:assert {p[len(slug)+1:]:inner.read(p) for p in inner.namelist()}==runtime
 result={'product':slug,'version':new,'source':str(skill),'complete_zip':str(zipfile_path),'package_root':str(out),'sha256':digest(complete),'runtime_files':len(runtime),'files':len(rows),'bytes':len(complete),'constructor':'PASS'}
 (target/'build-result.json').write_bytes(encode(result));shutil.copy2(zipfile_path,repo/('delivery-v'+new)/zipfile_path.name);print(json.dumps(result));return result
EXPECTED_BASE='8b68272a0d8a8a96921d949929e05348438df1ac772a81adf74cdb788d800d60'
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,help='Accepted prior complete ZIP; exact SHA-256 is checked');p.add_argument('--suffix',default='-rebuild');a=p.parse_args()
 build('praxis-mine',a.suffix,baseline_override=a.baseline)
