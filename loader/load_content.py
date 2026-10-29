#!/usr/bin/env python3
"""
FinKids content loader — parses markdown content files and seeds the DB via
the admin bulk-upsert endpoints.

Usage:
    python load_content.py --be-url http://localhost:8080 --token <admin-jwt>
    python load_content.py --dry-run          # parse + validate only, no HTTP calls
"""
import argparse
import json
import sys
from pathlib import Path

import requests

from parsers.goal_parser import parse_goal_directory
from parsers.lesson_parser import parse_learning_directory
from parsers.map_parser import load_goal_to_lesson_map
from validators.schema import validate_all

CONTENT_ROOT = Path(__file__).resolve().parent.parent


def parse_args():
    p = argparse.ArgumentParser(description="FinKids content loader")
    p.add_argument("--be-url", default="http://localhost:8080",
                   help="Backend base URL (no trailing slash)")
    p.add_argument("--token", default=None,
                   help="Admin JWT token (required unless --dry-run)")
    p.add_argument("--dry-run", action="store_true",
                   help="Parse and validate only — no HTTP calls")
    return p.parse_args()


def post(url: str, payload: dict, token: str):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    args = parse_args()

    if not args.dry_run and not args.token:
        print("ERROR: --token is required unless --dry-run is set.", file=sys.stderr)
        sys.exit(1)

    print("Parsing content …")
    module_map = load_goal_to_lesson_map(CONTENT_ROOT)
    goals_dir = CONTENT_ROOT / "goals-habits"
    learning_dir = CONTENT_ROOT / "learning"

    goals = parse_goal_directory(goals_dir, module_map)
    levels = parse_learning_directory(learning_dir)

    print(f"  Parsed {len(goals)} goal templates, "
          f"{sum(len(c['lessons']) for lv in levels for c in lv['chapters'])} lessons\n")

    if not validate_all(goals, levels):
        print("\nValidation failed — fix errors before loading.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[dry-run] Validation passed. No data sent to backend.")
        sys.exit(0)

    base = args.be_url.rstrip("/")

    print("\nLoading goal templates …")
    result = post(
        f"{base}/admin/content/goal-templates/bulk-upsert",
        {"templates": goals},
        args.token,
    )
    print(f"  ✓ {result['data']['processed']} goal templates upserted")

    print("Loading lessons …")
    result = post(
        f"{base}/admin/content/lessons/bulk-upsert",
        {"levels": levels},
        args.token,
    )
    print(f"  ✓ {result['data']['processed']} lessons upserted")

    print("\nContent load complete.")


if __name__ == "__main__":
    main()
