#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "pyyaml"]
# ///
"""Convert 3x-ui base64 subscription to Clash YAML profile."""

import base64
import sys
from urllib.parse import parse_qs, unquote, urlparse

import requests
import yaml


def fetch_sub(url: str) -> str:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text.strip()


def decode_sub(raw: str) -> list[str]:
    try:
        decoded = base64.b64decode(raw + "==").decode()
        return [line for line in decoded.splitlines() if line.strip()]
    except Exception:
        return [line for line in raw.splitlines() if line.strip()]


def parse_vless(uri: str) -> dict | None:
    parsed = urlparse(uri)
    if parsed.scheme != "vless":
        return None

    params = parse_qs(parsed.query)
    p = {k: v[0] for k, v in params.items()}

    name = unquote(parsed.fragment) if parsed.fragment else f"vless-{parsed.hostname}"
    security = p.get("security", "none")

    proxy: dict = {
        "name": name,
        "type": "vless",
        "server": parsed.hostname,
        "port": parsed.port,
        "uuid": parsed.username,
        "udp": True,
        "network": p.get("type", "tcp"),
    }

    flow = p.get("flow", "")
    if flow:
        proxy["flow"] = flow

    if security == "reality":
        proxy["tls"] = True
        proxy["servername"] = p.get("sni", "")
        proxy["reality-opts"] = {
            "public-key": p.get("pbk", ""),
            "short-id": p.get("sid", ""),
        }
        if fp := p.get("fp"):
            proxy["client-fingerprint"] = fp
    elif security == "tls":
        proxy["tls"] = True
        proxy["servername"] = p.get("sni", "")
        if fp := p.get("fp"):
            proxy["client-fingerprint"] = fp

    if proxy["network"] == "ws":
        proxy["ws-opts"] = {
            "path": p.get("path", "/"),
            "headers": {"Host": p.get("host", proxy["server"])},
        }
    elif proxy["network"] == "grpc":
        proxy["grpc-opts"] = {"grpc-service-name": p.get("serviceName", "")}

    return proxy


RULES: list[str] = [
    # ads
    "GEOSITE,category-ads-all,REJECT",
    # private
    "GEOIP,private,DIRECT,no-resolve",
    "GEOSITE,private,DIRECT",
    # direct domains
    "DOMAIN-SUFFIX,discord.com,DIRECT",
    "DOMAIN-SUFFIX,discordapp.com,DIRECT",
    "DOMAIN-SUFFIX,discord.gg,DIRECT",
    "DOMAIN-SUFFIX,discord.media,DIRECT",
    "DOMAIN-SUFFIX,discordcdn.com,DIRECT",
    "DOMAIN-SUFFIX,discord.co,DIRECT",
    "DOMAIN-SUFFIX,telegram.org,DIRECT",
    "DOMAIN-SUFFIX,telegram.me,DIRECT",
    "DOMAIN-SUFFIX,t.me,DIRECT",
    "DOMAIN-SUFFIX,telesco.pe,DIRECT",
    "DOMAIN-SUFFIX,tdesktop.com,DIRECT",
    "DOMAIN-SUFFIX,telegra.ph,DIRECT",
    "DOMAIN-SUFFIX,youtube.com,DIRECT",
    "DOMAIN-SUFFIX,googlevideo.com,DIRECT",
    "DOMAIN-SUFFIX,ytimg.com,DIRECT",
    "DOMAIN-SUFFIX,youtu.be,DIRECT",
    "DOMAIN-SUFFIX,ggpht.com,DIRECT",
    "DOMAIN-SUFFIX,steampowered.com,DIRECT",
    "DOMAIN-SUFFIX,steamcommunity.com,DIRECT",
    "DOMAIN-SUFFIX,steamstatic.com,DIRECT",
    "DOMAIN-SUFFIX,steamgames.com,DIRECT",
    "DOMAIN-SUFFIX,steam-chat.com,DIRECT",
    "DOMAIN-SUFFIX,steamusercontent.com,DIRECT",
    # torrents
    "PROCESS-NAME,qbittorrent,DIRECT",
    # catch-all
    "MATCH,Proxy",
]


def build_clash(proxies: list[dict]) -> dict:
    names = [p["name"] for p in proxies]
    return {
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "ipv6": False,
        "dns": {
            "enable": True,
            "ipv6": False,
            "nameserver": ["8.8.8.8", "1.1.1.1"],
        },
        "proxies": proxies,
        "proxy-groups": [
            {"name": "Proxy", "type": "select", "proxies": names + ["DIRECT"]},
            {
                "name": "Auto",
                "type": "url-test",
                "proxies": names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300,
            },
        ],
        "rules": RULES,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <sub-url> [output.yaml]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    raw = fetch_sub(url)
    uris = decode_sub(raw)

    proxies = []
    for uri in uris:
        proxy = parse_vless(uri)
        if proxy:
            proxies.append(proxy)
        else:
            print(f"skipped: {uri[:60]}", file=sys.stderr)

    if not proxies:
        print("no valid proxies found", file=sys.stderr)
        sys.exit(1)

    config = build_clash(proxies)
    output = yaml.dump(config, allow_unicode=True, sort_keys=False)

    if out:
        with open(out, "w") as f:
            f.write(output)
        print(f"written to {out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
