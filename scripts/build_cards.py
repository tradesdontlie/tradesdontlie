#!/usr/bin/env python3
"""Generate themed SVG repo cards for the profile README.

Fetches live repo metadata from the GitHub API and renders one SVG card per
repo into assets/cards/. Runs in CI daily so star counts stay fresh without
depending on third-party card services.
"""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

OWNER = "tradesdontlie"
REPOS = [
    "tradingview-mcp",
    "task-manager-mcp",
    "pine-script-v6-extension",
    "pinescript-development-workspace",
    "pinescript-compiler",
    "prop-firm-monte-carlo",
]
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "cards")

LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "C#": "#178600",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "Rust": "#dea584",
    "Go": "#00ADD8",
}

CARD_W, CARD_H = 420, 150


def fetch(repo):
    url = f"https://api.github.com/repos/{OWNER}/{repo}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-card-builder",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def kfmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def wrap(text, width=56, max_lines=2):
    words = (text or "").split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
        else:
            cur = f"{cur} {w}".strip()
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(words) and len(lines) == max_lines and " ".join(lines).count(" ") + 1 < len(words):
        lines[-1] = lines[-1][: width - 1].rstrip() + "…"
    return lines


def render(data):
    name = data["name"]
    desc_lines = wrap(data.get("description") or "")
    lang = data.get("language") or ""
    lang_color = LANG_COLORS.get(lang, "#8b949e")
    stars = kfmt(data.get("stargazers_count", 0))
    forks = kfmt(data.get("forks_count", 0))

    desc_svg = "".join(
        f'<text x="24" y="{78 + i * 20}" font-family="\'Segoe UI\',Ubuntu,sans-serif" '
        f'font-size="13" fill="#8b949e">{escape(line)}</text>'
        for i, line in enumerate(desc_lines)
    )

    lang_svg = ""
    if lang:
        lang_svg = (
            f'<circle cx="30" cy="124" r="5" fill="{lang_color}"/>'
            f'<text x="42" y="129" font-family="\'Segoe UI\',Ubuntu,sans-serif" '
            f'font-size="12" fill="#8b949e">{escape(lang)}</text>'
        )

    stats_x = 220 if lang else 24
    return f'''<svg width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="0.5" y="0.5" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
  <path d="M 330 44 L 348 36 L 362 40 L 378 26 L 396 18" stroke="#00d4aa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.55"/>
  <path d="M 330 44 L 348 36 L 362 40 L 378 26 L 396 18 L 396 52 L 330 52 Z" fill="#00d4aa" opacity="0.07"/>
  <g transform="translate(22, 24)">
    <path d="M4 1.5H3a2 2 0 0 0-2 2V13a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1" stroke="#8b949e" stroke-width="1.4" fill="none" transform="scale(1.15)"/>
  </g>
  <text x="46" y="40" font-family="'JetBrains Mono','Consolas',monospace" font-size="17" font-weight="700" fill="#00d4aa">{escape(name)}</text>
  {desc_svg}
  {lang_svg}
  <g transform="translate({stats_x}, 115)">
    <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z" fill="#e3b341" transform="scale(0.9)"/>
    <text x="20" y="12" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="12" fill="#e6edf3">{stars}</text>
    <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z" fill="#8b949e" transform="translate(64,0) scale(0.9)"/>
    <text x="84" y="12" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="12" fill="#e6edf3">{forks}</text>
  </g>
</svg>
'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for repo in REPOS:
        data = fetch(repo)
        path = os.path.join(OUT_DIR, f"{repo}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(data))
        print(f"wrote {path} ({data.get('stargazers_count', 0)} stars)")


if __name__ == "__main__":
    main()
