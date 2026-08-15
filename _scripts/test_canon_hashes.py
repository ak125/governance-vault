#!/usr/bin/env python3
"""Tests du publisher canonique — hash_mode, sous-ensemble JCS, gate de statut.

Le VECTEUR DE PARITE (§1) est le contrat entre ce publisher et tout verificateur aval :
meme document -> meme empreinte. Un verificateur qui ne reproduit pas PARITY_SHA256 sur
PARITY_DOC n'est pas symetrique, et la divergence ne se verrait qu'en production.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("cch", REPO / "_scripts" / "compute-canon-hashes.py")
cch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cch)


# --------------------------------------------------------------------------- #
# 1. VECTEUR DE PARITE — artefact partage, pas une constante dupliquee
# --------------------------------------------------------------------------- #
# Le vecteur vit dans 99-meta/jcs-parity-vector.json : le publisher et tout
# verificateur aval lisent LE MEME fichier. Recopier ses constantes de chaque cote
# creerait deux sources qui derivent — exactement ce que ce vecteur existe pour empecher.
PARITY_PATH = REPO / "99-meta" / "jcs-parity-vector.json"
PARITY = json.loads(PARITY_PATH.read_text(encoding="utf-8"))
PARITY_DOC = PARITY["document"]
PARITY_EXCLUDED = PARITY["excluded_paths"]
PARITY_CANONICAL = PARITY["canonical_form"]


def test_parity_canonical_form_is_exact():
    """La forme canonique est figee au caractere pres : cles triees, separateurs
    compacts, tableau NON trie (l'ordre d'un tableau est signifiant)."""
    assert cch.canonical_json(PARITY_DOC, PARITY_EXCLUDED) == PARITY_CANONICAL


def test_parity_hash_matches_the_published_vector():
    """LE test de parite. Tout verificateur aval doit produire expected_sha256 sur
    document + excluded_paths. S'il ne le reproduit pas, il n'est pas symetrique."""
    h = cch.sha256_text(cch.canonical_json(PARITY_DOC, PARITY_EXCLUDED))
    assert h == PARITY["expected_sha256"]
    assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)


def test_parity_vector_exercises_the_hard_cases():
    """Le vecteur doit rester discriminant : s'il ne contenait que des cas triviaux,
    deux implementations divergentes le passeraient toutes les deux."""
    doc = PARITY_DOC
    assert list(doc["dimensions"]["autorite"]) != sorted(doc["dimensions"]["autorite"]), \
        "cles deja triees : le tri ne serait pas exerce"
    assert doc["liste"] != sorted(doc["liste"]), "tableau deja trie : l'ordre ne serait pas exerce"
    assert any(v is None for v in doc["flags"].values()), "null non exerce"
    assert '"' in doc["texte"] and "\\" in doc["texte"], "echappement non exerce"
    assert "metadata.distribution_sha256" in PARITY_EXCLUDED, "exclusion non exercee"


def test_excluded_path_is_really_excluded():
    """Changer le champ exclu ne doit PAS changer l'empreinte — sinon le contrat
    deviendrait impossible a publier : ecrire son hash changerait son hash."""
    doc = json.loads(json.dumps(PARITY_DOC))
    doc["metadata"]["distribution_sha256"] = "sha256:" + "f" * 64
    assert cch.canonical_json(doc, PARITY_EXCLUDED) == PARITY_CANONICAL


def test_absent_excluded_path_is_a_noop():
    doc = json.loads(json.dumps(PARITY_DOC))
    del doc["metadata"]["distribution_sha256"]
    assert cch.canonical_json(doc, PARITY_EXCLUDED) == PARITY_CANONICAL


def test_any_other_key_changes_the_hash():
    """Toute cle non exclue entre dans le hash, y compris une note."""
    doc = json.loads(json.dumps(PARITY_DOC))
    doc["_note"] = "ajout"
    assert cch.canonical_json(doc, PARITY_EXCLUDED) != PARITY_CANONICAL


# --------------------------------------------------------------------------- #
# 2. Sous-ensemble JCS — refuser plutot qu'approximer
# --------------------------------------------------------------------------- #
def test_non_ascii_key_is_refused():
    """RFC 8785 trie par unites UTF-16, Python par point de code : hors ASCII les
    deux ordres peuvent diverger. On refuse au lieu de produire une empreinte
    plausible mais non conforme."""
    with pytest.raises(cch.JcsUnsupported, match="non-ASCII"):
        cch.canonical_json({"clé": 1}, [])


def test_float_is_refused():
    with pytest.raises(cch.JcsUnsupported, match="flottant"):
        cch.canonical_json({"poids": 22.5}, [])


def test_nested_float_is_refused():
    with pytest.raises(cch.JcsUnsupported):
        cch.canonical_json({"a": {"b": [1, 2.0]}}, [])


def test_non_ascii_string_value_is_allowed():
    """Une VALEUR non-ASCII est admise : l'echappement JSON est defini sans ambiguite.
    Seules les CLES posent le probleme de tri."""
    out = cch.canonical_json({"k": "éàü"}, [])
    assert out == '{"k":"éàü"}'


# --------------------------------------------------------------------------- #
# 2bis. Bornes des entiers — un int Python n'est pas un Number ECMAScript
# --------------------------------------------------------------------------- #
def test_max_safe_integer_is_accepted():
    assert cch.canonical_json({"n": 9007199254740991}, []) == '{"n":9007199254740991}'


def test_negative_max_safe_integer_is_accepted():
    assert cch.canonical_json({"n": -9007199254740991}, []) == '{"n":-9007199254740991}'


@pytest.mark.parametrize("n", [9007199254740992, 9007199254740993, -9007199254740992, 2**64])
def test_integer_beyond_ieee754_safe_range_is_refused(n):
    """9007199254740993 est exact en Python et ne l'est PAS en Number ECMAScript.
    Accepter cet entier rendrait fausse l'affirmation « les deux coincident »."""
    with pytest.raises(cch.JcsUnsupported, match="IEEE-754"):
        cch.canonical_json({"n": n}, [])


