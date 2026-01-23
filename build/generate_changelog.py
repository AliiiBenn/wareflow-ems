"""Generate changelog from git commits.

This script parses git commits and generates a structured changelog
following Keep a Changelog format (https://keepachangelog.com/).

Usage:
    python build/generate_changelog.py
    python build/generate_changelog.py --version 1.2.0
    python build/generate_changelog.py --from-tag v1.1.0 --to-tag v1.2.0
"""

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return output."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_tags() -> List[str]:
    """Get all git tags sorted by version."""
    tags = run_git_command(["git", "tag", "-l", "v*.*.*"]).split("\n")
    # Filter empty strings
    tags = [t for t in tags if t]
    # Sort by version
    tags.sort(key=lambda x: [int(i) for i in x.replace("v", "").split(".")])
    return tags


def get_latest_tag() -> str:
    """Get the latest git tag."""
    tags = get_tags()
    if tags:
        return tags[-1]
    return ""


def get_commits(from_ref: str = None, to_ref: str = "HEAD") -> List[Dict]:
    """Get commits between two references."""
    if from_ref:
        range_spec = f"{from_ref}..{to_ref}"
    else:
        range_spec = to_ref

    # Get commit messages in format: hash|message
    output = run_git_command([
        "git", "log", range_spec,
        "--pretty=format:%H|%s",
        "--reverse"
    ])

    commits = []
    for line in output.split("\n"):
        if not line or "|" not in line:
            continue
        hash_id, message = line.split("|", 1)
        commits.append({"hash": hash_id, "message": message})

    return commits


def parse_commit_message(message: str) -> Dict:
    """Parse a conventional commit message."""
    # Pattern: type(scope): description
    # Examples:
    # feat: add new feature
    # fix(auth): resolve login issue
    # feat(database)!: breaking change
    pattern = r"^(\w+)(?:\(([^)]+)\))?(!)?: (.+)"

    match = re.match(pattern, message)
    if not match:
        return {"type": "other", "scope": None, "breaking": False, "description": message}

    commit_type, scope, breaking, description = match.groups()

    return {
        "type": commit_type.lower(),
        "scope": scope,
        "breaking": bool(breaking),
        "description": description
    }


def categorize_commit(parsed: Dict) -> tuple:
    """Categorize commit into changelog section and emoji."""
    type_mapping = {
        "feat": ("Added", "✨"),
        "fix": ("Fixed", "🐛"),
        "security": ("Security", "🔒"),
        "docs": ("Documentation", "📚"),
        "refactor": ("Changed", "♻️"),
        "perf": ("Performance", "⚡"),
        "test": ("Tests", "✅"),
        "chore": ("Other", "🔧"),
        "style": ("Style", "💄"),
        "build": ("Build", "📦"),
        "ci": ("CI", "🤖"),
    }

    category, emoji = type_mapping.get(parsed["type"], ("Other", "🔧"))

    if parsed["breaking"]:
        category = "Breaking Changes"
        emoji = "⚠️"

    return category, emoji


def generate_changelog(
    version: str = None,
    from_tag: str = None,
    to_tag: str = "HEAD"
) -> str:
    """Generate changelog markdown."""
    if not version:
        version = "Unreleased"

    # Get commits
    commits = get_commits(from_tag, to_tag)

    if not commits:
        return f"## [{version}]\n\nNo changes.\n"

    # Parse and categorize commits
    categories = {}
    breaking_changes = []

    for commit in commits:
        parsed = parse_commit_message(commit["message"])
        category, emoji = categorize_commit(parsed)

        if category not in categories:
            categories[category] = []

        # Add emoji to description
        description = f"{emoji} {parsed['description']}"

        # Add commit hash link
        commit_hash = commit["hash"][:8]
        description += f" ({commit_hash})"

        categories[category].append(description)

        # Track breaking changes
        if parsed["breaking"]:
            breaking_changes.append(parsed["description"])

    # Generate markdown
    changelog = f"## [{version}]\n\n"

    # Add date if not unreleased
    if version != "Unreleased":
        date_str = datetime.now().strftime("%Y-%m-%d")
        changelog += f"**Release Date**: {date_str}\n\n"

    # Add breaking changes warning at top
    if breaking_changes:
        changelog += "### ⚠️ Breaking Changes\n\n"
        for change in breaking_changes:
            changelog += f"- {change}\n"
        changelog += "\n"

    # Add categories
    for category in ["Added", "Fixed", "Security", "Changed", "Performance", "Documentation", "Tests", "Other"]:
        if category not in categories:
            continue

        changelog += f"### {category}\n\n"
        for item in categories[category]:
            changelog += f"- {item}\n"
        changelog += "\n"

    return changelog


def update_changelog_file(version: str = None, from_tag: str = None):
    """Update CHANGELOG.md file."""
    changelog_path = Path("CHANGELOG.md")

    # Generate new changelog entry
    new_entry = generate_changelog(version, from_tag)

    if changelog_path.exists():
        # Read existing changelog
        content = changelog_path.read_text()

        # Check if unreleased section exists
        if "## [Unreleased]" in content:
            # Replace unreleased section
            content = re.sub(
                r"## \[Unreleased\].*?(?=\n## \[|$)",
                new_entry,
                content,
                flags=re.DOTALL
            )
        else:
            # Add new version at top
            content = new_entry + "\n" + content
    else:
        # Create new changelog with header
        header = """# Changelog

All notable changes to Wareflow EMS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
        content = header + new_entry

    # Write updated changelog
    changelog_path.write_text(content)

    print(f"✅ Updated {changelog_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelog from git commits"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Version number (e.g., 1.2.0)"
    )
    parser.add_argument(
        "--from-tag",
        type=str,
        default=None,
        help="Starting tag (default: latest tag)"
    )
    parser.add_argument(
        "--to-tag",
        type=str,
        default="HEAD",
        help="Ending tag (default: HEAD)"
    )
    parser.add_argument(
        "--update-file",
        action="store_true",
        help="Update CHANGELOG.md file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Get from_tag if not specified
    from_tag = args.from_tag
    if from_tag is None:
        from_tag = get_latest_tag()
        if from_tag:
            print(f"Using latest tag: {from_tag}")

    # Generate changelog
    version = args.version
    if version and not version.startswith("v"):
        version = f"v{version}"

    changelog = generate_changelog(version, from_tag, args.to_tag)

    # Output
    if args.output:
        Path(args.output).write_text(changelog)
        print(f"✅ Changelog written to {args.output}")
    elif args.update_file:
        update_changelog_file(version, from_tag)
    else:
        print(changelog)


if __name__ == "__main__":
    main()
