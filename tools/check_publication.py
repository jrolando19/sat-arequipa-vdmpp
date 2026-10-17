"""Check a staged/committed snapshot locally. Never publishes or changes Git state."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest=json.loads((ROOT/'publication_manifest.json').read_text(encoding='utf-8'))
    failures=[]
    expected_vdm=['model/'+name+'.vdmpp' for name in
                  ['TiposSAT','Sensor','Quebrada','Alarma','Sistema','TestSAT']]+['review/AuditSAT.vdmpp']
    records={item['file']:item for item in manifest['files']}
    for name,item in records.items():
        path=ROOT/name
        if not path.is_file() or digest(path)!=item['public_sha256']:
            failures.append('public hash mismatch: '+name)
    for name in expected_vdm:
        item=records[name]
        if item['original_sha256']!=item['public_sha256']:
            failures.append('frozen VDM source changed: '+name)
    text_suffixes={'.md','.txt','.json','.log','.ps1','.py','.vdmpp','.svg'}
    for path in ROOT.rglob('*'):
        rel=path.relative_to(ROOT)
        if (not path.is_file() or path.suffix not in text_suffixes or
            any(part in {'.git','tools_runtime','evidence_reproduced','execution_reproduced','__pycache__'} for part in rel.parts) or
            rel.parts[:2]==('model','tools')):
            continue
        text=path.read_text(encoding='utf-8-sig')
        # Do not treat this checker source's generic detection expressions as leaked data.
        if path==Path(__file__).resolve():continue
        if re.search(r'[A-Za-z]:[/\\]+Users[/\\]+[^/\\\s]+|Co-authored-by',text,re.I):
            failures.append('private path or unwanted attribution: '+str(rel))
        if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|AIza[0-9A-Za-z_-]{25,}',text):
            failures.append('credential-like payload: '+str(rel))
    result={'status':'PASS' if not failures else 'FAIL','failures':failures,
            'frozen_vdm_sources_verified':len(expected_vdm),
            'files_verified':len(records),'publishes_or_changes_git':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