def test_deep_oversized_integer_is_refused():
    with pytest.raises(cch.JcsUnsupported, match="IEEE-754"):
        cch.canonical_json({"a": {"b": [1, 2**53]}}, [])


# --------------------------------------------------------------------------- #
# 2ter. Proprietes dupliquees — invisibles apres parsing, donc refusees AU parsing
# --------------------------------------------------------------------------- #
def test_duplicate_key_is_refused_at_parse_time():
    """json.loads accepterait ce document et ne garderait que weight=22 : la
    duplication serait invisible pour le guard. Le refus doit donc etre au parsing."""
    with pytest.raises(cch.JcsUnsupported, match="dupliquee"):
        cch.strict_json_loads('{"weight": 10, "weight": 22}')


def test_duplicate_key_nested_is_refused():
    with pytest.raises(cch.JcsUnsupported, match="dupliquee"):
        cch.strict_json_loads('{"a": {"b": 1, "b": 2}}')


def test_plain_json_loads_would_have_swallowed_it():
    """Preuve du besoin : le parseur standard ne signale rien."""
    assert json.loads('{"weight": 10, "weight": 22}') == {"weight": 22}


def test_strict_loads_accepts_a_clean_document():
    assert cch.strict_json_loads('{"a": 1, "b": {"c": 2}}') == {"a": 1, "b": {"c": 2}}


# --------------------------------------------------------------------------- #
# 3. Gate de statut — fail-closed
# --------------------------------------------------------------------------- #
def _entry(**over):
    base = {"name": "T", "canon_path": "x.json", "version": "1", "publishable_when": ["accepted"]}
    base.update(over)
    return base


def _json_doc(status):
    body = {"metadata": {}} if status is None else {"metadata": {"status": status}}
    return json.dumps(body)


@pytest.mark.parametrize("status", ["proposed", "conditional", "deprecated", "canon", "ACCEPTED"])
def test_status_not_in_publishable_when_is_refused(status, tmp_path):
    p = tmp_path / "c.json"
    with pytest.raises(SystemExit) as exc:
        cch.enforce_publishable("t", _entry(), p, _json_doc(status))
    assert "publishable_when" in str(exc.value)


def test_status_absent_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="ne declare aucun statut"):
        cch.enforce_publishable("t", _entry(), tmp_path / "c.json", _json_doc(None))


def test_publishable_when_absent_is_refused(tmp_path):
    """Une entree qui ne declare pas ses statuts admissibles est refusee : l'oubli
    ne doit pas valoir permission."""
    e = _entry()
    del e["publishable_when"]
    with pytest.raises(SystemExit, match="publishable_when"):
        cch.enforce_publishable("t", e, tmp_path / "c.json", _json_doc("accepted"))


def test_accepted_passes(tmp_path):
    cch.enforce_publishable("t", _entry(), tmp_path / "c.json", _json_doc("accepted"))


def test_markdown_canon_vocabulary_is_respected(tmp_path):
    """Les rules du vault declarent `status: canon`, pas `accepted`. La liste
    admissible est PAR ENTREE : un vocabulaire code en dur aurait casse l'existant."""
    md = "---\nid: R1\nstatus: canon\n---\n\ncorps\n"
    cch.enforce_publishable("r", _entry(publishable_when=["canon"]), tmp_path / "r.md", md)
    with pytest.raises(SystemExit):
        cch.enforce_publishable("r", _entry(publishable_when=["accepted"]), tmp_path / "r.md", md)


# --------------------------------------------------------------------------- #
# 4. Non-regression du mode historique
# --------------------------------------------------------------------------- #
def test_registered_canons_all_declare_publishable_when():
    for key, meta in cch.CANONS.items():
        assert meta.get("publishable_when"), f"{key} sans publishable_when"


def test_registered_canons_compute_without_error():
    """Le gate ne doit pas casser la chaine existante."""
    out = cch.compute()
    assert set(out["canons"]) == set(cch.CANONS)
    for key, val in out["canons"].items():
        assert val["hash_mode"] == cch.CANONS[key].get("hash_mode", "text_sha256")
        assert len(val["distribution_sha256"]) == 64


def test_source_score_weights_is_not_registered_yet():
    """Le contrat est `proposed` : livrer la CAPACITE de projeter ne vaut pas
    AUTORISATION. Son enregistrement est un acte owner distinct."""
    assert "source-score-weights" not in cch.CANONS
