#!/usr/bin/env python3
"""
wow-refresh/reload.py — Send live reload commands to AzerothCore via SOAP.

Usage:
  python reload.py npc_vendor          # reload vendor lists (no restart needed)
  python reload.py item_template       # reload item prices/stats
  python reload.py creature_template   # reload NPC stats/flags
  python reload.py all                 # reload every mapped table
  python reload.py ".reload spell_dbc" # send a raw command directly
"""

import sys
import json
import re
import base64
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def soap_command(cfg, command):
    """Send a single GM command to worldserver via SOAP. Returns response text."""
    host = cfg["soap"]["host"]
    port = cfg["soap"]["port"]
    user = cfg["soap"]["username"]
    pw   = cfg["soap"]["password"]

    url = f"http://{host}:{port}/"
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:ns1="urn:AC">'
        "<SOAP-ENV:Body>"
        "<ns1:executeCommand>"
        f"<command>{command}</command>"
        "</ns1:executeCommand>"
        "</SOAP-ENV:Body>"
        "</SOAP-ENV:Envelope>"
    )

    credentials = base64.b64encode(f"{user}:{pw}".encode()).decode()
    req = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers={
            "Content-Type": "text/xml;charset=UTF-8",
            "SOAPAction": "urn:AC/executeCommand",
            "Authorization": f"Basic {credentials}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"SOAP HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Cannot reach worldserver at {url}\n"
            f"Make sure SOAP is enabled in worldserver.conf:\n"
            f"  SOAP.Enabled = 1\n"
            f"  SOAP.IP = 127.0.0.1\n"
            f"  SOAP.Port = 7878\n"
            f"Reason: {e.reason}"
        ) from e


def extract_result(soap_response):
    match = re.search(r"<result>(.*?)</result>", soap_response, re.DOTALL)
    if match:
        return match.group(1).strip() or "OK"
    return "OK (no result body)"


def do_reload(cfg, target):
    reload_map = cfg.get("reload_map", {})

    if target.startswith("."):
        # Raw command
        print(f"-> {target}")
        print(f"   {extract_result(soap_command(cfg, target))}")
        return True

    if target == "all":
        tables = list(reload_map.keys())
    elif target in reload_map:
        tables = [target]
    else:
        print(f"Unknown table '{target}'. Known tables:")
        for k in reload_map:
            print(f"  {k}")
        return False

    for tbl in tables:
        cmd = reload_map[tbl]
        print(f"-> {cmd}")
        print(f"   {extract_result(soap_command(cfg, cmd))}")

    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cfg = load_config()
    try:
        success = do_reload(cfg, sys.argv[1])
        sys.exit(0 if success else 1)
    except RuntimeError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
