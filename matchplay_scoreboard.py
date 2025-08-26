import requests
import csv
import json
import io
from collections import defaultdict
import configparser
import os
from datetime import datetime

BASE_URL = 'https://app.matchplay.events/api'


def load_config():
    """Load API token and tournament ID from config.ini or prompt to create it"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")

    if not os.path.exists(config_path):
        print(f"Config file not found at {config_path}.")
        create = input("Would you like to create one now? (y/n): ").strip().lower()
        if create == 'y':
            api_token = input("Enter your MatchPlay API token: ").strip()
            tournament_id = input("Enter your tournament ID: ").strip()
            with open(config_path, 'w') as f:
                f.write('[matchplay]\n')
                f.write(f'api_token = {api_token}\n')
                f.write(f'tournament_id = {tournament_id}\n')
            print(f"Config file created at {config_path}")
        else:
            raise ValueError("Config file is required. Exiting.")

    config.read(config_path)
    api_token = config.get("matchplay", "api_token", fallback="").strip()
    tournament_id = config.get("matchplay", "tournament_id", fallback="").strip()

    if not api_token or "YOUR_API_TOKEN_HERE" in api_token or not tournament_id or "YOUR_TOURNAMENT_ID_HERE" in tournament_id:
        raise ValueError("Missing or placeholder values in config.ini")

    return api_token, tournament_id


def fetch_csv(endpoint, filename, api_token):
    """Download CSV from MatchPlay endpoint and return parsed rows"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Authorization': f'Bearer {api_token}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        f.write(resp.text)
    print(f"✅ Saved {filename}")

    reader = csv.DictReader(io.StringIO(resp.text))
    return [{k.strip(): v.strip() for k, v in row.items()} for row in reader]


def get_standings(tournament_id, api_token):
    """Get standings JSON from MatchPlay API"""
    url = f"{BASE_URL}/tournaments/{tournament_id}/standings"
    headers = {'Authorization': f'Bearer {api_token}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def create_player_name_map(players):
    """Map Player ID to Player name"""
    return {str(p.get("Player id") or p.get("Player ID")).strip():
            (p.get("Player name") or p.get("Name", "")).strip()
            for p in players if (p.get("Player id") or p.get("Player ID"))}


def compute_stats(games):
    """Compute points and games played per player"""
    stats = defaultdict(lambda: {"points": 0.0, "gamesPlayed": 0})
    for g in games:
        pid = g.get("Player ID") or g.get("Player id")
        if not pid:
            continue
        try:
            points = float(g.get("Points") or 0)
        except ValueError:
            points = 0.0
        stats[str(pid)]["points"] += points
        stats[str(pid)]["gamesPlayed"] += 1
    return stats


def merge_data(players_map, standings, game_stats):
    """Merge player names, standings, and stats"""
    merged = []
    for pid, name in players_map.items():
        entry = {
            "playerId": pid,
            "playerName": name,
            "points": 0.0,
            "gamesPlayed": None,
            "position": None
        }
        if standings:
            s = next((x for x in standings if str(x.get("playerId")) == pid), None)
            if s:
                entry["points"] = float(s.get("points") or 0)
                entry["gamesPlayed"] = s.get("gamesPlayed")
                entry["position"] = s.get("position")

        if pid in game_stats:
            if entry["points"] == 0:
                entry["points"] = game_stats[pid]["points"]
            if entry["gamesPlayed"] is None:
                entry["gamesPlayed"] = game_stats[pid]["gamesPlayed"]

        merged.append(entry)

    return sorted(
        merged,
        key=lambda x: (x["position"] if x["position"] is not None else 9999,
                       -float(x["points"]),
                       -(x["gamesPlayed"] or 0))
    )


def create_html(data, tournament_id):
    """Generate HTML scoreboard"""
    html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{tournament_id}</title>
<style>
body {{font-family: Arial, sans-serif; background:#111; color:#fff; padding:20px;}}
.scoreboard {{max-width:600px; margin:auto;}}
.header, .row {{display:flex; justify-content:space-between; align-items:center; padding:10px; border-radius:10px; margin-bottom:8px;}}
.header {{background:#007bff; font-weight:bold; position:sticky; top:0;}}
.row {{background:#222; transition:transform 0.2s;}}
.row:hover {{transform:scale(1.02);}}
.position {{width:50px; text-align:center;}}
.player-name {{flex:1; text-align:left; padding:0 10px; font-weight:bold;}}
.games-played, .points {{width:60px; text-align:center;}}
.points {{color:#ffd700; font-weight:bold;}}
</style>
</head>
<body>
<div class='scoreboard'>
<div class='header'><div class='position'>Rank</div><div class='player-name'>Player</div><div class='games-played'>Games</div><div class='points'>Points</div></div>
"""
    for p in data:
        html += f"<div class='row'><div class='position'>{p.get('position','-')}</div><div class='player-name'>{p.get('playerName','')}</div><div class='games-played'>{p.get('gamesPlayed','-')}</div><div class='points'>{p.get('points',0):.1f}</div></div>"
    html += "</div></body></html>"

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{tournament_id}.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"🎨 HTML scoreboard generated: {filepath}")


if __name__ == "__main__":
    try:
        API_TOKEN, TOURNAMENT_ID = load_config()
        players = fetch_csv(f"tournaments/{TOURNAMENT_ID}/players/csv", f"tournament_{TOURNAMENT_ID}_players.csv", API_TOKEN)
        games = fetch_csv(f"tournaments/{TOURNAMENT_ID}/games/csv", f"tournament_{TOURNAMENT_ID}_games.csv", API_TOKEN)
        standings = get_standings(TOURNAMENT_ID, API_TOKEN)

        player_map = create_player_name_map(players)
        game_stats = compute_stats(games)
        combined = merge_data(player_map, standings, game_stats)

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"tournament_{TOURNAMENT_ID}_final.json")
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(combined, jf, indent=4)
        print(f"💾 Saved JSON: {json_path}")

        create_html(combined, TOURNAMENT_ID)

    except Exception as e:
        print(f"Error: {e}")
