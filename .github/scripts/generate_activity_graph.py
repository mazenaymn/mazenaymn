#!/usr/bin/env python3

from __future__ import annotations

import datetime as dt
import json
import math
import os
import pathlib
import sys
import urllib.error
import urllib.request


WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST_DIR = WORKSPACE_ROOT / "dist"
OUTPUT_FILE = DIST_DIR / "contribution-graph.svg"
GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "mazenaymn")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("SNK_GITHUB_TOKEN")


def iso_utc(moment: dt.datetime) -> str:
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def graphql_request(query: str, variables: dict[str, str]) -> dict:
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN or SNK_GITHUB_TOKEN is required to generate the activity graph")

    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "mazenaymn-profile-graph",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        error_body = ""
        try:
            error_body = error.read().decode("utf-8")
        except Exception:
            error_body = ""
        if error.code == 401:
            raise RuntimeError(
                "GitHub API request failed with status 401 (unauthorized). "
                "Check that SNK_GITHUB_TOKEN is a valid personal access token and not expired."
            ) from error
        raise RuntimeError(f"GitHub API request failed with status {error.code}: {error_body}") from error

    data = json.loads(body)
    if data.get("errors"):
        messages = "; ".join(item.get("message", "unknown error") for item in data["errors"])
        raise RuntimeError(f"GitHub API returned errors: {messages}")

    return data["data"]


def fetch_contribution_days() -> list[dict[str, object]]:
    today = dt.datetime.now(dt.timezone.utc).date()
    from_date = dt.datetime.combine(today - dt.timedelta(days=30), dt.time.min, tzinfo=dt.timezone.utc)
    to_date = dt.datetime.combine(today + dt.timedelta(days=1), dt.time.min, tzinfo=dt.timezone.utc)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    data = graphql_request(
        query,
        {"login": USERNAME, "from": iso_utc(from_date), "to": iso_utc(to_date)},
    )
    user = data.get("user")
    if not user:
        raise RuntimeError(f"Could not load GitHub user data for '{USERNAME}'")

    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]

    days: list[dict[str, object]] = []
    for week in weeks:
        days.extend(week["contributionDays"])

    return days[-31:]


def color_for_value(value: int, maximum: int) -> str:
    if value <= 0:
        return "#26324a"
    if maximum <= 1:
        return "#7aa2f7"

    scale = value / maximum
    if scale < 0.25:
        return "#7aa2f7"
    if scale < 0.5:
        return "#5b8def"
    if scale < 0.75:
        return "#3f7ae0"
    return "#2f6fda"


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_svg(days: list[dict[str, object]]) -> str:
    max_value = max((int(day["contributionCount"]) for day in days), default=0)
    max_value = max(max_value, 1)

    width = 1200
    height = 360
    chart_left = 90
    chart_top = 110
    chart_width = 1020
    chart_height = 170
    bar_gap = 6
    bar_width = math.floor((chart_width - bar_gap * (len(days) - 1)) / len(days)) if days else 0
    bar_width = max(bar_width, 12)

    grid_lines = []
    for tick in range(0, max_value + 1):
        y = chart_top + chart_height - (tick / max_value) * chart_height
        grid_lines.append(
            f'<line x1="{chart_left}" y1="{y:.1f}" x2="{chart_left + chart_width}" y2="{y:.1f}" stroke="#263247" stroke-width="1" stroke-dasharray="4 4" opacity="0.8" />'
        )
        grid_lines.append(
            f'<text x="{chart_left - 12}" y="{y + 4:.1f}" text-anchor="end" fill="#8ea0c8" font-size="12">{tick}</text>'
        )

    bars = []
    labels = []
    for index, day in enumerate(days):
        count = int(day["contributionCount"])
        x = chart_left + index * (bar_width + bar_gap)
        bar_height = 0 if max_value == 0 else round((count / max_value) * chart_height)
        y = chart_top + chart_height - bar_height
        color = color_for_value(count, max_value)
        date_text = str(day["date"])
        short_label = date_text[8:10].lstrip("0") or "0"

        bars.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="6" fill="{color}" />'
        )
        labels.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{chart_top + chart_height + 24}" text-anchor="middle" fill="#8ea0c8" font-size="11">{short_label}</text>'
        )

    total = sum(int(day["contributionCount"]) for day in days)
    active_days = sum(1 for day in days if int(day["contributionCount"]) > 0)

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\" fill=\"none\" role=\"img\" aria-label=\"Contribution graph\">
  <defs>
    <linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0%\" stop-color=\"#0b1120\" />
      <stop offset=\"100%\" stop-color=\"#111827\" />
    </linearGradient>
    <linearGradient id=\"accent\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\">
      <stop offset=\"0%\" stop-color=\"#7aa2f7\" />
      <stop offset=\"100%\" stop-color=\"#8b5cf6\" />
    </linearGradient>
    <filter id=\"shadow\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"140%\">
      <feDropShadow dx=\"0\" dy=\"16\" stdDeviation=\"18\" flood-color=\"#02040a\" flood-opacity=\"0.45\" />
    </filter>
  </defs>

  <rect width=\"100%\" height=\"100%\" rx=\"24\" fill=\"url(#bg)\" />
  <g filter=\"url(#shadow)\">
    <rect x=\"32\" y=\"28\" width=\"1136\" height=\"304\" rx=\"20\" fill=\"#151a2a\" stroke=\"#24304a\" />
  </g>

  <text x=\"60\" y=\"70\" fill=\"#e8eefc\" font-size=\"24\" font-family=\"Segoe UI, Arial, sans-serif\" font-weight=\"700\">{escape(USERNAME)}'s Contribution Graph</text>
  <rect x=\"60\" y=\"86\" width=\"160\" height=\"4\" rx=\"2\" fill=\"url(#accent)\" />

  <text x=\"1060\" y=\"70\" text-anchor=\"end\" fill=\"#8ea0c8\" font-size=\"13\" font-family=\"Segoe UI, Arial, sans-serif\">Last 31 days</text>
  <text x=\"1060\" y=\"92\" text-anchor=\"end\" fill=\"#e8eefc\" font-size=\"14\" font-family=\"Segoe UI, Arial, sans-serif\">{total} contributions</text>
  <text x=\"1060\" y=\"112\" text-anchor=\"end\" fill=\"#8ea0c8\" font-size=\"13\" font-family=\"Segoe UI, Arial, sans-serif\">{active_days} active days</text>

  <text x=\"28\" y=\"198\" transform=\"rotate(-90 28 198)\" fill=\"#8ea0c8\" font-size=\"13\" font-family=\"Segoe UI, Arial, sans-serif\">Contributions</text>
  <text x=\"606\" y=\"332\" text-anchor=\"middle\" fill=\"#8ea0c8\" font-size=\"13\" font-family=\"Segoe UI, Arial, sans-serif\">Days</text>

  {"".join(grid_lines)}
  {"".join(bars)}
  {"".join(labels)}
</svg>
"""


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    days = fetch_contribution_days()
    svg = render_svg(days)
    OUTPUT_FILE.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())