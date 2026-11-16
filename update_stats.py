#!/usr/bin/env python3
"""Генерирует stats.svg с актуальной статистикой из GitHub API.

Работает локально (python3 update_stats.py) и в GitHub Actions
(там автоматически передаётся GITHUB_TOKEN). Результат — stats.svg
в текущей папке.
"""
import base64
import datetime
import json
import os
import urllib.request

USER = "ryzhenkahvh"          # логин GitHub
DISPLAY = "jxpix"             # отображаемое имя в заголовке карточки
API = "https://api.github.com"


def api(path, accept="application/vnd.github+json"):
    headers = {
        "Accept": accept,
        "User-Agent": USER,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fmt(n):
    """1234 -> '1.2k' (как в github-readme-stats)."""
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100")
prs = api(f"/search/issues?q=author:{USER}+type:pr")
issues = api(f"/search/issues?q=author:{USER}+type:issue")
commits = api(f"/search/commits?q=author:{USER}")

stars = sum(r.get("stargazers_count", 0) for r in repos)
created = datetime.datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")

avatar_url = user["avatar_url"] + ("&" if "?" in user["avatar_url"] else "?") + "s=200"
req = urllib.request.Request(avatar_url, headers={"User-Agent": USER})
with urllib.request.urlopen(req, timeout=30) as r:
    avatar_b64 = base64.b64encode(r.read()).decode()

values = {
    "{{display}}": DISPLAY,
    "{{stars}}": fmt(stars),
    "{{commits}}": fmt(commits["total_count"]),
    "{{prs}}": fmt(prs["total_count"]),
    "{{issues}}": fmt(issues["total_count"]),
    "{{repos}}": fmt(user["public_repos"]),
    "{{followers_line}}": f'{user["followers"]} followers · {user["following"]} following',
    "{{joined_line}}": created.strftime("joined %b %Y"),
    "{{date_line}}": "updated " + datetime.date.today().strftime("%d.%m.%Y"),
    "{{avatar}}": avatar_b64,
}

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="195" viewBox="0 0 450 195" role="img" aria-label="GitHub statistics for {{display}} (__USER__)">
  <title>{{display}}'s GitHub Stats</title>
  <defs>
    <style>
      text { font-family: "Segoe UI", "Ubuntu", "Helvetica Neue", Arial, sans-serif; }
      .title { font-size: 18px; font-weight: 600; fill: #fe428e; }
      .chip  { font-size: 10px; fill: #a9fef7; opacity: .55; }
      .label { font-size: 13.5px; fill: #a9fef7; }
      .value { font-size: 13.5px; font-weight: 700; fill: #a9fef7; }
      .meta  { font-size: 11px; fill: #a9fef7; }
      .foot  { font-size: 8.5px; fill: #a9fef7; opacity: .5; }
      .icon  { stroke: #f8d847; fill: none; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
      .gold  { fill: #f8d847; }
    </style>
    <clipPath id="avatarClip"><circle cx="375" cy="93" r="39"/></clipPath>
  </defs>

  <rect x="0.75" y="0.75" width="448.5" height="193.5" rx="6" fill="#141321" stroke="#fe428e" stroke-opacity="0.35" stroke-width="1.5"/>

  <text class="title" x="25" y="37">{{display}}'s GitHub Stats</text>
  <text class="chip" x="425" y="37" text-anchor="end">self-hosted · theme radical</text>

  <line x1="300" y1="58" x2="300" y2="166" stroke="#a9fef7" stroke-opacity="0.15" stroke-width="1"/>

  <g transform="translate(30,61)">
    <path class="gold" d="M8 1.2l1.95 3.95 4.35.63-3.15 3.07.74 4.33L8 11.15l-3.89 2.05.74-4.33L1.7 5.78l4.35-.63z"/>
  </g>
  <text class="label" x="58" y="75">Total Stars:</text>
  <text class="value" x="282" y="75" text-anchor="end">{{stars}}</text>

  <g transform="translate(30,85)">
    <circle class="icon" cx="8" cy="8" r="2.6"/>
    <line class="icon" x1="0.5" y1="8" x2="5.4" y2="8"/>
    <line class="icon" x1="10.6" y1="8" x2="15.5" y2="8"/>
  </g>
  <text class="label" x="58" y="99">Total Commits:</text>
  <text class="value" x="282" y="99" text-anchor="end">{{commits}}</text>

  <g transform="translate(30,109)">
    <g class="icon">
      <circle cx="3.5" cy="3.5" r="2"/>
      <circle cx="3.5" cy="12.5" r="2"/>
      <path d="M3.5 5.5v5"/>
      <path d="M9.5 3.5h2.3a1.5 1.5 0 0 1 1.5 1.5v5.3"/>
      <path d="M11.3 11l2 2 2-2"/>
    </g>
  </g>
  <text class="label" x="58" y="123">Total PRs:</text>
  <text class="value" x="282" y="123" text-anchor="end">{{prs}}</text>

  <g transform="translate(30,133)">
    <circle class="icon" cx="8" cy="8" r="6.2"/>
    <circle class="gold" cx="8" cy="8" r="1.9"/>
  </g>
  <text class="label" x="58" y="147">Total Issues:</text>
  <text class="value" x="282" y="147" text-anchor="end">{{issues}}</text>

  <g transform="translate(30,157)">
    <g class="icon">
      <rect x="1.8" y="1.8" width="12.4" height="12.4" rx="1.6"/>
      <line x1="8" y1="1.8" x2="8" y2="14.2"/>
    </g>
  </g>
  <text class="label" x="58" y="171">Public Repos:</text>
  <text class="value" x="282" y="171" text-anchor="end">{{repos}}</text>

  <image href="data:image/png;base64,{{avatar}}" x="336" y="54" width="78" height="78" clip-path="url(#avatarClip)" preserveAspectRatio="xMidYMid slice"/>
  <circle cx="375" cy="93" r="39.75" fill="none" stroke="#fe428e" stroke-width="1.6" stroke-opacity="0.9"/>
  <text class="meta" x="375" y="152" text-anchor="middle">{{followers_line}}</text>
  <text class="meta" x="375" y="168" text-anchor="middle" opacity="0.65">{{joined_line}}</text>
  <text class="foot" x="425" y="188" text-anchor="end">{{date_line}}</text>
</svg>
'''

svg = svg.replace("__USER__", USER)
for key, val in values.items():
    svg = svg.replace(key, val)

with open("stats.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"stats.svg готов: {stars=} {prs['total_count']=} {commits['total_count']=} "
      f"{issues['total_count']=} {user['public_repos']=}")
