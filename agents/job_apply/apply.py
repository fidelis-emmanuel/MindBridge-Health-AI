#!/usr/bin/env python3
"""
MindBridge Job Apply Agent — CLI entry point.

Usage (run from project root only):
    python agents/job_apply/apply.py add
    python agents/job_apply/apply.py list
    python agents/job_apply/apply.py update <id>
    python agents/job_apply/apply.py stats

Note: On Windows, prefix with PYTHONUTF8=1 for correct emoji/box-drawing rendering.
    PYTHONUTF8=1 python agents/job_apply/apply.py --help
"""
import sys
import click
from pathlib import Path

# Windows: reconfigure stdout/stderr to UTF-8 so emoji and box-drawing render correctly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Allow running from project root: python agents/job_apply/apply.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.job_apply import matcher, cover_letter, tracker
from agents.job_apply.profile import PROFILE
from agents.shared.logger import get_logger, log_session
from agents.shared.email_notifier import send_application_confirmation

logger = get_logger("job_apply")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fit_bar(score: int) -> str:
    """Visual progress bar for fit score."""
    filled = score // 5
    return "█" * filled + "░" * (20 - filled)


def _band_color(band: str) -> str:
    return {"Excellent": "bright_green", "Strong": "green",
            "Moderate": "yellow", "Weak": "red"}.get(band, "white")


def _read_multiline(prompt: str, sentinel: str = ";;") -> str:
    """Collect multi-line input until sentinel line is entered."""
    click.echo(f"{prompt} (type {sentinel} on a new line to finish):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == sentinel:
            break
        lines.append(line)
    return "\n".join(lines)


# ── CLI group ─────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """MindBridge Job Apply Agent — track, score, and apply."""
    pass


# ── add ───────────────────────────────────────────────────────────────────────

@cli.command()
def add():
    """Add a new job posting, score it, and optionally generate a cover letter."""
    click.echo("\n── New Job Application ─────────────────────────────────────\n")
    company  = click.prompt("Company name")
    title    = click.prompt("Job title")
    job_text = _read_multiline("\nPaste the full job posting")

    if not job_text.strip():
        click.secho("❌  Job posting cannot be empty.", fg="red")
        return

    # Score
    fit = matcher.score(job_text)
    click.echo(f"\n📊 Fit Score: ", nl=False)
    click.secho(f"{fit['score']}/100 ({fit['band']})",
                fg=_band_color(fit["band"]), bold=True)
    click.echo(f"   {_fit_bar(fit['score'])}")

    if fit["matched_skills"]:
        click.echo(f"   ✅ Skills matched : {', '.join(fit['matched_skills'][:6])}")
    if fit["matched_roles"]:
        click.echo(f"   🎯 Role match     : {fit['matched_roles'][0]}")
    if fit["matched_healthcare"]:
        click.echo(f"   🏥 Healthcare     : {', '.join(fit['matched_healthcare'][:4])}")

    # Cover letter
    letter_text = ""
    if click.confirm("\nGenerate cover letter with Claude?", default=True):
        click.echo("✍️  Writing cover letter...")
        try:
            letter_text = cover_letter.generate(job_text, company, title, fit)
            click.echo("\n" + "─" * 60)
            click.echo(letter_text)
            click.echo("─" * 60)
            click.secho("\n✅ Letter saved to agents/job_apply/letters/", fg="green")
        except (RuntimeError, OSError) as e:
            click.secho(f"⚠️  Cover letter failed: {e}", fg="yellow")

    # Save to DB
    app_id = tracker.add_job(company, title, fit["score"], job_text, letter_text)
    click.secho(f"\n✅ Saved as application #{app_id}", fg="green")

    # Log
    log_session("job_apply", "add", {
        "id": app_id,
        "company": company,
        "title": title,
        "fit_score": fit["score"],
        "band": fit["band"],
    })

    # Email notification (silent if EMAIL_PASSWORD not set)
    stats = tracker.get_stats()
    send_application_confirmation(title, company, stats.get("applied", 0))


# ── list ──────────────────────────────────────────────────────────────────────

@cli.command("list")
@click.option(
    "--status", default=None,
    type=click.Choice(["draft", "applied", "interview", "offer", "rejected"]),
    help="Filter by status",
)
def list_jobs(status):
    """List all tracked applications."""
    rows = tracker.list_jobs(status)
    if not rows:
        msg = f"No applications with status '{status}'." if status else "No applications yet."
        click.echo(msg)
        return

    header = f"\n{'ID':<4} {'Company':<22} {'Title':<30} {'Score':<7} {'Status':<11} Created"
    click.echo(header)
    click.echo("─" * 82)

    status_colors = {
        "applied":   "cyan",
        "interview": "bright_green",
        "offer":     "bright_cyan",
        "rejected":  "red",
        "draft":     "white",
    }

    for r in rows:
        score_str = f"{r['fit_score']}/100" if r["fit_score"] is not None else "—"
        created   = (r["created_at"] or "")[:10]
        color     = status_colors.get(r["status"], "white")

        click.echo(
            f"{r['id']:<4} {r['company'][:21]:<22} {r['title'][:29]:<30} "
            f"{score_str:<7} ",
            nl=False,
        )
        click.secho(f"{r['status']:<11}", fg=color, nl=False)
        click.echo(created)


# ── update ────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("app_id", type=int)
def update(app_id):
    """Update status or notes for an application (by ID)."""
    status = click.prompt(
        "New status",
        type=click.Choice(["draft", "applied", "interview", "offer", "rejected"]),
    )
    notes = click.prompt("Notes (press Enter to skip)", default="")

    ok = tracker.update_status(app_id, status, notes)
    if ok:
        click.secho(f"✅ Application #{app_id} → '{status}'", fg="green")
        log_session("job_apply", "update", {"id": app_id, "status": status})
    else:
        click.secho(f"❌ Application #{app_id} not found.", fg="red")


# ── stats ─────────────────────────────────────────────────────────────────────

@cli.command()
def stats():
    """Show application pipeline statistics."""
    s     = tracker.get_stats()
    total = s.pop("_total", 0)
    avg   = s.pop("_avg_fit", 0)

    click.echo("\n── Application Pipeline ────────────────────────────────────\n")
    click.echo(f"  Total tracked  : {total}")
    click.echo(f"  Avg fit score  : {avg}/100")
    click.echo()

    status_icons = {
        "draft":     "📝",
        "applied":   "📤",
        "interview": "🎙️ ",
        "offer":     "🎉",
        "rejected":  "❌",
    }

    for status_name, count in sorted(s.items()):
        icon = status_icons.get(status_name, "•")
        bar  = "█" * count
        click.echo(f"  {icon} {status_name:<12} {count:>3}  {bar}")

    click.echo()


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
