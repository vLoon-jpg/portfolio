#!/usr/bin/env python3
"""
Auto Portfolio Updater — scans project directories, parses READMEs,
and updates the portfolio index.html with generated project cards.

Usage:
    python portfolio/update.py                  # Scan & update (default)
    python portfolio/update.py --dry-run        # Preview changes without writing
    python portfolio/update.py --watch          # Watch mode (auto-update on changes)
    python portfolio/update.py --json           # Only dump project data as JSON

Configuration: portfolio/projects_config.json
"""

import json
import re
import sys
import time
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ──
BASE_DIR = Path(__file__).resolve().parent          # portfolio/
PROJECTS_ROOT = BASE_DIR.parent                     # C:/Users/LENOVO/projects/
INDEX_HTML = BASE_DIR / "index.html"
CONFIG_FILE = BASE_DIR / "projects_config.json"

# ── Project Card Template ──
CARD_TEMPLATE = """\
    <div class="project-card" onclick="window.open('{url}','_blank')">
      <div class="project-header">
        <h3>{emoji} {title}</h3>
        <span class="project-link-icon">↗</span>
      </div>
      <p>{description}</p>
      <div class="project-tags">{tags_html}</div>
    </div>"""


def load_config():
    """Load project metadata config, returning (exclude_dirs, projects_data)."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {"exclude_dirs": [], "projects": {}}
    exclude = set(cfg.get("exclude_dirs", []))
    return exclude, cfg.get("projects", {})


def discover_project_dirs(exclude_dirs):
    """Scan PROJECTS_ROOT for project directories, excluding known non-project dirs."""
    projects = []
    exclude_dirs = exclude_dirs | {".git", "node_modules", "__pycache__",
                                    ".venv", ".agents", ".claude", ".ruff_cache",
                                    ".github", ".hermes", "portfolio"}
    try:
        for entry in sorted(PROJECTS_ROOT.iterdir()):
            if entry.is_dir() and entry.name not in exclude_dirs:
                projects.append(entry.name)
    except FileNotFoundError:
        print(f"[!] Projects directory not found: {PROJECTS_ROOT}")
        return []
    return projects


def read_readme_text(project_name):
    """Read the README file from a project directory (supports .md and .txt)."""
    proj_dir = PROJECTS_ROOT / project_name
    for readme_name in ("README.md", "README.txt", "README", "readme.md"):
        readme_path = proj_dir / readme_name
        if readme_path.exists():
            try:
                return readme_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                return ""
    return ""


def auto_extract_from_readme(readme_text, project_name):
    """Auto-extract description and tags from a README text."""
    title = project_name
    description = ""
    tags = []

    if not readme_text:
        return title, description, tags

    # Try to extract title from first # heading
    title_match = re.search(r'^#\s+(.+)', readme_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Remove badges/icons from title (unicode emoji + common symbols)
        emoji_pattern = re.compile(r'[\U0001F300-\U0001FFFF\u2600-\u27BF\uFE00-\uFE0F\u200D]', flags=re.UNICODE)
        title = emoji_pattern.sub('', title).strip()

    # Extract first substantial paragraph after title (skip badges/emojis)
    lines = readme_text.split('\n')
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# '):
            capture = True
            continue
        if capture and stripped and not stripped.startswith('#') and not stripped.startswith('![') and not stripped.startswith('['):
            if len(stripped) > 30:  # substantial paragraph
                # Clean markdown links: [text](url) -> text
                description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
                # Truncate
                if len(description) > 120:
                    description = description[:117] + "..."
                break

    # If no long paragraph, try first short one
    if not description:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('!') and not stripped.startswith('['):
                description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
                if len(description) > 120:
                    description = description[:117] + "...\n"
                break

    # Extract tags from README (tech stack mentions)
    tech_keywords = {
        'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript',
        'typescript': 'TypeScript', 'c++': 'C++', 'c#': 'C#', 'go': 'Go',
        'rust': 'Rust', 'html': 'HTML', 'css': 'CSS',
        'fabric': 'Fabric', 'minecraft': 'Minecraft', 'mod': 'Game Mod',
        'docker': 'Docker', 'react': 'React', 'flask': 'Flask',
        'fastapi': 'FastAPI', 'django': 'Django', 'node': 'Node.js',
        'gradle': 'Gradle', 'maven': 'Maven',
        'playwright': 'Playwright', 'selenium': 'Selenium',
        'discord': 'Discord', 'telegram': 'Telegram',
        'cli': 'CLI', 'api': 'API', 'automation': 'Automation',
        'security': 'Security', 'game': 'Game Dev',
        'powerpoint': 'PowerPoint', 'pptx': 'PowerPoint',
        'ai': 'AI', 'machine learning': 'Machine Learning',
        'steam': 'Steam', 'workshop': 'Steam',
        'mcp': 'MCP', 'whatsapp': 'WhatsApp', 'pipecat': 'Pipecat',
        'c2': 'C2', 'malware': 'Security', 'trojan': 'Security',
    }

    readme_lower = readme_text.lower()
    found_tags = set()
    for keyword, label in tech_keywords.items():
        if keyword in readme_lower:
            found_tags.add(label)
    tags = sorted(found_tags, key=lambda t: t.lower())

    return title, description, tags


def build_project_card(project_name, config_projects, exclude_dirs):
    """Build a project card dict from config or auto-detection."""
    # Skip if explicitly excluded
    if project_name in exclude_dirs:
        return None

    # Check config
    if project_name in config_projects:
        p = config_projects[project_name]
        return {
            "title": p.get("title", project_name),
            "emoji": p.get("emoji", "📁"),
            "url": p.get("url", f"https://github.com/vLoon-jpg/{project_name}"),
            "tags": p.get("tags", []),
            "description": p.get("description", ""),
            "dir": project_name,
        }

    # Auto-detect from README
    readme = read_readme_text(project_name)
    title, description, tags = auto_extract_from_readme(readme, project_name)

    # Skip if no meaningful data
    if not description and project_name not in config_projects:
        return None

    return {
        "title": title,
        "emoji": "📁",
        "url": f"https://github.com/vLoon-jpg/{project_name}",
        "tags": tags,
        "description": description,
        "dir": project_name,
    }


def render_cards_html(project_cards):
    """Generate HTML for project cards."""
    cards_html = []
    for card in project_cards:
        tags_html = "".join(
            f'<span class="tag">{tag}</span>' for tag in card["tags"]
        )
        cards_html.append(CARD_TEMPLATE.format(
            url=card["url"],
            emoji=card["emoji"],
            title=card["title"],
            description=card["description"],
            tags_html=tags_html,
        ))
    return "\n".join(cards_html)


def generate_section_html(cards_html):
    """Generate the full featured-projects section HTML."""
    count = cards_html.count('class="project-card"')
    return f"""\
