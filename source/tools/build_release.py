#!/usr/bin/env python3
"""Build a new private Praxis candidate from current owned source; preserve accepted archives."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,tempfile,zipfile
from datetime import datetime,timezone
from archive_paths import assert_unlinked,check_tree,reparse
from verify_release import verify
VERSION='1.2.0';SLUG='praxis-mine';ROOT=Path(__file__).resolve().parents[2]
ART_SHA='7da3992d465f1263ac4249ad935378e9b93415600ce3a033176cab482a243dfc'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files(root):
 root=assert_unlinked(root)
 return sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() not in {'.pyc','.pyo'})
def inventory(root):return [{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files(root)]
def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def archive(source,target,prefix=''):
 entries=check_tree(source,files(source),prefix)
 with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for name,data in entries:
   info=zipfile.ZipInfo(name,(2026,10,7,0,0,0));info.create_system=3;info.external_attr=(0o100755 if name.endswith('.command') else 0o100644)<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED)
 return {'file':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'members':len(entries)}
def copy_file(relative,stage):
 source=ROOT/relative
 if not source.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Customer source escapes repository')
 for p in (source,*source.parents):
  if reparse(p):raise ValueError('Linked customer source')
 target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
def build(output):
 output=Path(os.path.abspath(output))
 if output.exists():raise ValueError('Candidate output exists; choose a new path. Accepted releases are preserved.')
 output.parent.mkdir(parents=True,exist_ok=True)
 for p in (output.parent,*output.parent.parents):
  if reparse(p):raise ValueError('Linked output ancestor')
 plugin=ROOT/'source/plugin';skill=plugin/'skills'/SLUG
 check_tree(plugin,files(plugin));check_tree(ROOT/'docs',files(ROOT/'docs'));check_tree(ROOT/'assets',files(ROOT/'assets'));check_tree(ROOT/'delivery-sidecars',files(ROOT/'delivery-sidecars'))
 if sha(ROOT/'delivery-sidecars/Praxis Mine.jpg')!=ART_SHA:raise ValueError('Accepted artwork changed')
 docs=json.loads((ROOT/'documentation-manifest.json').read_text(encoding='utf-8'))['customer_docs']
 with tempfile.TemporaryDirectory(prefix='.praxis-build-',dir=output.parent) as temp:
  work=Path(temp);stage=work/'package';stage.mkdir()
  shutil.copytree(plugin,stage/'codex'/SLUG,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
  for relative in docs+['documentation-manifest.json','documentation-authorship.json','documentation-custody.json','Open.cmd','Open.command']:copy_file(relative,stage)
  # Current scoped authoring evidence is support; old review verdicts stay outside this candidate.
  receipt=json.loads((ROOT/'documentation-authorship.json').read_text(encoding='utf-8'))
  records=[receipt['documentation_manifest'],receipt['evidence_packet'],receipt['authoring_response'],*receipt['execution_evidence'],receipt['authoring']['capability_snapshot']]
  for record in records:copy_file(record['path'],stage)
  shutil.copytree(ROOT/'docs/assets',stage/'docs/assets',dirs_exist_ok=True)
  shutil.copytree(ROOT/'assets',stage/'assets')
  shutil.copytree(ROOT/'delivery-sidecars',stage/'delivery-sidecars',dirs_exist_ok=True)
  (stage/'tools').mkdir()
  for name in ['archive_paths.py','verify_release.py']:shutil.copy2(ROOT/'source/tools'/name,stage/'tools'/name)
  (stage/'claude').mkdir();(stage/'archives').mkdir()
  archives=[]
  for kind,source,path in [('claude-skill',skill,stage/'claude'/f'{SLUG}-v{VERSION}.zip'),('standalone-skill',skill,stage/'archives'/f'{SLUG}-skill-v{VERSION}.zip'),('plugin',plugin,stage/'archives'/f'{SLUG}-plugin-v{VERSION}.zip')]:
   record=archive(source,path,SLUG);archives.append({'kind':kind,'path':path.relative_to(stage).as_posix(),**record})
  save(stage/'component-custody.json',{'schema':'praxis-mine-component-custody/v1','name':'Praxis Mine','version':VERSION,'archives':archives})
  manifest={'schema':'praxis-mine-release/v1','name':'Praxis Mine','slug':SLUG,'version':VERSION,'customer_docs':docs,'plugin_files':inventory(stage/'codex'/SLUG),'skill_files':inventory(stage/'codex'/SLUG/'skills'/SLUG),'archives':archives,'all_files':inventory(stage),'claim_boundary':'Private candidate. Exact file identity and bounded checks; no publication, installation, source truth or customer-outcome claim.'}
  save(stage/'manifest.json',manifest)
  result=verify(stage,require_complete=False)
  if not result['ok']:raise ValueError(json.dumps(result))
  kit=work/f'Praxis-Mine-v{VERSION}.zip';record=archive(stage,kit)
  output.mkdir();shutil.copytree(stage,output/'package');shutil.copy2(kit,output/kit.name)
  for p in files(ROOT/'delivery-sidecars'):shutil.copy2(p,output/p.name)
  (output/(kit.name+'.sha256')).write_text(record['sha256']+'  '+kit.name+'\n',encoding='ascii',newline='\n')
 return {'ok':True,'candidate_zip':str(output/kit.name),'sha256':record['sha256'],'package_root':str(output/'package'),'version':VERSION,'verification':result}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path);parser.add_argument('--repair-candidate',action='store_true');parser.add_argument('--staging',action='store_true');args=parser.parse_args()
 output=args.output_dir or ROOT/'repair-candidates'/('v'+VERSION+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
 try:print(json.dumps(build(output),indent=2))
 except (ValueError,OSError,zipfile.BadZipFile) as error:parser.error(str(error))
