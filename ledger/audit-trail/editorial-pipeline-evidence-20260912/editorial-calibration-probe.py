"""Diagnostic corpus for the existing score, not a competing eligibility engine."""
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
score = load('score', root / '_scripts/compute-confidence-score.py')
gates = load('quality', root / '_scripts/quality-gates.py')
refs = [{'kind':'raw','path':'sources/same-witness.md','confidence':'high'},
        {'kind':'external_url','url':'https://example.com/same-witness','confidence':'high'}]
fm = {'entity_type':'gamme','source_refs':refs}
repeated = 'Ce paragraphe de fixture est repete a chaque rubrique sans information supplementaire.'
def sections(text):
    return '\n'.join('## '+heading+'\n'+text for heading in score.SECTIONS_REQUIRED['gamme'])
cases = [
 ('brief_explanation_without_irrelevant_sections', fm, '## Définition\nLe filtre retient des particules presentes dans le lubrifiant. Cette fixture ne constitue pas une preuve technique.', 'Useful-scoped form; technical truth not evaluated by this probe'),
 ('repeated_paragraphs_with_one_resolved_link', fm, sections(repeated)+'\n[[related]]', 'Duplicate filler; distinct source kinds refer to the same witness'),
 ('contradictory_text_same_structure', fm, sections('Cette fixture affirme une propriete puis son contraire, avec les memes references declarees.')+'\n[[related]]', 'Contradiction must be caught by specialized evidence gates, not this score'),
 ('unsubstantiated_procedure_same_structure', fm, sections('Cette fixture presente une procedure precise sans passage source qui la justifie.')+'\n[[related]]', 'Procedure evidence is not established by heading/source labels'),
 ('all_sections_no_links', fm, sections(repeated), 'No internal link despite all sections and high labels'),
 ('all_sections_broken_link', fm, sections(repeated)+'\n[[missing]]', 'Broken internal link'),
 ('all_sections_no_source', {'entity_type':'gamme','source_refs':[]}, sections(repeated)+'\n[[related]]', 'No source declarations'),
 ('all_sections_medium_sources', {'entity_type':'gamme','source_refs':[dict(r,confidence='medium') for r in refs]}, sections(repeated)+'\n[[related]]', 'Same form with medium labels'),
]
results=[]
with tempfile.TemporaryDirectory() as tmp:
    wiki=Path(tmp); (wiki/'related.md').write_text('Fixture link target')
    for case, meta, body, label in cases:
        results.append({'case':case,'score':score.compute_score(meta,body,wiki),'at_least_current_floor':score.compute_score(meta,body,wiki)>=.85,'interpretation':label})
    # The current scorer keys on entity_type, with no role-specific intent argument.
    common=sections(repeated)+'\n[[related]]'
    role_scores={role:score.compute_score(fm,common,wiki) for role in ['R2 transactional intent','R8 vehicle context']}
registry,catalog=gates.load_registry(),gates.load_source_catalog()
quality=[]
for name in ['valid-plaquette-de-frein.md','valid-non-safety-filtre.md','invalid-source-slug-unknown.md','invalid-overclaimed-brochure-high.md','invalid-no-relation-to-part.md','invalid-maintenance-advice-missing.md']:
    failures,warnings=gates.run_gates(root/'_scripts/tests/fixtures'/name,registry,catalog)
    quality.append({'fixture':name,'failures':failures,'warnings':warnings})
assert results[1]['score']==1.0
assert results[4]['score']==.8
assert results[7]['score']==.84
print(json.dumps({'scope':'Arithmetic scorer corpus and native independent quality fixtures. No complete promotion decision on synthetic cases; no factual truth certification.',
 'score_cases':results,'same_entity_payload_score_by_intended_role':role_scores,'native_quality_cases':quality,'thresholds_changed':False,'promotions':0},ensure_ascii=False,indent=2))
