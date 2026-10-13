"""Verify a frozen archive and extract into a new directory, with Windows long paths."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,zipfile
archive=Path(sys.argv[1]).resolve();destination=Path(sys.argv[2]).resolve()
assert not destination.exists(),'Use a new directory; never overwrite prior evidence'
destination.mkdir(parents=True)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    manifest=json.loads(z.read('evidence-file-manifest.json'))
    for name,record in manifest.items():
        body=z.read(name)
        assert hashlib.sha256(body).hexdigest()==record['sha256'] and len(body)==record['bytes'],name
    for name in z.namelist():
        assert (destination/name).resolve().is_relative_to(destination),name
    extraction_path='\\\\?\\'+str(destination) if os.name=='nt' else str(destination)
    z.extractall(extraction_path)
research=destination/'research'
r=subprocess.run([sys.executable,'-B','-X','utf8',str(research/'offline_replay.py'),str(research)],capture_output=True,text=True,encoding='utf8',cwd=destination)
assert r.returncode==0,r.stderr
result=json.loads(r.stdout);assert result['passed']
print(json.dumps({'passed':True,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'manifest_entries_verified':len(manifest),'zip_members':len(manifest)+1,'fresh_extracted_offline_replay':result,'destination':str(destination),'overwrite_or_delete':False},ensure_ascii=False))
