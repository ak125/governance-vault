"""Read-only corpus characterization; emits evidence, never exports or promotions."""
import contextlib, hashlib, importlib.util, io, json, subprocess
from pathlib import Path
base = Path(__file__).resolve().parent
roots = [Path('/opt/automecanik/wiki-auto-validation'), Path('/opt/automecanik/wiki-editorial-qualification-20260912')]
records, inputs, errors, excluded = [], [], [], []
for root in roots:
    spec = importlib.util.spec_from_file_location('wiki_builder', root / '_scripts/build_exports_seo.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    for folder, pattern in [('exports/seo','*.json'), ('wiki','*.md'), ('proposals','*.md')]:
        for p in sorted((root/folder).rglob(pattern)):
            raw=p.read_bytes(); inputs.append({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest()})
            rel=p.relative_to(root).as_posix()
            if rel in ('proposals/_index.md','proposals/_quality/sources-brief.md'):
                excluded.append({'path':str(p),'reason':'navigation index or source-quality brief, not an entity fiche'})
                continue
            try:
                if folder == 'exports/seo':
                    payload = json.loads(raw); stage='existing-export'; status=None; eligible=None
                    if not isinstance(payload,dict) or 'entity_id' not in payload: continue
                else:
                    fm, body = builder._parse_markdown(p)
                    if not fm.get('entity_type') or not fm.get('slug'): raise ValueError('entity_type or slug missing on entity candidate')
                    capture=io.StringIO()
                    with contextlib.redirect_stderr(capture):
                        facts,sources,blocks=builder._extract_facts_sources_blocks(fm,body,fm['entity_type'])
                        eligible,reason=builder._is_seo_eligible(fm,body,p)
                    payload={'entity_id':fm['entity_type']+':'+fm['slug'],'entity_type':fm['entity_type'],'blocks':blocks}
                    stage='native-transform-preview-'+folder;status=fm.get('review_status')
                records.append({'path':str(p),'stage':stage,'review_status':status,'eligible':eligible,'payload':payload})
            except Exception as e: errors.append({'path':str(p),'error':str(e)})
heads={str(r):subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD']).decode().strip() for r in roots}
(base/'editorial-identity-inputs.json').write_text(json.dumps({'heads':heads,'inputs':inputs,'records':records,'errors':errors,'excluded':excluded},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'files_read':len(inputs),'records':len(records),'errors':errors}))
