"""Generate local profile cards from GitHub's public GraphQL data.

Requires Python 3.10+ and GitHub CLI. In Actions, GH_TOKEN is supplied by the
workflow's automatic GITHUB_TOKEN; no personal token or service is required.
"""

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
QUERY = """
query Profile($login: String!, $cursor: String) {
  user(login: $login) {
    login
    followers { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          firstDay
          contributionDays { date contributionCount contributionLevel }
        }
      }
    }
    repositories(first: 100, after: $cursor, privacy: PUBLIC,
                 ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes { name url stargazerCount primaryLanguage { name color } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""


def fetch_profile(username):
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", username):
        raise ValueError("Invalid GitHub username")
    cursor = None
    repositories = []
    while True:
        response = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=json.dumps({"query": QUERY, "variables": {
                "login": username, "cursor": cursor,
            }}),
            text=True, encoding="utf-8", capture_output=True, check=True,
        )
        payload = json.loads(response.stdout)
        if payload.get("errors"):
            raise RuntimeError("GitHub GraphQL rejected the profile query")
        user = payload["data"]["user"]
        if not user:
            raise ValueError("GitHub user not found")
        page = user["repositories"]
        repositories.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            if len(repositories) != page["totalCount"]:
                raise ValueError("Incomplete repository response")
            user["repositories"] = repositories
            user["updated_on"] = datetime.now(timezone.utc).date().isoformat()
            return user
        next_cursor = page["pageInfo"]["endCursor"]
        if not next_cursor or next_cursor == cursor:
            raise ValueError("GitHub returned an invalid pagination cursor")
        cursor = next_cursor


def validate_profile(profile):
    calendar = profile["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    if not 365 <= len(days) <= 372 or len({day["date"] for day in days}) != len(days):
        raise ValueError("Incomplete or duplicated contribution dates")
    dates = sorted(date.fromisoformat(day["date"]) for day in days)
    if any(right - left != timedelta(days=1) for left, right in zip(dates, dates[1:])):
        raise ValueError("Missing day in the contribution calendar")
    if dates[-1].isoformat() != profile["updated_on"]:
        raise ValueError("Contribution calendar does not include the update date")
    for day in days:
        date.fromisoformat(day["date"])
        if day["contributionCount"] < 0:
            raise ValueError("Negative contribution count")
    if sum(day["contributionCount"] for day in days) != calendar["totalContributions"]:
        raise ValueError("Contribution total does not match the calendar")
    if len({repo["url"] for repo in profile["repositories"]}) != len(profile["repositories"]):
        raise ValueError("Duplicated repository in profile response")


def text(x, y, content, size=16, color="#94A3B8", weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" {extra}>{escape(str(content))}</text>')


def card(height, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<defs><linearGradient id="bg"><stop stop-color="#15142A"/><stop offset="1" stop-color="#0D2030"/></linearGradient><linearGradient id="accent"><stop stop-color="#A78BFA"/><stop offset="1" stop-color="#22D3EE"/></linearGradient></defs>
<style>
@keyframes scan {{ from {{transform:translateX(0)}} to {{transform:translateX(1040px)}} }}
.scan {{animation:scan 14s ease-in-out infinite alternate}}
@media (prefers-reduced-motion:reduce) {{* {{animation:none!important}}}}
</style>
<rect x=".5" y=".5" width="1199" height="{height - 1}" rx="20" fill="url(#bg)" stroke="#343452"/>
<g font-family="Segoe UI, Arial, sans-serif">{body}</g>
</svg>
'''


def render_stats(profile):
    repos = profile["repositories"]
    total = profile["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    metrics = [
        (total, "CONTRIBUCIONES", "Últimos 12 meses · visibles"),
        (len(repos), "REPOSITORIOS", "Públicos propios · sin forks"),
        (sum(repo["stargazerCount"] for repo in repos), "ESTRELLAS", "En repositorios propios públicos"),
        (profile["followers"]["totalCount"], "SEGUIDORES", "Comunidad en GitHub"),
    ]
    body = text(32, 35, "DANTE1128 / EN NÚMEROS", 12, "#A5B4FC", 600,
                'letter-spacing="2"')
    for index, (value, label, description) in enumerate(metrics):
        x = 32 + index * 296
        if index:
            body += f'<path d="M{x - 18} 62V177" stroke="#343452"/>'
        body += text(x, 98, f"{value:,}", 44, "#C4B5FD" if index < 2 else "#67E8F9", 700)
        body += text(x, 131, label, 12, "#E2E8F0", 600, 'letter-spacing="1.7"')
        body += text(x, 157, description, 12)
    body += text(32, 201, f"Datos de GitHub · Actualizado: {profile['updated_on']} UTC", 11)
    return card(222, "Estadísticas reales de Dante Yupanqui en GitHub", body)


def render_calendar(profile):
    calendar = profile["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    colors = {"NONE": "#1C263B", "FIRST_QUARTILE": "#373268",
              "SECOND_QUARTILE": "#6D4DC4", "THIRD_QUARTILE": "#A78BFA",
              "FOURTH_QUARTILE": "#67E8F9"}
    body = text(32, 40, "Cada aporte deja una huella.", 25, "#F1F5F9", 700)
    body += text(32, 69, f"{calendar['totalContributions']:,} contribuciones visibles en los últimos 12 meses", 15)
    months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    previous_month = None
    for col, week in enumerate(weeks):
        month = date.fromisoformat(week["firstDay"]).month
        x = 72 + col * 20
        if previous_month is not None and month != previous_month:
            body += text(x, 106, months[month - 1], 12)
        previous_month = month
        for day in week["contributionDays"]:
            current = date.fromisoformat(day["date"])
            row = (current.weekday() + 1) % 7
            y = 120 + row * 19
            fill = colors[day["contributionLevel"]]
            label = f"{day['date']}: {day['contributionCount']} contribuciones"
            body += (f'<rect x="{x}" y="{y}" width="15" height="15" rx="4" fill="{fill}">'
                     f'<title>{escape(label)}</title></rect>')
    for row, label in [(1, "lun"), (3, "mié"), (5, "vie")]:
        body += text(32, 132 + row * 19, label, 11)
    body += '<rect class="scan" x="72" y="257" width="55" height="2" rx="1" fill="url(#accent)"/>'
    body += text(32, 293, "Constancia, curiosidad y código.", 13)
    body += text(923, 293, "Menos", 11)
    for level, fill in enumerate(colors.values()):
        body += f'<rect x="{967 + level * 20}" y="281" width="14" height="14" rx="3" fill="{fill}"/>'
    body += text(1073, 293, "Más", 11)
    return card(322, "Calendario de contribuciones de Dante Yupanqui", body)


def render_languages(profile):
    languages = Counter()
    colors = {}
    for repo in profile["repositories"]:
        language = repo.get("primaryLanguage")
        if language:
            languages[language["name"]] += 1
            colors[language["name"]] = language.get("color") or "#A78BFA"
    top = languages.most_common(7)
    if len(languages) > 7:
        top.append(("Otros", sum(languages.values()) - sum(count for _, count in top)))
        colors["Otros"] = "#64748B"
    body = text(32, 40, "Lenguajes que dan vida a mis repositorios", 24, "#F1F5F9", 700)
    body += text(32, 69, "Lenguaje principal por repositorio público propio · sin forks ni repositorios sin lenguaje", 14)
    if not top:
        body += text(32, 129, "Todavía no hay repositorios públicos con un lenguaje identificado.")
    else:
        x = 32
        total = sum(languages.values())
        for language, count in top:
            width = count / total * 1136
            body += f'<rect x="{x:.2f}" y="96" width="{width:.2f}" height="13" fill="{escape(colors[language])}"/>'
            x += width
        for index, (language, count) in enumerate(top):
            col, row = index % 4, index // 4
            x, y = 32 + col * 284, 144 + row * 37
            body += f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{escape(colors[language])}"/>'
            body += text(x + 20, y, f"{language} · {count}", 15, "#D7E2EE", 600)
    return card(218, "Distribución de repositorios por lenguaje principal", body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="Dante1128")
    parser.add_argument("--snapshot", type=Path, help="Render a saved response without network access")
    args = parser.parse_args()
    profile = (json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot
               else fetch_profile(args.username))
    validate_profile(profile)
    output = ROOT / "assets"
    # Render everything before replacing the last successful cards.
    files = {
        "github-stats.svg": render_stats(profile),
        "github-calendar.svg": render_calendar(profile),
        "github-languages.svg": render_languages(profile),
        "github-data.json": json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
    }
    for name, content in files.items():
        (output / name).write_text(content, encoding="utf-8")
    print(f"Updated {len(files)} profile assets for {profile['login']} ({profile['updated_on']} UTC)")


if __name__ == "__main__":
    main()
