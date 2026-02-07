# CLAUDE.md

## Project Overview

**Governance Vault** is the governance and audit documentation system for **AutoMecanik**, a NestJS + Remix monorepo application. This is a Markdown-based knowledge management vault (Obsidian-compatible), not a software project. It stores architecture decisions (ADRs), incident post-mortems, governance rules, agent specifications, audit trails, and compliance records.

## Governance Authority Model

**GOVERNANCE-HUMAN.md is the SOURCE OF TRUTH.** It overrides all other documents.

- **RULE-H0**: Human operator is the only authority. No AI may override this.
- **RULE-H1**: All agents are NON-TRUSTED by default.
- **RULE-H4**: Only the principal VPS + human-approved workflows may write to this vault.
- **RULE-H5**: Canon (`.spec/00-canon/`, governance-vault, ADRs, rules) is read-only for agents.
- **RULE-H6**: All agent modifications must pass through the Airlock governance gate.

Agents may only submit **candidates** (bundles). They must NOT commit, push, or modify governance directly.

## Repository Structure

```
governance-vault/
├── 00-index/           # MOC (Maps of Content) - navigation hubs
├── 01-incidents/       # Post-mortems & incident reports
├── 02-decisions/       # ADRs (ADR-001 to ADR-010) + operational decisions (DEC-*)
├── 03-policies/        # Bundle specification + schema + prompts
├── 03-rules/           # Technical rules (R1-R7) + governance rules (R8-R11)
├── 04-audit-trail/     # Deployment logs, security audits, bundle decisions
├── 05-agents/          # 140 AI agent specifications (categorized)
├── 05-compliance/      # Plans, checklists, reports
├── 06-knowledge/       # Architecture & knowledge base
├── 99-meta/            # Governance meta-documents
├── scripts/            # Governance automation (bash)
└── README.md
```

## Vault Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **R-Vault-01** | Canon fait foi - `.spec/00-canon/` is authoritative | `sync-canon.sh` (one-way sync) |
| **R-Vault-02** | Zero orphans - every document linked from at least 1 MOC | `check-orphans.sh` |
| **R-Vault-03** | Signed commits - all commits must be cryptographically signed | `audit-signatures.sh` |
| **R-Vault-04** | CI read-only - no CI/CD writes to governance vault | Policy enforcement |

## Technical Rules (AutoMecanik Monorepo)

These rules apply to the related NestJS + Remix monorepo, documented here for governance:

- **R1**: 3-tier architecture: Controller -> Service -> DataService
- **R2**: Direct Supabase SDK (no Prisma), tables prefixed with `__`
- **R3**: Redis sessions + Passport authentication
- **R4**: Zod validation on all inputs
- **R5**: HMAC-based payment security (Paybox)
- **R6-R7**: Additional architectural constraints

## Scripts

```bash
scripts/check-orphans.sh   # Validate no orphaned documents
scripts/sync-canon.sh      # One-way sync from monorepo canon
scripts/audit-signatures.sh # Verify signed commits
scripts/evidence-pack.sh   # Generate compliance evidence bundles
scripts/gov                # Main governance CLI tool
```

## Document Conventions

- **Language**: Primarily French, some English
- **ADR format**: `ADR-NNN-title.md` with YAML frontmatter (id, title, status, date)
- **Decisions**: `DEC-NNN-title.md`
- **Incidents**: `YYYY-MM-DD_severity_title.md`
- **Agents**: `AGENT-name.md` with approval verdicts (APPROVED / APPROVED_WITH_CONDITIONS / NOT_APPROVED)
- **MOC (Maps of Content)**: Navigation hub files linking related documents via `[[wikilinks]]`

## Key References

- `00-index/GOVERNANCE-HUMAN.md` - Ultimate authority model (read this first)
- `00-index/MOC-Governance.md` - Master navigation index
- `03-rules/technical/rules.md` - R1-R7 technical rules
- `03-rules/governance/governance-policy.md` - R8-R11 governance rules
- `05-agents/registry/REG-001-agents.md` - Master agent registry (140 agents)
- `03-policies/BUNDLE-SPEC.md` - Bundle specification format
- `03-policies/bundle.schema.v1.json` - Bundle JSON schema

## Working in This Repo

- This is a documentation vault. Changes are Markdown edits, not code changes.
- Respect the MOC linking system: every new document must be referenced from at least one MOC.
- Follow existing naming conventions for ADRs, decisions, incidents, and agents.
- The monorepo canon (`.spec/00-canon/`) is the source of truth; this vault is an enriched operational mirror.
