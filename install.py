#!/usr/bin/env python3
"""Install the plugin from this checkout; optionally bind a key in Umbriel.

Requires Python 3.11+, Noctalia 5 with plugin API 26+, and a running shell.
This checkout remains the plugin source: keep it after installation.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

PLUGIN = "zerodice0/codex_usage"
SOURCE = "codex-usage"
TOGGLE = f"noctalia msg panel-toggle {PLUGIN}:panel"
ROOT = Path(__file__).resolve().parent


def shortcut_config(content, key, remove=False):
    """Preserve comments/formatting and refuse to overwrite another binding."""
    if not re.fullmatch(r"(?:Mod|Super|Alt|Ctrl|Shift)(?:\+[A-Za-z0-9]+)+", key):
        raise ValueError("Use an Umbriel shortcut such as Mod+Shift+U")
    parsed = tomllib.loads(content)
    value = parsed.get("keybinds", {}).get(key)
    action = value.get("action") if isinstance(value, dict) else value
    expected = "spawn:" + TOGGLE
    if value is not None and action != expected:
        raise ValueError(f"{key} already has a different action; choose --shortcut or --no-shortcut")
    if value is not None and not remove:
        return content
    if value is None and remove:
        return content
    section = re.search(r"(?m)^\[keybinds\][ \t]*(?:#[^\n]*)?(?:\n|$)", content)
    line = f'{json.dumps(key)} = {{ action = {json.dumps(expected)}, repeat = false }}\n'
    if remove:
        pattern = rf"(?m)^[ \t]*[\"']{re.escape(key)}[\"'][ \t]*=[^\n]*(?:\n|$)"
        updated, count = re.subn(pattern, "", content, count=1)
        if count != 1:
            raise ValueError("Cannot safely remove this binding's syntax; remove it manually")
    elif section:
        position = section.end()
        separator = "" if content[:position].endswith("\n") else "\n"
        updated = content[:position] + separator + line + content[position:]
    elif "keybinds" in parsed:
        raise ValueError("Cannot safely edit this keybinds syntax; use --no-shortcut")
    else:
        updated = content.rstrip() + "\n\n[keybinds]\n" + line
    tomllib.loads(updated)
    return updated


def included_bindings(path, seen=None):
    """Read effective included keybinds so installation cannot hide a conflict."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen or not path.exists():
        return {}
    seen.add(path)
    doc = tomllib.loads(path.read_text())
    bindings = {}
    for included in doc.get("include", {}).get("files", []):
        child = Path(os.path.expandvars(os.path.expanduser(included)))
        bindings.update(included_bindings(child if child.is_absolute() else path.parent / child, seen))
    bindings.update(doc.get("keybinds", {}))
    return bindings


def run(*args):
    result = subprocess.run(args, check=True, text=True, capture_output=True, timeout=30)
    if result.stdout.strip().startswith("error:"):
        raise ValueError(result.stdout.strip())
    return result.stdout


def replace_config(path, before, after):
    if before == after:
        return
    if path.read_text() != before:
        raise ValueError("Configuration changed during installation; rerun the installer")
    # A unique backup is retained beside the config, outside the Git repository.
    descriptor, backup_name = tempfile.mkstemp(prefix=path.name + ".codex-usage-backup-", dir=path.parent)
    os.close(descriptor)
    shutil.copy2(path, backup_name)
    descriptor, candidate_name = tempfile.mkstemp(prefix=".codex-usage-", suffix=".toml", dir=path.parent)
    candidate = Path(candidate_name)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(after)
        run("umbriel", "validate", "-c", str(candidate))
        if path.read_text() != before:
            raise ValueError("Configuration changed during validation; rerun the installer")
        candidate.chmod(path.stat().st_mode & 0o777)
        candidate.replace(path)
    finally:
        candidate.unlink(missing_ok=True)
    print(f"Configuration backup: {backup_name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shortcut", default="Mod+Shift+U")
    parser.add_argument("--no-shortcut", action="store_true", help="Configure the compositor shortcut manually")
    parser.add_argument("--umbriel-config", type=Path, help="Explicit Umbriel configuration path")
    parser.add_argument("--check", action="store_true", help="Validate and print the plan without changes")
    parser.add_argument("--uninstall", action="store_true", help="Disable plugin, remove source and matching shortcut; keep source files")
    args = parser.parse_args()
    if not shutil.which("noctalia"):
        raise ValueError("Install Noctalia 5 first")
    run("noctalia", "msg", "status")
    if not args.uninstall:
        run("noctalia", "plugins", "lint", str(ROOT / "codex_usage"))
    sources = run("noctalia", "msg", "plugins", "source", "list")
    existing = next((line.split(maxsplit=2) for line in sources.splitlines() if line.startswith(SOURCE + " ")), None)
    if existing and existing != [SOURCE, "path", str(ROOT)]:
        raise ValueError(f"Source {SOURCE!r} points elsewhere; manage that source in Noctalia settings first")

    config = args.umbriel_config
    if config is None and "umbriel" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
        config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "umbriel/config.toml"
    before = after = None
    if not args.no_shortcut and config is not None:
        config = config.expanduser().resolve()
        before = config.read_text()
        if not args.uninstall:
            effective = included_bindings(config).get(args.shortcut)
            action = effective.get("action") if isinstance(effective, dict) else effective
            if effective is not None and action != "spawn:" + TOGGLE:
                raise ValueError(f"{args.shortcut} is already assigned (including included files)")
        after = shortcut_config(before, args.shortcut, remove=args.uninstall)
        print(f"{'Remove' if args.uninstall else 'Configure'} {args.shortcut} in {config}")
    print(f"{'Remove' if args.uninstall else 'Register'} plugin source: {ROOT}")
    print(f"Toggle command: {TOGGLE}")
    if args.check:
        return

    if args.uninstall:
        if before is not None:
            replace_config(config, before, after)
        run("noctalia", "msg", "plugins", "disable", PLUGIN)
        if existing:
            run("noctalia", "msg", "plugins", "source", "remove", SOURCE)
        print("Plugin disabled; source files and plugin preferences retained.")
    else:
        if not existing:
            run("noctalia", "msg", "plugins", "source", "add", SOURCE, "path", str(ROOT))
        run("noctalia", "msg", "plugins", "enable", PLUGIN)
        if before is not None:
            replace_config(config, before, after)
        else:
            print("Bind the toggle command in your compositor to finish keyboard setup.")
        print("Installed. Keep this checkout; git pull updates the plugin.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        sys.exit(1)
