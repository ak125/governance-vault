# Read-only counterexample: native scalar score only, not the full promotion engine.
import importlib.util,json,tempfile,sys
from pathlib import Path
root=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('confidence',root/'_scripts/compute-confidence-score.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='score-counterexample-') as d:
 wiki=Path(d);(wiki/'target.md').write_text('fixture only')
 fm={'entity_type':'gamme','source_refs':[{'kind':'technical_datasheet','confidence':'high'},{'kind':'workshop_guidance','confidence':'high'}]}
 body='\n'.join('## '+h+'\n'+'banane '*10 for h in m.SECTIONS_REQUIRED['gamme'])+'\n[[target]]'
 print(json.dumps({'scope':'compute_score only; full gates not exercised','content':'banane repeated 10 times per required section','sources':'unverified confidence declarations','score':m.compute_score(fm,body,wiki)},indent=2))
