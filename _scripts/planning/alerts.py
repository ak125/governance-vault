"""P0 stagnation alerts: dedup via existing open issue check, ack via close-issue,
best-effort GitHub Issues (primary) + email SMTP (fallback)."""
import json
import logging
import os
import re
import smtplib
import subprocess
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import yaml


log = logging.getLogger("planning.alerts")


COOLDOWN_HOURS = 24
ALERT_REPO = "ak125/governance-vault"
ALERT_LABEL = "planning-p0-stagnant"


_ACK_BLOCK_RE = re.compile(
    r"```yaml\s*\n(ack:[\s\S]*?)\n```",
    re.MULTILINE,
)


class _StringTimestampLoader(yaml.SafeLoader):
    """SafeLoader variant that keeps ISO timestamps as strings (no auto-datetime).

    PyYAML's default SafeLoader resolves YAML implicit `tag:yaml.org,2002:timestamp`
    tokens to `datetime.datetime` objects. We persist `last_alert_at` / `acked_at` /
    `mute_until` as ISO 8601 strings (UTC, with `Z` suffix preserved) to keep the
    round-trip stable and stay compatible with `_parse_iso()` which expects a string.
    """


# Remove the timestamp implicit resolver so YYYY-MM-DDTHH:MM:SSZ stays a string.
_StringTimestampLoader.yaml_implicit_resolvers = {
    k: [(tag, regexp) for tag, regexp in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def read_ack_block(moc_path: Path) -> dict[str, Any]:
    """Parse the ack YAML block from MOC. Returns {} if absent or malformed."""
    if not moc_path.exists():
        return {}
    m = _ACK_BLOCK_RE.search(moc_path.read_text())
    if not m:
        return {}
    try:
        loaded = yaml.load(m.group(1), Loader=_StringTimestampLoader) or {}
    except yaml.YAMLError:
        log.warning("ack block YAML invalid in %s", moc_path)
        return {}
    return loaded.get("ack") or {}


def update_last_alert_at(
    ack_block: dict[str, Any],
    *,
    fired_ids: list[str],
    now: datetime,
) -> dict[str, Any]:
    """Return new ack_block with last_alert_at=now.isoformat() for each fired_id.

    Preserves existing keys (acked_at, mute_until, reason, etc.). Pure function —
    does NOT mutate input.
    """
    iso = now.isoformat()
    out = {k: dict(v) for k, v in ack_block.items()}
    for cid in fired_ids:
        out.setdefault(cid, {})["last_alert_at"] = iso
    return out


def write_ack_update(moc_path: Path, *, ack_block: dict[str, Any]) -> bool:
    """Rewrite the ack YAML block in MOC. Returns True if file changed.

    Only the ack block is rewritten ; surrounding MOC content (frontmatter, items
    table, semantic_hash, etc.) is preserved verbatim. This keeps "ack updates"
    distinct from "business updates" (I3) — the file changes but `semantic_hash`
    line is untouched, so commit message convention :
    `chore(planning): ack update [no-hash-change]`.

    "Changed" is checked semantically (parsed YAML equality), not byte-equal —
    `safe_dump` may add quotes to ISO timestamps that the operator wrote unquoted,
    which is cosmetic-only and must NOT trigger a commit.
    """
    if not moc_path.exists():
        return False
    text = moc_path.read_text()
    new_yaml = yaml.safe_dump({"ack": ack_block}, default_flow_style=False).rstrip()
    new_block = f"```yaml\n{new_yaml}\n```"

    # Compare semantically against existing block (avoid cosmetic quote-only diffs).
    existing_ack = read_ack_block(moc_path)
    if existing_ack == ack_block:
        return False

    new_text, n = _ACK_BLOCK_RE.subn(new_block, text, count=1)
    if n == 0 or new_text == text:
        return False
    moc_path.write_text(new_text)
    return True


def _parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def compute_alert_targets(
    items: list[dict[str, Any]],
    *,
    ack_block: dict[str, Any],
    now: datetime,
) -> list[dict[str, Any]]:
    """Return items eligible for alerting (P0 stagnant 24h+, no recent alert, not muted)."""
    targets = []
    cooldown = timedelta(hours=COOLDOWN_HOURS)
    for it in items:
        if it.get("priority") != "P0":
            continue
        if (it.get("stagnation_days") or 0) < 1:
            continue
        cid = it["canonical_id"]
        ack = ack_block.get(cid, {})
        last_alert_str = ack.get("last_alert_at")
        if last_alert_str and (now - _parse_iso(last_alert_str)) < cooldown:
            continue
        mute_until_str = ack.get("mute_until")
        if mute_until_str and _parse_iso(mute_until_str) > now:
            continue
        targets.append(it)
    return targets


def _open_issue_exists(canonical_id: str) -> bool:
    """Check if an open issue with `canonical_id` in title already exists (dedup)."""
    try:
        r = subprocess.run(
            ["gh", "issue", "list",
             "--repo", ALERT_REPO,
             "--label", ALERT_LABEL,
             "--state", "open",
             "--search", f'"{canonical_id}" in:title',
             "--json", "number,title",
             "--limit", "10"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        return len(json.loads(r.stdout)) > 0
    except Exception as e:
        log.warning("gh issue list failed (dedup check skipped): %s", e)
        return False  # On failure, allow create attempt — gh-side dedup not enforced


def send_alert_github_issue(item: dict[str, Any]) -> bool:
    """Create GitHub Issue with `planning-p0-stagnant` label. Returns True on success."""
    cid = item["canonical_id"]
    if _open_issue_exists(cid):
        log.info("Issue already open for %s — skipping create", cid)
        return True  # Treat as success : alert already visible
    title = f"[P0 stagnant {item.get('stagnation_days','?')}d] {cid}"
    body_lines = [
        f"**Canonical ID** : `{cid}`",
        f"**Title** : {item.get('title','(no title)')}",
        f"**Stagnation** : {item.get('stagnation_days','?')} days",
        f"**URL** : {item.get('url','(no url)')}",
        "",
        "_Auto-created by Planning Live cron (ADR-053). Close this issue to ack the alert._",
        "_The next cron run will read closed issues and persist `acked_at` in MOC ack block._",
    ]
    try:
        subprocess.run(
            ["gh", "issue", "create",
             "--repo", ALERT_REPO,
             "--title", title,
             "--label", ALERT_LABEL,
             "--body", "\n".join(body_lines)],
            check=True, capture_output=True, text=True, timeout=15,
        )
        return True
    except Exception as e:
        log.warning("gh issue create failed for %s: %s", cid, e)
        return False


def send_alert_email(item: dict[str, Any]) -> bool:
    """Email fallback via SMTP. Returns True on success."""
    host = os.environ.get("SMTP_HOST")
    to_addr = os.environ.get("EMAIL_ALERT_TO")
    if not host or not to_addr:
        log.warning("SMTP_HOST or EMAIL_ALERT_TO missing — skipping email")
        return False
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM", user or "automecanik-bot@localhost")
    msg = EmailMessage()
    msg["Subject"] = f"[P0 stagnant] {item['canonical_id']}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(
        f"Item {item['canonical_id']} stagnant {item.get('stagnation_days','?')}d.\n"
        f"Title: {item.get('title','')}\n"
        f"URL: {item.get('url','')}\n"
    )
    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        log.warning("SMTP send failed for %s: %s", item['canonical_id'], e)
        return False


def fire_alerts(
    targets: list[dict[str, Any]],
    *,
    strict: bool = False,
) -> list[str]:
    """Fire alerts. Returns list of canonical_ids successfully alerted (for ack persistence)."""
    fired = []
    for it in targets:
        if send_alert_github_issue(it) or send_alert_email(it):
            fired.append(it["canonical_id"])
        elif strict:
            raise RuntimeError(f"Both GH Issue and email failed for {it['canonical_id']}")
    return fired


def fetch_closed_alert_issues() -> list[dict[str, Any]]:
    """Fetch closed `planning-p0-stagnant` issues. Used to detect ack actions.

    Returns list of {canonical_id, closed_at, closed_by} extracted from titles.
    canonical_id is parsed from title format `[P0 stagnant Nd] <canonical_id>`.
    """
    try:
        r = subprocess.run(
            ["gh", "issue", "list",
             "--repo", ALERT_REPO,
             "--label", ALERT_LABEL,
             "--state", "closed",
             "--json", "number,title,closedAt,author",
             "--limit", "100"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        rows = json.loads(r.stdout)
    except Exception as e:
        log.warning("gh issue list (closed) failed: %s", e)
        return []
    out = []
    for row in rows:
        # Title format : `[P0 stagnant Nd] <canonical_id>`
        title = row.get("title", "")
        if "] " not in title:
            continue
        cid = title.split("] ", 1)[1].strip()
        if not cid:
            continue
        out.append({
            "canonical_id": cid,
            "closed_at": row.get("closedAt"),
            "closed_by": (row.get("author") or {}).get("login"),
            "issue_number": row.get("number"),
        })
    return out
