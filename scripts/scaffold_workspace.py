#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import time
import uuid
from datetime import date, timedelta
from pathlib import Path
from string import Template


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
SHARED_RULES_DIR = Path.home() / ".openclaw" / "shared-rules" / "departments"


def render_template(template_path: Path, values: dict[str, str]) -> str:
    return Template(template_path.read_text()).safe_substitute(values)


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content)


def ensure_not_nested_workspace(workspace: Path) -> None:
    for parent in workspace.parents:
        if (parent / "AGENTS.md").exists() and (parent / "IDENTITY.md").exists():
            raise SystemExit(
                f"Refusing to create nested workspace inside existing agent workspace: {parent}"
            )
        if parent == Path.home():
            break


def validate_agent_id(agent_id: str) -> None:
    if not re.fullmatch(r"[a-z0-9-]+", agent_id):
        raise SystemExit(
            "agent-id must use lowercase ASCII letters, numbers, and hyphen only"
        )


def validate_department_slug(department_slug: str) -> None:
    rule_file = SHARED_RULES_DIR / f"{department_slug}.md"
    if not rule_file.exists():
        raise SystemExit(f"Missing department rule file: {rule_file}")


def init_runtime_layer(
    *,
    agent_id: str,
    display_name: str,
    agent_dir: Path,
    force: bool,
    seed_main_session: bool,
    session_display_name: str,
    copy_runtime_config_from: Path | None,
) -> None:
    runtime_root = agent_dir.parent
    sessions_dir = runtime_root / "sessions"
    sessions_file = sessions_dir / "sessions.json"

    agent_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir.mkdir(parents=True, exist_ok=True)

    if copy_runtime_config_from is not None:
        source_dir = copy_runtime_config_from.expanduser()
        for filename in ("models.json", "auth-profiles.json"):
            src = source_dir / filename
            dst = agent_dir / filename
            if src.exists() and (force or not dst.exists()):
                shutil.copy2(src, dst)

    if sessions_file.exists() and not force:
        return

    session_index: dict[str, object] = {}
    if seed_main_session:
        session_id = str(uuid.uuid4())
        session_key = f"agent:{agent_id}:main"
        session_path = sessions_dir / f"{session_id}.jsonl"
        if force or not session_path.exists():
            session_path.write_text("")
        now_ms = int(time.time() * 1000)
        session_index[session_key] = {
            "sessionId": session_id,
            "updatedAt": now_ms,
            "systemSent": True,
            "abortedLastRun": False,
            "chatType": "direct",
            "displayName": session_display_name,
            "deliveryContext": {
                "channel": "webchat",
            },
            "origin": {
                "label": "heartbeat",
                "provider": "webchat",
                "from": "heartbeat",
                "to": "heartbeat",
                "surface": "webchat",
                "chatType": "direct",
            },
            "sessionFile": str(session_path),
            "compactionCount": 0,
            "status": "done",
            "lastChannel": "webchat",
        }

    sessions_file.write_text(json.dumps(session_index, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new OpenClaw agent workspace from the bundled openclaw-agent-builder templates."
    )
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--department", required=True, help="Department slug that matches ~/.openclaw/shared-rules/departments/<slug>.md")
    parser.add_argument("--department-name", default="")
    parser.add_argument("--role", required=True)
    parser.add_argument("--upstream", default="董事长")
    parser.add_argument("--approved-channels", default="direct")
    parser.add_argument("--identity-summary", default="Dedicated OpenClaw agent")
    parser.add_argument("--vibe", default="clear, steady, disciplined")
    parser.add_argument("--emoji", default=":)")
    parser.add_argument("--heartbeat-owner", default="this agent")
    parser.add_argument("--heartbeat-style", default="silent")
    parser.add_argument("--heartbeat-check-1", default="Check pending work in this lane")
    parser.add_argument("--heartbeat-check-2", default="Check whether memory needs updating")
    parser.add_argument("--heartbeat-check-3", default="Check whether escalation is required")
    parser.add_argument("--agent-dir", default="")
    parser.add_argument("--copy-runtime-config-from", default="")
    parser.add_argument("--init-runtime", action="store_true")
    parser.add_argument("--seed-main-session", action="store_true")
    parser.add_argument("--session-display-name", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser()
    validate_agent_id(args.agent_id)
    validate_department_slug(args.department)
    ensure_not_nested_workspace(workspace)
    memory_dir = workspace / "memory"
    skills_dir = workspace / "skills"

    workspace.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    department_name = args.department_name or args.department.replace("-", " ").title()

    values = {
        "agent_id": args.agent_id,
        "display_name": args.display_name,
        "department_slug": args.department,
        "department_name": department_name,
        "role_name": args.role,
        "upstream_controller": args.upstream,
        "approved_channels": args.approved_channels,
        "identity_summary": args.identity_summary,
        "vibe": args.vibe,
        "emoji": args.emoji,
        "heartbeat_owner": args.heartbeat_owner,
        "heartbeat_style": args.heartbeat_style,
        "heartbeat_check_1": args.heartbeat_check_1,
        "heartbeat_check_2": args.heartbeat_check_2,
        "heartbeat_check_3": args.heartbeat_check_3,
    }

    template_map = {
        "AGENTS.md.template": "AGENTS.md",
        "IDENTITY.md.template": "IDENTITY.md",
        "HEARTBEAT.md.template": "HEARTBEAT.md",
        "MEMORY.md.template": "MEMORY.md",
        "SOUL.md.template": "SOUL.md",
        "USER.md.template": "USER.md",
        "TOOLS.md.template": "TOOLS.md",
    }

    for template_name, output_name in template_map.items():
        content = render_template(TEMPLATE_DIR / template_name, values)
        write_file(workspace / output_name, content, args.force)

    for target_day in (date.today() - timedelta(days=1), date.today()):
        daily_memory = memory_dir / f"{target_day.isoformat()}.md"
        if not daily_memory.exists() or args.force:
            daily_memory.write_text(
                "# Daily Memory\n\n"
                f"- Agent: {args.display_name}\n"
                f"- Department: {department_name}\n"
                f"- Date: {target_day.isoformat()}\n"
                "- Record real decisions, not placeholders.\n"
            )

    if args.init_runtime:
        if not args.agent_dir:
            raise SystemExit("--init-runtime requires --agent-dir")
        init_runtime_layer(
            agent_id=args.agent_id,
            display_name=args.display_name,
            agent_dir=Path(args.agent_dir).expanduser(),
            force=args.force,
            seed_main_session=args.seed_main_session,
            session_display_name=args.session_display_name or args.display_name,
            copy_runtime_config_from=Path(args.copy_runtime_config_from).expanduser()
            if args.copy_runtime_config_from
            else None,
        )

    print(f"Scaffolded workspace: {workspace}")
    print("Next steps:")
    print("1. Add or verify the agent in openclaw.json agents.list.")
    if args.init_runtime:
        print("2. Verify the initialized runtime layer (agentDir, sessions, main session displayName).")
        print("3. Configure heartbeat, live bindings, and database sync if needed.")
    else:
        print("2. Initialize runtime layer (agentDir, sessions, main session displayName).")
        print("3. Configure heartbeat, live bindings, and database sync if needed.")


if __name__ == "__main__":
    main()