<!-- FEATURED PROJECTS START -->
<section id="featured-projects" class="section">
  <div class="container">
    <h2>Featured Projects</h2>
    <p class="section-sub">Things I've built — mods, tools, automation scripts, and school projects. ({count} projects)</p>
    <div class="projects-list">
{cards_html}
    </div>
  </div>
</section>
<!-- FEATURED PROJECTS END -->"""


def find_projects_section(html):
    """Find the featured projects section marker in the HTML."""
    start_marker = "<!-- FEATURED PROJECTS START -->"
    end_marker = "<!-- FEATURED PROJECTS END -->"
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker)
    if start_idx != -1 and end_idx != -1:
        return start_idx, end_idx + len(end_marker)
    return None, None


def find_skills_section_end(html):
    """Find where the Skills section ends so we can insert our section after it."""
    # Look for the closing of Skills section (</section> after id="skills")
    skills_end = "</section>"  # first </section> after skills
    skills_marker = 'id="skills"'
    skills_idx = html.find(skills_marker)
    if skills_idx == -1:
        return None
    # Find the NEXT </section> after the skills section
    after_skills = html.find("</section>", skills_idx)
    if after_skills == -1:
        return None
    return after_skills + len("</section>")


def update_index_html(new_section_html):
    """Inject the new section into index.html, replacing or inserting as needed."""
    if not INDEX_HTML.exists():
        print(f"[!] index.html not found at: {INDEX_HTML}")
        return False

    html = INDEX_HTML.read_text(encoding="utf-8")

    # Check if section already exists
    start_idx, end_idx = find_projects_section(html)

    if start_idx is not None:
        # Replace existing section
        new_html = html[:start_idx] + new_section_html + html[end_idx:]
        print("[+] Replaced existing featured projects section.")
    else:
        # No existing section — insert after Skills section
        skills_end = find_skills_section_end(html)
        if skills_end is None:
            # Fallback: insert before Projects section
            projects_marker = '<section id="projects"'
            insert_before = html.find(projects_marker)
            if insert_before == -1:
                print("[!] Could not find insertion point in index.html.")
                return False
            new_html = html[:insert_before] + "\n\n" + new_section_html + "\n\n" + html[insert_before:]
            print("[+] Inserted before Projects section.")
        else:
            new_html = html[:skills_end] + "\n\n" + new_section_html + "\n" + html[skills_end:]
            print("[+] Inserted after Skills section.")

    INDEX_HTML.write_text(new_html, encoding="utf-8")
    return True


def get_projects_data(project_names, config_projects, exclude_dirs):
    """Get processed project cards data."""
    cards = []
    for name in project_names:
        card = build_project_card(name, config_projects, exclude_dirs)
        if card:
            cards.append(card)
    # Sort: configured projects first (in config order), then auto-detected alphabetically
    configured_names = list(config_projects.keys())
    configured = [c for c in cards if c["dir"] in configured_names]
    # Sort configured by config order
    configured.sort(key=lambda c: configured_names.index(c["dir"]))
    auto = sorted([c for c in cards if c["dir"] not in configured_names],
                  key=lambda c: c["title"].lower())
    return configured + auto


def print_help():
    print(__doc__)
    sys.exit(0)


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()

    dry_run = "--dry-run" in sys.argv
    watch_mode = "--watch" in sys.argv
    json_output = "--json" in sys.argv

    exclude_dirs, config_projects = load_config()
    project_dirs = discover_project_dirs(exclude_dirs)

    if not project_dirs:
        print("[!] No project directories found.")
        return

    cards = get_projects_data(project_dirs, config_projects, exclude_dirs)

    if json_output:
        print(json.dumps(cards, indent=2))
        return

    cards_html = render_cards_html(cards)
    section_html = generate_section_html(cards_html)

    print(f"[+] Found {len(project_dirs)} projects, generated {len(cards)} cards.")
    for card in cards:
        tags_str = ", ".join(card["tags"]) if card["tags"] else "no tags"
        print(f"    {card['emoji']} {card['title']}  [{tags_str}]")

    if dry_run:
        print("\n[Dry run] Would update index.html with:")
        print(section_html[:500] + "...")
        return

    success = update_index_html(section_html)
    if success:
        print(f"[+] Portfolio updated: {INDEX_HTML}")
    else:
        print("[!] Failed to update portfolio.")

    if watch_mode:
        print("[*] Watch mode enabled. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(30)
                # Re-scan and update
                project_dirs = discover_project_dirs(exclude_dirs)
                cards = get_projects_data(project_dirs, config_projects, exclude_dirs)
                cards_html = render_cards_html(cards)
                section_html = generate_section_html(cards_html)
                update_index_html(section_html)
                print(f"[+] Auto-updated at {time.strftime('%H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n[*] Watch mode stopped.")


if __name__ == "__main__":
    main()
