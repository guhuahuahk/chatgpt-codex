#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from string import Template


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"


def render_template(template_path: Path, values: dict[str, str]) -> str:
    return Template(template_path.read_text()).safe_substitute(values)


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content)


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
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser()
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

    daily_memory = memory_dir / "YYYY-MM-DD.md"
    if not daily_memory.exists() or args.force:
        daily_memory.write_text(
            "# Daily Memory\n\n"
            f"- Agent: {args.display_name}\n"
            f"- Department: {department_name}\n"
            "- Use real dated files for live runtime.\n"
        )

    print(f"Scaffolded workspace: {workspace}")
    print("Next steps:")
    print("1. Replace placeholder daily memory with a real date file.")
    print("2. Add the agent to openclaw.json agents.list.")
    print("3. Create agentDir and initialize sessions store.")
    print("4. Configure heartbeat, channel bindings, and database sync if needed.")


if __name__ == "__main__":
    main()
